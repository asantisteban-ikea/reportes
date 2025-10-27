import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def main():
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
    df_sku = load_worksheet_data("HFB")
    df_sku["SKU"] = df_sku["SKU"].astype(str).str.zfill(8)
    df_usuarioswh = load_worksheet_data("USUARIO WH")
    recuperaciones_ws = sh.worksheet("WAREHOUSE")

    # === INTERFAZ ===
    fecha = st.date_input("📅 Fecha de la recuperación", value=None)

    proceso_auditoria = st.selectbox(
        "Indica el proceso de auditoria",
        ["Auditoria DO ECOM",
        "Auditoria DESTR",
        "Auditoria Tienda",
        "Auditoria INV",
        "Auditoria AS-IS",
        "Plan Enfermero"],
        placeholder="Auditoria",
        index=None
    )

    if fecha:
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

    novedad = st.selectbox(
        "¿Que novedad se presentó?",
        [
            "SOBRANTE",
            "AVERIA",
            "FALTANTE",
            "IMPRESO",
            "TROQUE",
            "SIN SKU",
            "OLPN EN  MAL ESTADO",
            "RECUPERACION",
            "OLPN SIN AUDITAR",
            "OLPN  EN ESTADO ENVIADO",
            "ETIQUETA",
            "OLPN RE IMPRESO Y TROCADO"
        ],
        placeholder="Selecciona una de las opciones",
        accept_new_options=True,
        index=None
    )

    tipo_documento = st.radio(
        "Indica el tipo de documento",
        ["OLPN", "ILPN"],
        placeholder="Selecciona",
        value=None
    )

    numero_documento = st.text_input("💻 Número de documento")  

    lista_sku = st.selectbox(
        "📦 SKU", 
        df_sku["SKU"].dropna().tolist(),
        placeholder= "Ingresa el SKU del producto",
        index=None
        )

    if lista_sku:
        producto = df_sku.loc[df_sku["SKU"] == lista_sku, "ITEM"].iloc[0]
        familia = df_sku.loc[df_sku["SKU"] == lista_sku, "FAMILIA"].iloc[0]
        st.info(f"🛒 Producto: **{producto}**, Familia: **{familia}**")
    else:
        st.warning("⚠️ Debes seleccionar uno de los SKU de las opciones")

    auditor = st.selectbox(
        "👮 Nombre de auditor",
        [
            "Felipe Gutierrez",
            "Yulieth Parada",
            "Jessica Camacho",
            "Linda Sandoval",
            "Jhon Ballesteros",
            "Angel Mendez",
            "Laura Alvarez"
        ],
        placeholder="Auditor",
        accept_new_options=True,
        index=None
    )

    opciones_usuarios = [
        f"{row['NOMBRE']} ({row['USUARIO']})"
        for _, row in df_usuarioswh.iterrows()
    ]

    lista_usuarioswh = st.selectbox(
        "📦 Usuario WH", 
        opciones_usuarios,
        placeholder= "Ingresa el usuario que reporta",
        index=None
        )

    if lista_usuarioswh:
        usuario = lista_usuarioswh.split("(")[-1].replace(")", "").strip()
        worker = df_usuarioswh.loc[df_usuarioswh["USUARIO"] == usuario].iloc[0]
        st.success(f"Seleccionaste a **{worker['NOMBRE']}** (picker: {worker['USUARIO']})")

        picker = worker['NOMBRE']
        documento_usuario = worker['USUARIO']
        st.write(picker, documento_usuario)

    observaciones = st.text_area("📝 Descripción de la novedad")

    tipo_novedad = st.selectbox(
        "🏬 Tipo de Novedad", 
        ["Print",
        "Faltante",
        "Sobrantes",
        "Etiqueta Mal ubicada",
        "Averia Productos",
        "Reimpreso",
        "Troque",
        "Sin auditar",
        "Recuperación",
        "Producto de Asis"],
        horizontal=False,
        index=None
    )

    area = st.radio(
        "📍 Área",
        ["CP",
        "INVENTARIOS",
        "MEZANINE",
        "NQS",
        "CALI",
        "MEDELLIN",
        "RECOVERY"],
        horizontal=False,
        index=None
    )

    cantidad = st.number_input("📊 Unidades", min_value=1, value=1)
    costo = st.number_input("💰 Valor unitario", min_value=0, value=0)
    total = cantidad * costo
    st.write(f"**Total:** ${total:,.0f}")

    numero_semana = fecha.isocalendar()[1]


    if st.button("📤 Registrar"):
        # Validar campos obligatorios
        if not numero_documento or not cantidad or not pvp:
            st.error("⚠️ Debes completar los campos obligatorios antes de registrar.")
        else:
            # Ajuste de hora a Colombia (UTC-5)
            hora_local = datetime.now(ZoneInfo("America/Bogota"))
            fecha_registro = (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")

            nueva_fila = [
                str(fecha), proceso_auditoria, novedad,
                tipo_documento,numero_documento, lista_sku,
                auditor, picker, documento_usuario,
                observaciones, tipo_novedad, area,
                cantidad, costo, total, numero_semana
            ]

            recuperaciones_ws.append_row(nueva_fila)
            st.success("✅ Información registrada correctamente.")

