import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Soporte Centromatic SPS",
    page_icon="🖨️",
    layout="centered"
)

st.title("🖨️ Control Técnico: Centromatic San Pedro Sula")

# 2. Conexión a Google Sheets (Usa el link de tus Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para cargar datos con limpieza de columnas
@st.cache_data(ttl=300) # Se actualiza cada 5 minutos
def cargar_datos():
    # Leemos la pestaña de Distribución
    df = conn.read(worksheet="Distribución")
    # LIMPIEZA CLAVE: Quita espacios y saltos de línea (\n) de los encabezados
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos()

    # --- INICIO DEL FORMULARIO ---
    with st.form("formulario_visita"):
        st.subheader("📝 Registrar Nueva Visita / Entrega")

        # Buscador de Clientes
        # Usamos .dropna() por si hay celdas vacías en tu Excel
        lista_clientes = sorted(df_clientes["Cliente"].dropna().unique())
        cliente_sel = st.selectbox("Seleccione el Cliente:", lista_clientes)

        # Extraer automáticamente Modelo y Serie del cliente seleccionado
        datos_cliente = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            # Mostramos el modelo y serie pero "bloqueados" para evitar errores
            modelo = st.text_input("Modelo de Equipo:", value=str(datos_cliente["Modelo"]), disabled=True)
            serie = st.text_input("Número de Serie:", value=str(datos_cliente["Serie"]), disabled=True)
        
        with col2:
            contador = st.number_input("Contador Total de Copias:", min_value=0, step=1)
            toners = st.number_input("Tóners Entregados:", min_value=0, step=1)

        notas = st.text_area("Notas Técnicas (Opcional):")

        # Botón de envío
        boton_enviar = st.form_submit_button("💾 Guardar en Google Sheets")

        if boton_enviar:
            # Crear el nuevo registro
            nuevo_registro = pd.DataFrame([{
                "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "Cliente": cliente_sel,
                "Modelo": datos_cliente["Modelo"],
                "Serie": datos_cliente["Serie"],
                "Contador": contador,
                "Toners": toners,
                "Notas": notas
            }])

            # GUARDAR: Intenta escribir en la pestaña "Reportes"
            try:
                conn.create(worksheet="Reportes", data=nuevo_registro)
                st.success(f"✅ ¡Éxito! Reporte guardado para {cliente_sel}")
                st.balloons()
            except Exception as e:
                st.error("Error al guardar: Asegúrate de tener una pestaña llamada 'Reportes' en tu Google Sheet.")

except Exception as e:
    st.error(f"Hubo un problema al leer las columnas del Excel: {e}")
    st.info("Revisa que los encabezados en tu Excel sean 'Cliente', 'Modelo' y 'Serie'.")

# --- VISTA PREVIA (Opcional) ---
if st.checkbox("Ver lista de clientes cargada"):
    st.write(df_clientes)