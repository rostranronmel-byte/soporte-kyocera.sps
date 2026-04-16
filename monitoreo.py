import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Soporte Centromatic SPS", page_icon="🖨️")
st.title("🖨️ Control Técnico: Centromatic SPS")

# 2. Establecer la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para cargar datos (apunta a tu enlace de Google Sheets)
@st.cache_data(ttl=60)
def cargar_datos_sps():
    # Lee la pestaña "Distribución" directamente de tu enlace
    df = conn.read(worksheet="Distribución")
    
    # LIMPIEZA CRÍTICA: Quita espacios y saltos de línea de los encabezados
    df.columns = [str(c).strip() for c in df.columns]
    
    # Filtramos filas vacías por si acaso
    df = df.dropna(subset=['Cliente'])
    return df

try:
    df_clientes = cargar_datos_sps()

    with st.form("registro_visita"):
        st.subheader("📝 Registrar Nueva Visita / Entrega")

        # Buscador de clientes basado en tu columna real de "Cliente"
        lista_nombres = sorted(df_clientes["Cliente"].unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", lista_nombres)

        # Extraer automáticamente Modelo y Serie del cliente seleccionado
        datos_fila = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            # Los datos vienen de tu Excel automáticamente
            modelo = st.text_input("Modelo Detectado:", value=str(datos_fila["Modelo"]), disabled=True)
            serie = st.text_input("Serie Detectada:", value=str(datos_fila["Serie"]), disabled=True)
        
        with col2:
            contador = st.number_input("Lectura de Contador:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)

        notas = st.text_area("Observaciones del Servicio:")

        # Botón para guardar
        if st.form_submit_button("💾 Guardar Reporte en Google Sheets"):
            nuevo_reporte = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_fila["Modelo"],
                "Serie": datos_fila["Serie"],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])

            # Guarda en la pestaña 'Reportes' (debe existir en tu Sheet)
            conn.create(worksheet="Reportes", data=nuevo_reporte)
            st.success(f"✅ ¡Guardado! El reporte de {cliente_sel} se envió correctamente.")
            st.balloons()

except Exception as e:
    st.error(f"Error al conectar con la hoja: {e}")
    st.info("Asegúrate de que la pestaña se llame 'Distribución' y que en Secrets esté el link correcto.")

# Opcional: Ver tabla de clientes (solo para el admin)
if st.checkbox("Mostrar base de datos de clientes"):
    st.dataframe(df_clientes)