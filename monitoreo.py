import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# --- SOLUCIÓN AL ERROR 400 ---
# Esta función limpia cualquier salto de línea que los Secrets metan por error
def get_clean_url():
    raw_url = st.secrets["connections"]["gsheets"]["url"]
    return raw_url.replace("\n", "").replace("\r", "").strip()

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def cargar_datos():
    url_final = get_clean_url()
    # Leemos la pestaña Distribucion
    df = conn.read(spreadsheet=url_final, worksheet="Distribucion", usecols=[0,1,2,3])
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos()

    with st.form("registro_centromatic"):
        st.subheader("Nueva Visita Técnica")
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
            
        notas = st.text_area("Notas:")
        
        if st.form_submit_button("💾 Guardar Datos"):
            nuevo = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_equipo['Modelo'],
                "Serie": datos_equipo['Serie'],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])
            # Usamos la URL limpia también para guardar
            conn.create(spreadsheet=get_clean_url(), worksheet="Reportes", data=nuevo)
            st.success("¡Registro guardado en Google Sheets!")
            st.balloons()

except Exception as e:
    # Si el error persiste, aquí veremos exactamente qué es
    st.error(f"Error detectado: {e}")
