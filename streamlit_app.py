import streamlit as st
import importlib

st.set_page_config(
    page_title="Sistema CCTV",
    page_icon="🎥",
    layout="centered"
)

# === SIDEBAR ===
st.sidebar.title("📂 Navegación")
main_page = st.sidebar.radio(
    "Selecciona un módulo:",
    ["🏠 Inicio", "📋 Registro", "🔍 Consulta", "📊 Reportes", "⚙️ Configuración"]
)

# === FUNCIÓN PARA CARGAR SUBPÁGINAS ===
def cargar_pagina(nombre_modulo):
    try:
        modulo = importlib.import_module(nombre_modulo)
        if hasattr(modulo, "run"):
            modulo.run()  # ejecuta función run() del módulo
        else:
            st.warning(f"⚠️ El módulo `{nombre_modulo}` no tiene una función run().")
    except ModuleNotFoundError:
        st.error(f"❌ No se encontró el módulo `{nombre_modulo}`.")
    except Exception as e:
        st.error(f"⚠️ Error al cargar la página: {e}")

# === INICIO ===
if main_page == "🏠 Inicio":
    st.title("🎥 Sistema de Control CCTV")
    st.markdown("---")
    st.header("🧭 Cómo navegar")
    st.markdown("""
    Usa el menú lateral para acceder a los diferentes módulos:
    - 📝 **Registro:** Diligencia los formatos de recuperaciones y casos detectados.
    - 🔍 **Consulta:** Visualiza los registros ya enviados y busca por SKU, fecha o responsable.
    - 📊 **Reportes:** Analiza la información consolidada mediante indicadores.
    - ⚙️ **Configuración:** Administra listas de SKU, usuarios o parámetros del sistema.
    """)

# === REGISTRO ===
elif main_page == "📋 Registro":
    st.title("📋 Registro de actividades")
    st.write("Selecciona el formulario que deseas abrir:")

    col1, col2, col3 = st.columns(3)

    if "subpage" not in st.session_state:
        st.session_state["subpage"] = None

    with col1:
        if st.button("🧾 Recuperaciones CCTV"):
            st.session_state["subpage"] = "pages.1_recuperaciones_cctv"

    with col2:
        if st.button("📦 Auditoría Recibo"):
            st.session_state["subpage"] = "pages.2_auditoria_recibo"

    with col3:
        if st.button("🏭 Auditoría Warehouse"):
            st.session_state["subpage"] = "pages.3_auditoria_warehouse"

    # Cargar la subpágina seleccionada
    if st.session_state["subpage"]:
        st.markdown("---")
        cargar_pagina(st.session_state["subpage"])

# === CONSULTA ===
elif main_page == "🔍 Consulta":
    st.info("🔍 Módulo de consulta aún en desarrollo.")

# === REPORTES ===
elif main_page == "📊 Reportes":
    st.info("📊 Módulo de reportes aún en desarrollo.")

# === CONFIGURACIÓN ===
elif main_page == "⚙️ Configuración":
    st.info("⚙️ Módulo de configuración aún en desarrollo.")

