import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargamos los datos de la pestaña Distribución
@st.cache_data(ttl=60)
def cargar_clientes():
    df = conn.read(worksheet="Distribución")
    # Limpiamos los nombres de las columnas (quita el \n y espacios)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_clientes()
    
    with st.form("registro_soporte"):
        st.subheader("📝 Registrar Nueva Visita")
        
        # Lista de clientes única y ordenada
        lista_nombres = sorted(df_clientes["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", lista_nombres)
        
        # Obtenemos los datos automáticos del cliente
        datos = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Modelo:** {datos['Modelo']}")
            st.info(f"**Serie:** {datos['Serie']}")
            st.caption(f"📍 {datos['Dirección']}")
        
        with col2:
            contador = st.number_input("Contador Actual:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)
            
        notas = st.text_area("Notas / Observaciones:")
        
        if st.form_submit_button("💾 Guardar Reporte"):
            # Creamos la nueva fila
            nuevo_dato = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos['Modelo'],
                "Serie": datos['Serie'],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])
            
            # Guardamos en la pestaña Reportes
            conn.create(worksheet="Reportes", data=nuevo_dato)
            st.success(f"¡Hecho! El reporte de {cliente_sel} se guardó en Google Sheets.")
            st.balloons()

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Revisa que la pestaña 'Distribución' y 'Reportes' existan en tu Google Sheet.")