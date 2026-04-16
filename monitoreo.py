import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la interfaz
st.set_page_config(page_title="Soporte Kyocera", page_icon="🖨️")
st.title("🖨️ Control Técnico: Kyocera San Pedro Sula")

archivo_datos = "datos_maquinas.csv"

# Cargar o crear base de datos
if os.path.exists(archivo_datos):
    df = pd.read_csv(archivo_datos)
else:
    df = pd.DataFrame(columns=["Fecha", "Cliente", "Serie", "Modelo", "Contador", "Toner" "Proxima Visita"])

# --- SECCIÓN DE REGISTRO ---
with st.expander("➕ Registrar Nueva Visita / Entrega de Tóner", expanded=True):
    with st.form("registro_tecnico", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Nombre del Cliente")
            serie = st.text_input("Número de Serie (SN)")
            modelo = st.selectbox("Modelo del Equipo", [
                "ECOSYS M2040", "ECOSYS M2640", "ECOSYS M3040", 
                "ECOSYS M3145", "ECOSYS M3645", "TASKALFA 3501I", 
                "TASKALFA 4501I", "TASKALFA 5501I", "TASKALFA 406CI", 
                "TASKALFA 5002I", "TASKALFA 6002I", "TASKALFA 6003I", 
                "TASKALFA 5053CI", "TASKALFA 6053CI", "Otro"
            ])
            
        with col2:
            contador = st.number_input("Contador Total de Copias", min_value=0, step=1)
            toner = st.number_input("Tóners Entregados", min_value=0, step=1)
            comentarios = st.text_area("Notas Técnicas (Opcional)")
        
        boton_guardar = st.form_submit_button("💾 Guardar en Base de Datos")

if boton_guardar:
    nueva_fila = {
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Cliente": cliente,
        "Serie": serie.upper(),
        "Modelo": modelo,
        "Contador": contador,
        "Toner": toner
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(archivo_datos, index=False)
    st.success(f"✅ Registro guardado para el equipo {serie.upper()}")
    st.rerun()

# --- SECCIÓN DE CONSULTA ---
st.divider()
st.subheader("🔍 Historial y Búsqueda")

# Filtro rápido por número de serie
busqueda = st.text_input("Escribe el Número de Serie para filtrar:")

if busqueda:
    # Filtramos el dataframe original según la búsqueda
    df_filtrado = df[df['Serie'].str.contains(busqueda.upper(), na=False)]
    st.write(f"Mostrando resultados para: {busqueda}")
    st.dataframe(df_filtrado, use_container_width=True)
else:
    # Si no hay búsqueda, muestra los últimos 10 registros
    st.write("Últimos registros guardados:")
    st.dataframe(df.tail(10), use_container_width=True)

# Botón para descargar a Excel/CSV por si ocupas mandar reporte a la oficina
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar todo el historial (CSV)",
        data=csv,
        file_name='reporte_kyocera.csv',
        mime='text/csv',
    )