import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
    
def run():
    # === CONFIGURACIÓN ===
    st.title("🧾 Formato para reporte de Recuperaciones")
    
    # === CREDENCIALES ===
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"]["credentials"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    
    gc = gspread.authorize(credentials)
    spreadsheet_id = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = gc.open_by_key(spreadsheet_id)
    
    # === CARGA DE DATOS CON CACHE (TTL = 7 días) ===
    @st.cache_data(ttl=7*24*60*60)  # 7 días en segundos
    def load_worksheet_data(sheet_name):
        ws = sh.worksheet(sheet_name)
        return pd.DataFrame(ws.get_all_records())
    
    # === CARGA DE HOJAS ===
    df_vigilantes = load_worksheet_data("VIGILANTES")
    df_sku = load_worksheet_data("HFB")
    df_sku["SKU"] = df_sku["SKU"].astype(str).str.zfill(8)
    recuperaciones_ws = sh.worksheet("RECUPERACIONES")
    
    # === INTERFAZ ===
    lista_tiendas = st.selectbox(
        "Elige una de las tiendas",
        ["IKEA NQS", "IKEA MALLPLAZA CALI", "IKEA ENVIGADO"],
        placeholder="Selecciona una tienda",
        index=None
    )
    
    if lista_tiendas:
        match lista_tiendas:
            case "IKEA NQS":
                id_tienda = 1
            case "IKEA MALLPLAZA CALI":
                id_tienda = 2
            case "IKEA ENVIGADO":
                id_tienda = 3
    
        fecha = st.date_input("📅 Fecha de la recuperación", value=None)
        hora = st.time_input("🕒 Hora de la recuperación", value=None)
    
        if fecha and hora:
            horas = hora.hour
            rango_horas = f"{horas} - {horas+1}"
            mes = fecha.month
            dia = fecha.weekday()
            
            match mes:
                case 1:
                    mes = "Enero"
                case 2:
                    mes = "Febrero"
                case 3:
                    mes = "Marzo"
                case 4:
                    mes = "Abril"
                case 5:
                    mes = "Mayo"
                case 6:
                    mes = "Junio"
                case 7:
                    mes = "Julio"
                case 8:
                    mes = "Agosto"
                case 9:
                    mes = "Septiembre"
                case 10:
                    mes = "Octubre"
                case 11:
                    mes = "Noviembre"
                case 12:
                    mes = "Diciembre"
                        
            match dia:
                case 0:
                    dia = "Lunes"
                case 1:
                    dia = "Martes"
                case 2:
                    dia = "Miercoles"
                case 3:
                    dia = "Jueves"
                case 4:
                    dia = "Viernes"
                case 5:
                    dia = "Sabado"
                case 6:
                    dia = "Domingo"
    
        vigilantes_df = df_vigilantes[df_vigilantes["ID_TIENDA"] == id_tienda]
        lista_vigilantes = st.selectbox(
            "👮 Nombre del vigilante",
            vigilantes_df["NOMBRE VIGILANTE"].dropna().tolist(),
            placeholder = "Indica el nombre del vigilante",
            index=None
        )
    
        pisos = st.radio(
            "🏬 Piso", 
            ["Piso 1", "Piso 2", "Piso 3", "Pecera/Sótano"],
            horizontal=True,
            index=None
        )
    
        ubicacion = st.radio(
            "📍 Ubicación",
            ["Antenas", "Autopago", "Auditoria", "Cajas Asistidas", "Check Out", "Solicitud"],
            horizontal=True,
            index=None
        )
        # === ÁREA QUE SOLICITA ===
        if ubicacion == "Solicitud":
            st.session_state["area"] = st.radio(
                "🗂️ Área que solicita",
                ["CX", "Recovery", "Olvido Cliente", "Fulfillment", "BNO", "S&S", "Sales", "Duty Manager"],
                horizontal=True,
                index=None
            )
        else:
            area = "No aplica"

    
        nombre_cw = st.text_input("👤 Nombre del Coworker")
        pos_cw = st.text_input("💻 Número de POS")
        if pos_cw:
            try:
                pos_cw = int(pos_cw)
            except Exception as e:
                st.warning(f"⚠️ Solo debes ingresar el número de la POS")   
    
        lista_sku = st.selectbox(
            "📦 SKU", 
            df_sku["SKU"].dropna().tolist(),
            placeholder= "Ingresa el SKU del producto",
            accept_new_options=True,
            index=None)
    
        if lista_sku:
            producto = df_sku.loc[df_sku["SKU"] == lista_sku, "ITEM"].iloc[0]
            familia = df_sku.loc[df_sku["SKU"] == lista_sku, "FAMILIA"].iloc[0]
            st.info(f"🛒 Producto: **{producto}**, Familia: **{familia}**")
            if len(lista_sku) != 8:
                st.warning("👉 Verifica la cantidad de digitos que tiene este nuevo codigo")
        else:
            st.warning("⚠️ Debes seleccionar uno de los SKU de las opciones")
    
        cantidad = st.number_input("📊 Cantidad", min_value=1, value=1)
        pvp = st.number_input("💰 Valor unitario", min_value=0, value=0)
        total = cantidad * pvp
        st.write(f"**Total:** ${total:,.0f}")
    
        descripcion = st.text_area("📝 Descripción del caso")
    
    
        if st.button("📤 Registrar"):
            # Validar campos obligatorios
            if not lista_tiendas or not lista_sku or not cantidad or not pvp:
                st.error("⚠️ Debes completar los campos obligatorios antes de registrar.")
            else:
                # Ajuste de hora a Colombia (UTC-5)
                hora_local = datetime.now(ZoneInfo("America/Bogota"))
                fecha_registro = (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    
                nueva_fila = [
                    hora_local.strftime("%Y-%m-%d %H:%M:%S"),
                    lista_tiendas, str(fecha), str(hora),
                    lista_vigilantes, pisos, ubicacion, area,
                    nombre_cw, pos_cw, lista_sku, familia, 
                    producto, cantidad, pvp, total, descripcion,
                    mes, dia, rango_horas
                ]
    
                recuperaciones_ws.append_row(nueva_fila)
                st.success("✅ Información registrada correctamente.")