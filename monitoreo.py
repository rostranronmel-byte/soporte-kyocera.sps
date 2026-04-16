import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración visual de la App
st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# 2. Establecer la conexión con los Secrets de Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para cargar los datos de tus clientes
@st.cache_data(ttl=60)
def cargar_datos_centromatic():
    # Lee la pestaña 'Distribucion' (sin tilde)
    # Seleccionamos solo las primeras 4 columnas (Cliente, Modelo, Serie, Dirección)
    df = conn.read(worksheet="Distribucion", usecols=[0, 1, 2, 3])
    
    # Limpieza de encabezados: quita espacios y saltos de línea invisibles
    df.columns = [str(c).strip() for c in df.columns]
    
    # Elimina filas que no tengan nombre de cliente
    df = df.dropna(subset=['Cliente'])
    return df

try:
    # Cargamos la base de datos de San Pedro Sula
    df_clientes = cargar_datos_centromatic()

    # Formulario de entrada de datos
    with st.form("registro_centromatic"):
        st.subheader("📝 Nueva Visita / Entrega de Tóners")

        # Buscador desplegable con los nombres de tus clientes reales
        lista_nombres = sorted(df_clientes["Cliente"].unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", lista_nombres)

        # Extraer automáticamente la información del equipo
        datos_equipo = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            # Mostramos el Modelo y Serie que ya están en tu Excel
            st.info(f"**Modelo:** {datos_equipo['Modelo']}")
            st.info(f"**Serie:** {datos_equipo['Serie']}")
        
        with col2:
            contador = st.number_input("Lectura de Contador Actual:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados (Cantidad):", min_value=0, step=1)

        notas = st.text_area("Notas u Observaciones del Servicio:")

        # Botón para guardar la información
        if st.form_submit_button("💾 Guardar Reporte"):
            # Creamos la fila que se enviará a la pestaña 'Reportes'
            nuevo_reporte = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_equipo['Modelo'],
                "Serie": datos_equipo['Serie'],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])

            # GUARDAR: Se añade la fila a la pestaña 'Reportes' de tu Google Sheets
            conn.create(worksheet="Reportes", data=nuevo_reporte)
            st.success(f"✅ ¡Excelente! Reporte de {cliente_sel} guardado con éxito.")
            st.balloons()

except Exception as e:
    st.error(f"⚠️ Error de Conexión: {e}")
    st.info("Revisa que en tu Google Sheets la pestaña se llame 'Distribucion' y exista una llamada 'Reportes'.")

# Opción para revisar la lista de clientes rápidamente
if st.checkbox("Mostrar tabla de clientes registrados"):
    st.dataframe(df_clientes)