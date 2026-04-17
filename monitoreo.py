import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# URL Directa para evitar el Error 400 de los Secrets
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1JsKz8v15giS-wHWPOc8nYYvMUIqoQGVgzLL_EgkCuGY/edit?usp=sharing"

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10) # Bajamos el tiempo para que refresque rápido
def cargar_datos():
    # Leemos la pestaña Distribucion
    df = conn.read(spreadsheet=URL_EXCEL, worksheet="Distribucion", usecols=[0,1,2,3])
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos()

    with st.form("registro_centromatic"):
        st.subheader("Registro de Visita Técnica")
        nombres_clientes = sorted(df_clientes["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", nombres_clientes)
        
        datos_equipo = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Modelo:** {datos_equipo['Modelo']}")
            st.info(f"**Serie:** {datos_equipo['Serie']}")
        with col2:
            contador = st.number_input("Lectura de Contador:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)
            
        notas = st.text_area("Notas del Servicio:")
        
        if st.form_submit_button("💾 Guardar"):
            nuevo_reg = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_equipo['Modelo'],
                "Serie": datos_equipo['Serie'],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])
            conn.create(spreadsheet=URL_EXCEL, worksheet="Reportes", data=nuevo_reg)
            st.success(f"¡Registro de {cliente_sel} guardado exitosamente!")
            st.balloons()

except Exception as e:
    st.error(f"Error detectado: {e}")
