import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración inicial
excel_path = "nacio.xlsx"
individual_sheets = [
    'AMBA 2019', 'AMBA 2022', 'EMBA 2018 FDS', 'EMBA JULIO 2018',
    'EMBA FDS 2020', 'EMBA 3X3 2020', 'EMBA 3X3 2021',
    'EMBA FDS 2021', 'EMBA FDS 2022', 'EMBA 3X3 2022'
]
total_sheet_name = 'TOTAL'

# Paleta de colores consistente
COLOR_PALETTE = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24

# Cargar datos
@st.cache_data
def load_data():
    sheets_dict = pd.read_excel(excel_path, sheet_name=individual_sheets)
    df_total = pd.concat(sheets_dict.values(), ignore_index=True)
    sheets_dict[total_sheet_name] = df_total
    return sheets_dict

sheets_dict = load_data()

# Función para crear visualización mejorada con solo gráfico de torta
def create_pie_chart_view(df, title):
    if "Nacionalidad" not in df.columns:
        st.error("La hoja no contiene una columna llamada 'Nacionalidad'.")
        return
    
    nacionalidades = df['Nacionalidad'].value_counts().reset_index()
    nacionalidades.columns = ['Nacionalidad', 'Cantidad']
    nacionalidades['Porcentaje'] = (nacionalidades['Cantidad'] / nacionalidades['Cantidad'].sum()) * 100
    nacionalidades = nacionalidades.sort_values('Cantidad', ascending=False)
    
    # Crear gráfico de torta con colores consistentes
    fig = px.pie(
        nacionalidades,
        values='Cantidad',
        names='Nacionalidad',
        title=f"Distribución de Nacionalidades - {title}",
        hole=0.3,
        color_discrete_sequence=COLOR_PALETTE
    )
    
    # Mejorar el diseño
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='radial',
        marker=dict(line=dict(color='#FFFFFF', width=1))
    )
    
    fig.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05,
            font=dict(size=10)
        ),
        height=600,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Mostrar tabla resumen debajo del gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla resumen ordenada
    st.subheader("Resumen Numérico")
    display_df = nacionalidades.copy()
    display_df['Porcentaje'] = display_df['Porcentaje'].round(1).astype(str) + '%'
    st.dataframe(
        display_df.style.format({'Cantidad': '{:,}'}),
        height=min(400, 50 + len(nacionalidades) * 35),
        use_container_width=True,
        hide_index=True
    )

# Crear tabs
sheet_names = individual_sheets + [total_sheet_name]
tabs = st.tabs(sheet_names)

for i, sheet_name in enumerate(sheet_names):
    with tabs[i]:
        st.title(f"Análisis de Nacionalidades - {sheet_name}")
        
        # Tratamiento especial para el TOTAL
        if sheet_name == total_sheet_name:
            df = sheets_dict[sheet_name]
            
            # Filtro interactivo para el TOTAL
            min_count = st.slider(
                "Filtrar nacionalidades con mínimo de personas:",
                min_value=1,
                max_value=50,
                value=10,
                key=f"filter_{sheet_name}"
            )
            
            filtered_df = df[df.groupby('Nacionalidad')['Nacionalidad'].transform('count') >= min_count]
            create_pie_chart_view(filtered_df, f"{sheet_name} (≥{min_count} personas)")
        else:
            create_pie_chart_view(sheets_dict[sheet_name], sheet_name)