"""
Dashboard de Seguimiento POA por Carreras 2025
==============================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import base64

def get_base64_image(image_path):
    """Convierte una imagen a base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Codificar el logo a base64
logo_base64 = get_base64_image("C:/Users/VivoBook/Downloads/Nueva carpeta/LOGO-RECTANGULAR_SIN-FONDO.png")
logo_data_url = f"data:image/png;base64,{logo_base64}" if logo_base64 else None

# =============================================================================
# CONFIGURACIÓN DE PÁGINA - FONDO OSCURO
# =============================================================================
st.set_page_config(
    page_title="Dashboard POA Carreras 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS PERSONALIZADO - FONDO NEGRO
# =============================================================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .main .block-container { padding: 1rem 2rem; max-width: 100%; }
    .header-container {
        background-color: #1F3A5E;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    .header-title { color: white; font-family: 'Times New Roman', serif; font-size: 1.4rem; font-weight: bold; margin: 0; }
    .header-subtitle { color: #c9d1d9; font-family: 'Arial', sans-serif; font-size: 0.85rem; margin: 0; }
    .section-title {
        color: #58a6ff; font-family: 'Arial', sans-serif; font-size: 1.1rem;
        font-weight: bold; margin: 1rem 0 0.75rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #238636;
    }
    .stSelectbox > div > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
    .stSelectbox label { color: #8b949e !important; }
    .kpi-card {
        background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; text-align: center;
    }
    .kpi-label { color: #8b949e; font-family: 'Arial', sans-serif; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem; }
    .kpi-value { color: #58a6ff; font-family: 'Arial', sans-serif; font-size: 1rem; font-weight: bold; }
    .kpi-main {
        background: linear-gradient(135deg, #FFD700 0%, #FFC107 100%); border: none; border-radius: 10px; padding: 1.25rem; margin: 0.5rem 0; text-align: center;
    }
    .kpi-main-label { color: #1a1a1a; font-family: 'Arial', sans-serif; font-size: 0.85rem; text-transform: uppercase; font-weight: bold; margin-bottom: 0.5rem; }
    .kpi-main-value { color: #000000; font-family: 'Arial Black', sans-serif; font-size: 2.2rem; font-weight: bold; }
    div[data-testid="stPlotlyChart"] { background-color: transparent; }
    div[data-testid="stDataFrame"] { background-color: #161b22; border-radius: 8px; }
    .streamlit-expanderHeader { background-color: #161b22 !important; color: #e6edf3 !important; border: 1px solid #30363d; border-radius: 8px; }
    hr { border-color: #30363d; margin: 1.5rem 0; }
    .footer { background-color: #161b22; padding: 1rem; border-radius: 8px; margin-top: 2rem; text-align: center; color: #8b949e; font-size: 0.8rem; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 0.75rem; }
    div[data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.75rem; }
    div[data-testid="stMetricValue"] { color: #58a6ff; font-size: 1.1rem; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CARGA DE DATOS SIMPLIFICADA
# =============================================================================
@st.cache_data
def load_data():
    """
    Carga los datos desde el archivo Excel.
    """
    try:
        file_path = "https://raw.githubusercontent.com/TU_USUARIO/REPO/main/Matriz%20Seguimiento%20Carreras%202025.xlsx"
        
        # Obtener nombres de todas las hojas
        xlsx = pd.ExcelFile(file_path)
        all_sheets = xlsx.sheet_names
        
        # Hojas administrativas a excluir
        excluded = ['resumen', 'Resumen', 'resumen_carreras', 'indicadores_carreras', 
                    'actividades_carreras', 'Hoja 1', 'Dashboard', 'Data', 'Config',
                    'Summary', 'summary', 'Índice', 'Indice']
        
        # Las carreras son los nombres de las hojas
        carreras_names = [s for s in all_sheets if s not in excluded]
        
        # Cargar hoja resumen_carreras
        df_resumen = pd.read_excel(file_path, sheet_name='resumen_carreras')
        df_resumen['CARRERA'] = df_resumen['CARRERA'].astype(str).str.strip()
        
        # Filtrar solo 2025
        df_resumen = df_resumen[df_resumen['año'] == 2025]
        
        # Crear diccionario: cada carrera tiene su fila en resumen_carreras
        # Vamos a asumir que las filas de resumen_carreras corresponden a las hojas de carreras
        # El orden debería ser el mismo
        
        # Crear un diccionario con los datos de cada carrera
        carreras_data = {}
        
        for idx, row in df_resumen.iterrows():
            carrera_id = str(row.get('CARRERA', ''))
            
            if carrera_id.startswith('gid='):
                # Usar el índice de la fila para encontrar la carrera correspondiente
                row_position = list(df_resumen.index).index(idx)
                if row_position < len(carreras_names):
                    nombre = carreras_names[row_position]
                else:
                    nombre = carrera_id
            else:
                # Si ya es un nombre, usarlo directamente
                nombre = carrera_id
            
            carreras_data[nombre] = {
                'director': row.get('DIRECTOR/A', 'N/A'),
                'poa': row.get('POA', 'N/A'),
                'informe_semestral': row.get('INFORME SEMESTRAL', 'N/A'),
                'matriz_semestral': row.get('MATRIZ SEMESTRAL', 'N/A'),
                'informe_final': row.get('INFORME FINAL', 'N/A'),
                'matriz_final': row.get('MATRIZ FINAL', 'N/A'),
                'observacion': row.get('Observación', 'N/A'),
                'avance_poa': (row.get('%Avance poa', 0) or 0) * 100,
            }
        
        # Si algunas carreras no tienen datos, agregarlas con valores por defecto
        for carrera in carreras_names:
            if carrera not in carreras_data:
                carreras_data[carrera] = {
                    'director': 'N/A',
                    'poa': 'N/A',
                    'informe_semestral': 'N/A',
                    'matriz_semestral': 'N/A',
                    'informe_final': 'N/A',
                    'matriz_final': 'N/A',
                    'observacion': 'Sin datos',
                    'avance_poa': 0,
                }
        
        return carreras_data, carreras_names
        
    except Exception as e:
        st.error(f"Error: {e}")
        return {}, []

CARRERAS_DATA, CARRERAS_LIST = load_data()

# =============================================================================
# PALETA DE COLORES
# =============================================================================
COLORS = {
    'background': '#0d1117', 'card_bg': '#161b22', 'header': '#1F3A5E',
    'yellow': '#FFD700', 'orange': '#FFA500', 'orange_dark': '#CC8400',
    'text': '#e6edf3', 'text_secondary': '#8b949e', 'border': '#30363d',
    'accent': '#58a6ff', 'success': '#3fb950',
}

# =============================================================================
# GRÁFICOS
# =============================================================================
def grafico_barras(carreras_data, carreras_list):
    """Crea gráfico de barras horizontales."""
    if not carreras_data or not carreras_list:
        return None
    
    # Crear lista de datos
    datos = []
    for carrera in carreras_list:
        if carrera in carreras_data:
            datos.append({
                'Carrera': carrera,
                'Avance POA': carreras_data[carrera]['avance_poa']
            })
    
    if not datos:
        return None
    
    df = pd.DataFrame(datos)
    df = df.sort_values('Avance POA', ascending=True)
    
    colores = []
    for avance in df['Avance POA']:
        if avance >= 80:
            colores.append(COLORS['yellow'])
        elif avance >= 60:
            colores.append(COLORS['orange'])
        else:
            colores.append(COLORS['orange_dark'])
    
    fig = go.Figure(data=[go.Bar(
        y=df['Carrera'], x=df['Avance POA'], orientation='h',
        marker_color=colores,
        text=[f'{v:.1f}%' for v in df['Avance POA']],
        textposition='inside',
        textfont=dict(color='#000000', size=11, family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Avance: %{x:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text='<b>AVANCE POA POR CARRERA</b>', font=dict(size=16, color=COLORS['accent'], family='Arial'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=dict(text='Porcentaje de Avance (%)', font=dict(size=12, color=COLORS['text_secondary'])),
            tickfont=dict(size=10, color=COLORS['text_secondary']),
            range=[0, 100], gridcolor=COLORS['border'], showgrid=True, gridwidth=1
        ),
        yaxis=dict(title='', tickfont=dict(size=10, color=COLORS['text']), automargin=True),
        margin=dict(l=20, r=20, t=60, b=50),
        height=max(400, len(df) * 40),
        showlegend=False
    )
    
    return fig

def grafico_barras_unica(carrera_seleccionada, avance):
    """Crea gráfico de barras para una sola carrera."""
    
    fig = go.Figure(data=[go.Bar(
        y=[carrera_seleccionada],
        x=[avance],
        orientation='h',
        marker_color=COLORS['yellow'],
        text=f'{avance:.1f}%',
        textposition='inside',
        textfont=dict(color='#000000', size=14, family='Arial Black'),
        hovertemplate=f'<b>{carrera_seleccionada}</b><br>Avance: {avance:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=f'<b>{carrera_seleccionada.upper()}</b>', font=dict(size=16, color=COLORS['accent'], family='Arial'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=dict(text='Porcentaje de Avance (%)', font=dict(size=12, color=COLORS['text_secondary'])),
            tickfont=dict(size=10, color=COLORS['text_secondary']),
            range=[0, 100], gridcolor=COLORS['border'], showgrid=True, gridwidth=1
        ),
        yaxis=dict(title='', tickfont=dict(size=12, color=COLORS['text']), automargin=True),
        margin=dict(l=20, r=20, t=60, b=50),
        height=150,
        showlegend=False
    )
    
    return fig

def grafico_donut(avance):
    """Crea gráfico donut."""
    fig = go.Figure(data=[go.Pie(
        labels=['Completado', 'Pendiente'],
        values=[avance, 100 - avance],
        hole=0.7,
        marker=dict(colors=[COLORS['yellow'], COLORS['border']]),
        textinfo='none',
        hoverinfo='label+percent'
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        annotations=[dict(text=f'<b>{avance:.1f}%</b>', font=dict(size=24, color=COLORS['accent']), showarrow=False, x=0.5, y=0.5)]
    )
    return fig

# =============================================================================
# INTERFAZ PRINCIPAL
# =============================================================================
def main():
    """Función principal."""
    
    # Encabezado con logo dentro del cuadro azul
    st.markdown(f"""
    <div class="header-container" style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 1.5rem;">
        <div>
            <h1 class="header-title" style="margin: 0;">INSTITUTO TECNOLÓGICO SUPERIOR AZUAY</h1>
            <p class="header-subtitle" style="margin: 0;">SEGUIMIENTO POA - CARRERAS 2025</p>
        </div>
        <img src="{logo_data_url}" style="height: 100px; max-width: 350px;">
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de carrera
    if not CARRERAS_LIST:
        st.error("❌ No se encontraron carreras.")
        return
    
    carrera_seleccionada = st.selectbox("SELECCIONAR CARRERA:", options=['Todas las Carreras'] + CARRERAS_LIST, index=0)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # VISTA GENERAL
    if carrera_seleccionada == 'Todas las Carreras':
        # Calcular métricas
        total_carreras = len([c for c in CARRERAS_LIST if c in CARRERAS_DATA])
        avances = [CARRERAS_DATA[c]['avance_poa'] for c in CARRERAS_LIST if c in CARRERAS_DATA]
        avance_promedio = sum(avances) / len(avances) if avances else 0
        
        poa_entregados = len([c for c in CARRERAS_LIST if c in CARRERAS_DATA and CARRERAS_DATA[c]['poa'] == 'ENTREGADO'])
        informes_entregados = len([c for c in CARRERAS_LIST if c in CARRERAS_DATA and CARRERAS_DATA[c]['informe_semestral'] == 'ENTREGADO'])
        matrices_entregadas = len([c for c in CARRERAS_LIST if c in CARRERAS_DATA and CARRERAS_DATA[c]['matriz_semestral'] == 'ENTREGADO'])
        
        # Layout 3 columnas
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        
        with col_izq:
            st.markdown('<p class="section-title">RESUMEN GENERAL</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="kpi-card"><p class="kpi-label">Total Carreras</p><p class="kpi-value">{total_carreras}</p></div>
            <div class="kpi-card"><p class="kpi-label">POA Entregados</p><p class="kpi-value">{poa_entregados}/{total_carreras}</p></div>
            <div class="kpi-card"><p class="kpi-label">Informes Semestrales</p><p class="kpi-value">{informes_entregados}/{total_carreras}</p></div>
            <div class="kpi-card"><p class="kpi-label">Matrices Semestrales</p><p class="kpi-value">{matrices_entregadas}/{total_carreras}</p></div>
            """, unsafe_allow_html=True)
        
        with col_centro:
            st.markdown('<p class="section-title">AVANCE POA POR CARRERA</p>', unsafe_allow_html=True)
            fig = grafico_barras(CARRERAS_DATA, CARRERAS_LIST)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col_der:
            st.markdown('<p class="section-title">RESUMEN</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="kpi-main">
                <p class="kpi-main-label">Avance POA General</p>
                <p class="kpi-main-value">{avance_promedio:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(grafico_donut(avance_promedio), use_container_width=True)
            
            alto = len([a for a in avances if a >= 80])
            medio = len([a for a in avances if 60 <= a < 80])
            bajo = len([a for a in avances if a < 60])
            
            st.markdown(f"""
            <div style="color: #e6edf3; font-size: 0.9rem; margin-top: 1rem;">
                <p><span style="color: #FFD700;">●</span> Alto (>80%): <strong>{alto}</strong></p>
                <p><span style="color: #FFA500;">●</span> Medio (60-79%): <strong>{medio}</strong></p>
                <p><span style="color: #CC8400;">●</span> Bajo (<60%): <strong>{bajo}</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    # VISTA POR CARRERA - CORREGIDO: muestra solo la carrera seleccionada
    else:
        if carrera_seleccionada not in CARRERAS_DATA:
            st.error(f"No hay datos para: {carrera_seleccionada}")
            return
        
        datos = CARRERAS_DATA[carrera_seleccionada]
        
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        
        with col_izq:
            st.markdown('<p class="section-title">INFORMACIÓN</p>', unsafe_allow_html=True)
            
            poa_color = COLORS['success'] if datos['poa'] == 'ENTREGADO' else COLORS['orange']
            informe_color = COLORS['success'] if datos['informe_semestral'] == 'ENTREGADO' else COLORS['orange']
            matriz_color = COLORS['success'] if datos['matriz_semestral'] == 'ENTREGADO' else COLORS['orange']
            
            st.markdown(f"""
            <div class="kpi-card"><p class="kpi-label">Responsable</p><p class="kpi-value" style="font-size: 0.9rem;">{datos['director']}</p></div>
            <div class="kpi-card"><p class="kpi-label">POA</p><p class="kpi-value" style="color: {poa_color};">{datos['poa']}</p></div>
            <div class="kpi-card"><p class="kpi-label">Informe Semestral</p><p class="kpi-value" style="color: {informe_color};">{datos['informe_semestral']}</p></div>
            <div class="kpi-card"><p class="kpi-label">Matriz Semestral</p><p class="kpi-value" style="color: {matriz_color};">{datos['matriz_semestral']}</p></div>
            <div class="kpi-card"><p class="kpi-label">Informe Final</p><p class="kpi-value">{datos['informe_final']}</p></div>
            <div class="kpi-card"><p class="kpi-label">Matriz Final</p><p class="kpi-value">{datos['matriz_final']}</p></div>
            """, unsafe_allow_html=True)
        
        with col_centro:
            st.markdown(f'<p class="section-title">AVANCE DE {carrera_seleccionada.upper()}</p>', unsafe_allow_html=True)
            
            # CORRECCIÓN: Usar la función para gráfica individual
            fig = grafico_barras_unica(carrera_seleccionada, datos['avance_poa'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color: #161b22; border: 2px solid #58a6ff; border-radius: 8px; padding: 1rem; margin-top: 1rem; text-align: center;">
                <p style="color: #8b949e; margin: 0; font-size: 0.9rem;">CARRERA SELECCIONADA</p>
                <p style="color: #58a6ff; margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: bold;">
                    {carrera_seleccionada} - {datos['avance_poa']:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_der:
            st.markdown('<p class="section-title">AVANCE</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="kpi-main">
                <p class="kpi-main-label">Avance POA</p>
                <p class="kpi-main-value">{datos['avance_poa']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(grafico_donut(datos['avance_poa']), use_container_width=True)
            
            if datos['observacion'] and datos['observacion'] != 'Sin datos':
                st.markdown(f"""
                <div style="background-color: #161b22; border-left: 4px solid #FFD700; padding: 0.75rem; border-radius: 4px; margin-top: 1rem; font-size: 0.8rem;">
                    <p style="color: #e6edf3; margin: 0;"><strong>Observación:</strong></p>
                    <p style="color: #8b949e; margin: 0.5rem 0 0 0;">{datos['observacion']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="footer">
        <p>Dashboard POA Carreras 2025 | Generado: {datetime.now().strftime('%Y-%m-%d')} | Total: {len(CARRERAS_LIST)} carreras</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enlace para más información
    st.markdown(f"""
    <div style="text-align: center; margin-top: 1.5rem; padding: 1rem; background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;">
        <p style="color: #8b949e; font-family: 'Arial', sans-serif; font-size: 0.85rem; margin: 0 0 0.5rem 0;">
            ¿Te falta información o tienes dudas sobre tu avance?
        </p>
        <a href="https://docs.google.com/spreadsheets/d/1FYv0ZFXwqOkbo2YYTGuW2ommKCmk9jTU/edit?gid=1746760684#gid=1746760684" 
           target="_blank" 
           style="color: #58a6ff; font-family: 'Arial', sans-serif; font-size: 0.9rem; text-decoration: none; font-weight: bold;">
            Ver información completa en Google Sheets
        </a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
