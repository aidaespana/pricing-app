import streamlit as st
import pandas as pd
import numpy as np
import io

# --- 1. CONFIGURACIÓ ---
st.set_page_config(layout="wide", page_title="Deporvillage Pricing Master", page_icon="🎯")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.image("https://www.deporvillage.com/static/version1677587740/frontend/Deporvillage/default/es_ES/images/logo.svg", width=180)
    st.header("⚙️ Control Panel")
    uploaded_file = st.file_uploader("Puja l'Excel de Snowflake", type=["xlsx", "csv"])

# --- 3. LOGICA PRINCIPAL ---
if uploaded_file:
    # Càrrega de dades
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    df.columns = df.columns.str.upper().str.strip()
    
    # Neteja de dades (com al teu Colab)
    df['FACTURACIÓN 28 DÍAS'] = df['FACTURACIÓN 28 DÍAS'].fillna(0)
    if 'ROTACIÓN 28 DÍAS' in df.columns:
        df['ROTACIÓN 28 DÍAS'] = np.where(df['VENTAS 28 DÍAS'] <= 0, 100, df['ROTACIÓN 28 DÍAS'])
    
    # Mètriques globals
    margen_medio = df['MARGEN'].mean()
    total_fact_marca = df['FACTURACIÓN 28 DÍAS'].sum()
    total_stock_marca = df['VALOR STOCK INTERNO'].sum()
    total_skus_marca = len(df)
    marca_nom = df['MARCA'].iloc[0]

    st.title(f"🎯 Brand Strategy: {marca_nom}")

    # PESTANYES A PANTALLA COMPLETA
    tab_resum, tab_detall, tab_bi = st.tabs(["📊 Resum de Marca", "🔎 Anàlisi Detallat", "🌐 Competidors (Minderest)"])

    # --- PESTANYA 1: RESUM EXECUTIU ---
    with tab_resum:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Facturació Total (28d)", f"{total_fact_marca:,.2f} €")
        col2.metric("Valor Stock Total", f"{total_stock_marca:,.2f} €")
        col3.metric("Margen Medio", f"{margen_medio:.2f}%")
        col4.metric("Total SKUs", total_skus_marca)
        
        st.divider()
        
        # Funció per crear les "Targetes de Segment" que tant t'agraden
        def targeta_segment(titol, subdf, color, icona):
            n_skus = len(subdf)
            val_stock = subdf['VALOR STOCK INTERNO'].sum()
            fact_seg = subdf['FACTURACIÓN 28 DÍAS'].sum()
            
            with st.container():
                st.markdown(f"### {icona} {titol}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("SKUs", f"{n_skus} ({(n_skus/total_skus_marca)*100:.1f}%)")
                c2.metric("Valor Stock", f"{val_stock:,.0f}€ ({(val_stock/total_stock_marca)*100:.1f}%)")
                c3.metric("Facturació", f"{fact_seg:,.0f}€ ({(fact_seg/total_fact_marca)*100:.1f}%)")
                c4.write("") # Espai buit
                st.markdown(f"<div style='border-bottom: 3px solid {color}; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # Segment 1: Bajada
        df_bajada = df[(df['MARGEN'] > margen_medio) & (df['ROTACIÓN 28 DÍAS'] > 4)]
        targeta_segment("Oportunitat de Bajada", df_bajada, "#3182ce", "📉")
        
        # Segment 2: Subida
        umbral_bajo = margen_medio * 0.8
        df_subida = df[(df['MARGEN'] < umbral_bajo) & (df['ROTACIÓN 28 DÍAS'] <= 4) & (df['VENTAS 28 DÍAS'] > 0)]
        targeta_segment("Oportunitat de Subida", df_subida, "#38a169", "🚀")
        
        # Segment 3: Encallados
        df_encallados = df[(df['MARGEN'] < umbral_bajo) & (df['ROTACIÓN 28 DÍAS'] > 4)]
        targeta_segment("Productes Encallats (Crític)", df_encallados, "#e53e3e", "⚠️")

    # --- PESTANYA 2: TAULES DETALLADES ---
    with tab_detall:
        st.subheader("Llistats per a execució")
        sel_segment = st.selectbox("Tria el segment per descarregar llistat:", ["Bajada", "Subida", "Encallats", "Stock Crític"])
        
        if sel_segment == "Bajada":
            st.dataframe(df_bajada, use_container_width=True)
        elif sel_segment == "Subida":
            st.dataframe(df_subida, use_container_width=True)
        elif sel_segment == "Encallats":
            st.dataframe(df_encallados, use_container_width=True)

    # --- PESTANYA 3: MINDEREST (A PANTALLA COMPLETA) ---
    with tab_bi:
        st.info("💡 Per veure el BI correctament, recorda tenir la sessió de Power BI oberta en aquest navegador.")
        pbi_url = "https://app.powerbi.com/reportEmbed?reportId=6e710f08-a1c2-4e65-9a06-d8c9a41feec9&groupId=226eb868-3d09-4111-8c60-70919dedcb48&autoAuth=true"
        st.markdown(f'<iframe title="Minderest BI" width="100%" height="800" src="{pbi_url}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)

else:
    st.image("https://cdn.pixabay.com/photo/2016/06/03/13/57/digital-marketing-1433427_1280.jpg", use_container_width=True)
    st.warning("👈 Puja el fitxer per començar.")
