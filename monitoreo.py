import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la interfaz
st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def cargar_datos():
    # Usamos el nombre exacto que ya corregiste en el Excel
    # El parámetro 'ttl' ayuda a que no dé error 400 por exceso de peticiones
    df = conn.read(worksheet="Distribucion", usecols=[0,1,2,3])
    
    # Limpiamos los nombres de las columnas por seguridad
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos()

    with st.form("formulario_centromatic"):
        st.subheader("Registro de Visita Técnica")
        
        # Lista de clientes desde tu Excel
        nombres_clientes = sorted(df_clientes["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", nombres_clientes)
        
        # Extraer datos automáticamente
        datos_equipo = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Modelo:** {datos_equipo['Modelo']}")
            st.info(f"**Serie:** {datos_equipo['Serie']}")
        
        with col2:
            contador = st.number_input("Lectura de Contador:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)
            
        notas = st.text_area("Notas del Servicio:")
        
        if st.form_submit_button("💾 Guardar en Reportes"):
            nuevo_registro = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_equipo['Modelo'],
                "Serie": datos_equipo['Serie'],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])
            
            # Guardar en la pestaña 'Reportes'
            conn.create(worksheet="Reportes", data=nuevo_registro)
            st.success(f"¡Registro de {cliente_sel} guardado exitosamente!")
            st.balloons()

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("Asegúrate de que en el Excel la pestaña se llame 'Distribucion' (sin tilde).")