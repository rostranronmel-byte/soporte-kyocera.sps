import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración visual
st.set_page_config(page_title="Kyocera SPS Support", page_icon="🖨️")
st.title("🖨️ Control Técnico Kyocera SPS")

# Conectar a la hoja de Google
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Leer los clientes de la pestaña 'Distribución'
# ttl="0" sirve para que siempre lea los datos más nuevos
df_clientes = conn.read(worksheet="Distribución", ttl="0")

# Limpiamos nombres de columnas (tu Excel tiene saltos de línea como 'Cliente\n')
df_clientes.columns = [c.strip() for c in df_clientes.columns]

# --- INTERFAZ ---
with st.container():
    st.subheader("Registro de Visita")
    
    # Buscador de clientes basado en tu columna "Cliente"
    lista_clientes = df_clientes["Cliente"].unique()
    cliente_sel = st.selectbox("Seleccione el Cliente:", lista_clientes)
    
    # Extraer datos automáticos (Modelo y Serie)
    datos = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        # Mostramos los datos que ya tenemos en el Excel
        st.info(f"**Modelo:** {datos['Modelo']}")
        st.info(f"**Serie:** {datos['Serie']}")
    
    with col2:
        contador = st.number_input("Contador Actual:", min_value=0, step=1)
        toners = st.number_input("Tóners Entregados:", min_value=0, step=1)

    notas = st.text_area("Notas del Servicio (Repuestos, fallas, etc.):")

    if st.button("🚀 Guardar Reporte"):
        # Creamos la fila para la pestaña de Reportes
        nuevo_dato = pd.DataFrame([{
            "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "Cliente": cliente_sel,
            "Modelo": datos['Modelo'],
            "Serie": datos['Serie'],
            "Contador": contador,
            "Toners": toners,
            "Notas": notas
        }])
        
        # Guardar en una pestaña llamada "Reportes"
        # Nota: Debes crear una pestaña llamada 'Reportes' en tu Google Sheet
        conn.create(worksheet="Reportes", data=nuevo_dato)
        st.success("¡Datos guardados correctamente en Google Sheets!")
        st.balloons()