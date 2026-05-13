import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuració de la pàgina a pantalla completa
st.set_page_config(layout="wide", page_title="Deporvillage Pricing Master", page_icon="🎯")

# Estils per a les targetes i el disseny
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { font-size: 2rem; color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Pricing Strategy Hub & Brand Analysis")
st.markdown("---")

# 2. Barra lateral per a pujar l'Excel
with st.sidebar:
    st.header("📥 Carregar Dades")
    uploaded_file = st.file_uploader("Puja el fitxer de Snowflake", type=["csv", "xlsx"])

if uploaded_file:
    # Lògica per llegir Excel o CSV
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    df.columns = df.columns.str.upper().str.strip()
    margen_medio = df['MARGEN'].mean()
    marca_nom = df['MARCA'].iloc[0]

    # KPIs superiors
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vendes (28d)", f"{df['FACTURACIÓN 28 DÍAS'].sum():,.0f}€")
    c2.metric("Valor Stock", f"{df['VALOR STOCK INTERNO'].sum():,.0f}€")
    c3.metric("Marge Mig", f"{margen_medio:.2f}%")
    c4.metric("SKUs Analitzats", len(df))

    st.markdown("---")

    # DISTRIBUCIÓ: Esquerra (Anàlisi Colab) | Dreta (Power BI)
    col_l, col_r = st.columns([1.3, 1])

    with col_l:
        st.subheader(f"🔍 Anàlisi Marca: {marca_nom}")
        pestanyes = st.tabs(["📉 Baixar Preu", "📈 Pujar/Ajustar", "📦 Alertes Stock"])
        
        with pestanyes[0]:
            df_b = df[(df['MARGEN'] > margen_medio) & (df['ROTACIÓN 28 DÍAS'] > 4)]
            st.dataframe(df_b[['SKU', 'NOMBRE', 'MARGEN', 'ROTACIÓN 28 DÍAS']], use_container_width=True)
            
        with pestanyes[1]:
            umbral = margen_medio * 0.8
            df_s = df[(df['MARGEN'] < umbral) & (df['ROTACIÓN 28 DÍAS'] <= 4)]
            st.dataframe(df_s[['SKU', 'NOMBRE', 'MARGEN', 'ROTACIÓN 28 DÍAS']], use_container_width=True)
            
        with pestanyes[2]:
            df['COBERTURA'] = (df['STOCK INTERNO TOTAL'] + df['STOCK PENDIENTE 30D']) / df['VENTAS 28 DÍAS'].replace(0, 0.01)
            df_st = df[df['COBERTURA'] <= 1]
            st.warning(f"Hi ha {len(df_st)} SKUs en risc de trencament.")
            st.dataframe(df_st[['SKU', 'NOMBRE', 'COBERTURA']], use_container_width=True)

    with col_r:
        st.subheader("📊 Competidors (Minderest)")
        pbi_url = "https://app.powerbi.com/reportEmbed?reportId=6e710f08-a1c2-4e65-9a06-d8c9a41feec9&groupId=226eb868-3d09-4111-8c60-70919dedcb48&experience=power-bi"
        st.markdown(f'<iframe width="100%" height="700" src="{pbi_url}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)

else:
    st.info("👋 Puja el fitxer de Snowflake a la barra lateral per veure l'anàlisi.")
