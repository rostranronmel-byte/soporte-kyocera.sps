import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# 2. Establecer la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para cargar datos (sin tildes para evitar errores)
@st.cache_data(ttl=60)
def cargar_datos_sps():
    # Busca la pestaña "Distribucion" (Asegúrate que en el Excel esté igual)
    df = conn.read(worksheet="Distribucion")
    # Limpia encabezados de basura como espacios o \n
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos_sps()

    with st.form("registro_visita"):
        st.subheader("📝 Registrar Nueva Visita")

        # Lista de clientes
        lista_nombres = sorted(df_clientes["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", lista_nombres)

        # Extraer Modelo y Serie automáticamente
        datos_fila = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Modelo:** {datos_fila['Modelo']}")
            st.info(f"**Serie:** {datos_fila['Serie']}")
        
        with col2:
            contador = st.number_input("Lectura de Contador:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)

        notas = st.text_area("Observaciones del Servicio:")

        if st.form_submit_button("💾 Guardar Reporte"):
            nuevo_reporte = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_fila["Modelo"],
                "Serie": datos_fila["Serie"],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])

            # Guarda en la pestaña 'Reportes'
            conn.create(worksheet="Reportes", data=nuevo_reporte)
            st.success(f"✅ ¡Guardado! Reporte de {cliente_sel} enviado.")
            st.balloons()

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Revisa que la pestaña del Excel se llame 'Distribucion' (sin tilde).")