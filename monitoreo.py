import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Centromatic SPS", page_icon="🖨️", layout="centered")
st.title("🖨️ Control Técnico: Centromatic SPS")

# Definimos la URL de forma ultra-limpia
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1JsKz8v15giS-wHWPOc8nYYvMUIqoQGVgzLL_EgkCuGY/edit?usp=sharing"

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def cargar_datos():
    # El secreto aquí es pasar la URL directamente y forzar el refresco
    df = conn.read(spreadsheet=URL_EXCEL, worksheet="Distribucion")
    # Limpiamos los nombres de las columnas por si tienen espacios
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df_clientes = cargar_datos()

    if not df_clientes.empty:
        with st.form("registro_visita"):
            st.subheader("Nueva Entrada de Servicio")
            
            # Buscamos la columna de Clientes
            lista_clientes = sorted(df_clientes["Cliente"].unique())
            cliente_sel = st.selectbox("Seleccione el Cliente:", lista_clientes)
            
            # Filtramos datos del equipo seleccionado
            info_equipo = df_clientes[df_clientes["Cliente"] == cliente_sel].iloc[0]
            
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**Modelo:** {info_equipo['Modelo']}")
                st.success(f"**Serie:** {info_equipo['Serie']}")
            with c2:
                contador = st.number_input("Contador actual:", min_value=0, step=1)
                toners = st.number_input("Tóners entregados:", min_value=0, step=1)
            
            notas = st.text_area("Observaciones:")
            
            if st.form_submit_button("💾 Guardar Reporte"):
                nuevo_dato = pd.DataFrame([{
                    "Fecha": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    "Cliente": cliente_sel,
                    "Modelo": info_equipo['Modelo'],
                    "Serie": info_equipo['Serie'],
                    "Contador": contador,
                    "Toners": toners,
                    "Notas": notas
                }])
                conn.create(spreadsheet=URL_EXCEL, worksheet="Reportes", data=nuevo_dato)
                st.balloons()
                st.success("¡Datos enviados correctamente!")
    else:
        st.warning("No se encontraron datos en la pestaña 'Distribucion'.")

except Exception as e:
    st.error(f"Error de conexión: Asegúrate de que el Excel sea 'Editor' para todos. Detalles: {e}")
