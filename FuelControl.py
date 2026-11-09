import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Control de Combustible Vehicular", page_icon="🚗", layout="wide"
)

st.title("🚗 Control de Combustible y Rendimiento")
st.write(
    "Gestiona las cargas de combustible, kilometraje, costos y eficiencia de tu"
    " vehículo."
)

# Inicializar estado con un DataFrame vacío
if "data" not in st.session_state:
  st.session_state.data = pd.DataFrame(
      columns=[
          "Fecha",
          "Kilometraje (km)",
          "Galones / Litros",
          "Costo Total ($)",
          "Precio por Unidad ($)",
      ]
  )

# Menú lateral de opciones
menu = st.sidebar.selectbox(
    "Menú de Opciones",
    [
        "📊 Resumen y Métricas",
        "➕ Registrar Carga",
        "📋 Historial de Cargas",
        "⚙️ Configuración y Datos",
    ],
)

df = st.session_state.data

if menu == "📊 Resumen y Métricas":
  st.header("Resumen General del Vehículo")

  if df.empty:
    st.info(
        "👋 ¡Bienvenido! Aún no hay registros. Ve a la sección **'Registrar"
        " Carga'** en el menú lateral para agregar tu primera carga."
    )
  else:
    total_gasto = df["Costo Total ($)"].sum()
    total_combustible = df["Galones / Litros"].sum()
    km_recorridos = df["Kilometraje (km)"].max() - df["Kilometraje (km)"].min()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gasto Total", f"${total_gasto:.2f}")
    col2.metric("Combustible Total", f"{total_combustible:.1f} unidades")
    col3.metric("Kilómetros Totales", f"{km_recorridos} km")

    if total_combustible > 0 and km_recorridos > 0:
      rendimiento_promedio = km_recorridos / total_combustible
      col4.metric("Rendimiento Promedio", f"{rendimiento_promedio:.2f} km/u")
    else:
      col4.metric("Rendimiento Promedio", "N/A")

    st.subheader("Evolución del Kilometraje")
    if len(df) > 1:
      chart_data = df.set_index("Fecha")["Kilometraje (km)"]
      st.line_chart(chart_data)
    else:
      st.write("Agrega más de un registro para ver la gráfica de evolución.")

elif menu == "➕ Registrar Carga":
  st.header("Registrar Nueva Carga de Combustible")

  with st.form("form_carga"):
    col1, col2 = st.columns(2)
    with col1:
      fecha = st.date_input("Fecha de carga")
      ultimo_km = (
          float(df["Kilometraje (km)"].max()) if not df.empty else 0.0
      )
      kilometraje = st.number_input(
          "Kilometraje actual (Odómetro)",
          min_value=0.0,
          step=1.0,
          value=ultimo_km,
      )
    with col2:
      cantidad = st.number_input(
          "Cantidad (Galones o Litros)", min_value=0.0, step=0.1, value=0.0
      )
      costo_total = st.number_input(
          "Costo Total ($)", min_value=0.0, step=0.01, value=0.0
      )

    submitted = st.form_submit_button("Guardar Carga")
    if submitted:
      if cantidad > 0 and costo_total > 0:
        precio_unidad = costo_total / cantidad
        nuevo_registro = pd.DataFrame({
            "Fecha": [str(fecha)],
            "Kilometraje (km)": [kilometraje],
            "Galones / Litros": [cantidad],
            "Costo Total ($)": [costo_total],
            "Precio por Unidad ($)": [precio_unidad],
        })
        st.session_state.data = pd.concat([df, nuevo_registro], ignore_index=True)
        st.success("¡Carga registrada exitosamente!")
      else:
        st.warning(
            "Por favor ingresa una cantidad y un costo mayor a cero para"
            " guardar la carga."
        )

elif menu == "📋 Historial de Cargas":
  st.header("Historial Detallado de Registros")
  if df.empty:
    st.info("No hay registros disponibles todavía.")
  else:
    st.dataframe(df, use_container_width=True)

    if st.button("Eliminar último registro"):
      if not df.empty:
        st.session_state.data = df.iloc[:-1].reset_index(drop=True)
        st.rerun()

elif menu == "⚙️ Configuración y Datos":
  st.header("Exportar / Importar Datos")
  st.write("Descarga tus datos actuales en formato CSV para respaldo.")

  if df.empty:
    st.warning("No hay datos para exportar todavía.")
  else:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar datos en CSV",
        data=csv,
        file_name="control_combustible.csv",
        mime="text/csv",
    )