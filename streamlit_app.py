import streamlit as st
import importlib

# === CONFIGURACIÓN GENERAL ===
st.set_page_config(
    page_title="Sistema CCTV",
    page_icon="🎥",
    layout="centered"
)

# === ESTADO DE SESIÓN ===
if "current_form" not in st.session_state:
    st.session_state.current_form = None  # No hay formulario activo


# === FUNCIÓN PARA CAMBIAR DE FORMULARIO ===
def open_form(form_name):
    st.session_state.current_form = form_name


# === SIDEBAR ===
st.sidebar.title("📂 Navegación")
page = st.sidebar.radio(
    "Selecciona un módulo:",
    ["🏠 Inicio", "📋 Registro", "🔍 Consulta", "📊 Reportes", "⚙️ Configuración"]
)

# === PÁGINA PRINCIPAL ===
if page == "🏠 Inicio":
    st.session_state.current_form = None
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

# === MÓDULO REGISTRO ===
elif page == "📋 Registro":
    st.title("📋 Registro de actividades")

    # Si no hay formulario abierto, mostrar botones
    if st.session_state.current_form is None:
        st.write("Selecciona el formulario que deseas abrir:")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("🧾 Recuperaciones CCTV", on_click=lambda: open_form("recuperaciones_cctv"))
        with col2:
            st.button("📦 Auditoría Recibo", on_click=lambda: open_form("auditoria_recibo"))
        with col3:
            st.button("🏭 Auditoría Warehouse", on_click=lambda: open_form("auditoria_warehouse"))

    # Si ya hay un formulario activo, cargarlo dinámicamente
    else:
        try:
            form_module = importlib.import_module(f"forms.{st.session_state.current_form}")
            form_module.main()  # Llama la función principal del formulario
        except Exception as e:
            st.error(f"❌ Error al cargar el formulario: {e}")

        st.markdown("---")
        st.button("⬅️ Volver al menú de registro", on_click=lambda: open_form(None))

# === MÓDULOS RESTANTES ===
elif page == "🔍 Consulta":
    st.session_state.current_form = None
    st.info("🔍 Módulo de consulta aún en desarrollo.")

elif page == "📊 Reportes":
    st.session_state.current_form = None
    st.info("📊 Módulo de reportes aún en desarrollo.")

elif page == "⚙️ Configuración":
    st.session_state.current_form = None
    st.info("⚙️ Módulo de configuración aún en desarrollo.")
