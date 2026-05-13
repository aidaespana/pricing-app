import streamlit as st
import pandas as pd
import numpy as np

# 1. CONFIGURACIÓ DE LA PÀGINA (Pantalla completa i títol al navegador)
st.set_page_config(
    layout="wide", 
    page_title="Deporvillage | Pricing Hub", 
    page_icon="🎯"
)

# 2. ESTILS CSS PER A L'ESTÈTICA DE "SINGLE PAGE APP"
st.markdown("""
    <style>
    /* Fons de l'app */
    .main { background-color: #f8fafc; }
    
    /* Targetes de mètriques */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Títols de les seccions */
    h1, h2, h3 { color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Botó de la sidebar */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #2563eb;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CAPÇALERA PRINCIPAL
st.title("🎯 Brand Strategy & Pricing Dashboard")
st.markdown("Anàlisi de dades internes fusionat amb intel·ligència competitiva (Minderest).")
st.divider()

# 4. BARRA LATERAL (SIDEBAR)
with st.sidebar:
    st.image("https://www.deporvillage.com/static/version1677587740/frontend/Deporvillage/default/es_ES/images/logo.svg", width=180)
    st.header("⚙️ Configuració")
    uploaded_file = st.file_uploader("Puja l'Excel de Snowflake", type=["xlsx", "csv"])
    
    st.divider()
    st.markdown("### 💡 Instruccions")
    st.caption("1. Exporta les dades de Snowflake.")
    st.caption("2. Puja el fitxer aquí.")
    st.caption("3. Revisa les recomanacions i compara amb el BI.")

# 5. LÒGICA PRINCIPAL (Només s'executa si hi ha fitxer)
if uploaded_file:
    # Lectura de dades
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # Neteja de columnes (per si venen amb espais o minúscules)
        df.columns = df.columns.str.upper().str.strip()
        
        # Càlculs base
        marge_mig = df['MARGEN'].mean()
        vendes_totals = df['FACTURACIÓN 28 DÍAS'].sum()
        stock_valor = df['VALOR STOCK INTERNO'].sum()
        marca = df['MARCA'].iloc[0] if 'MARCA' in df.columns else "Marca Seleccionada"

        # --- FILA 1: KPIs (TARGETES) ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vendes (28d)", f"{vendes_totals:,.0f} €")
        col2.metric("Valor Stock", f"{stock_valor:,.0f} €")
        col3.metric("Marge Mig", f"{marge_mig:.2f} %")
        col4.metric("SKUs Totals", len(df))

        st.markdown("---")

        # --- FILA 2: DISTRIBUCIÓ EN DUES COLUMNES ---
        col_esquerra, col_dreta = st.columns([1.2, 1])

        # COLUMNA ESQUERRA: ANÀLISI INTERN (ESTIL COLAB)
        with col_esquerra:
            st.subheader(f"🔍 Anàlisi Estratègic: {marca}")
            
            tabs = st.tabs(["📉 Baixar Preu", "📈 Pujar/Ajustar", "📦 Stock Crític"])
            
            with tabs[0]: # Lògica per baixar preu
                df_bajada = df[(df['MARGEN'] > marge_mig) & (df['ROTACIÓN 28 DÍAS'] > 4)]
                st.write("SKUs amb marge alt i bona rotació (Candidats a guanyar share):")
                st.dataframe(df_bajada[['SKU', 'NOMBRE', 'MARGEN', 'ROTACIÓN 28 DÍAS']], use_container_width=True)
                
            with tabs[1]: # Lògica per pujar o revisar
                umbral_bajo = marge_mig * 0.8
                df_subida = df[(df['MARGEN'] < umbral_bajo) & (df['ROTACIÓN 28 DÍAS'] <= 4)]
                st.write("SKUs amb marge molt baix i rotació lenta:")
                st.dataframe(df_subida[['SKU', 'NOMBRE', 'MARGEN', 'ROTACIÓN 28 DÍAS']], use_container_width=True)
                
            with tabs[2]: # Lògica de cobertura
                df['COBERTURA'] = (df['STOCK INTERNO TOTAL'] + df['STOCK PENDIENTE 30D']) / df['VENTAS 28 DÍAS'].replace(0, 0.01)
                df_riesgo = df[df['COBERTURA'] <= 1]
                st.error(f"⚠️ {len(df_riesgo)} productes amb risc de trencament (cobertura < 1 mes).")
                st.dataframe(df_riesgo[['SKU', 'NOMBRE', 'COBERTURA']], use_container_width=True)

        # COLUMNA DRETA: MINDEREST BI
        with col_dreta:
            st.subheader("📊 Competidors (Minderest)")
            # Nota: L'iframe de Power BI necessita autoAuth=true per intentar loguejar-se sol
            pbi_url = "https://app.powerbi.com/reportEmbed?reportId=6e710f08-a1c2-4e65-9a06-d8c9a41feec9&groupId=226eb868-3d09-4111-8c60-70919dedcb48&autoAuth=true"
            
            st.markdown(f"""
                <iframe title="Minderest" width="100%" height="750" 
                src="{pbi_url}" frameborder="0" allowFullScreen="true"
                style="border-radius: 12px; border: 1px solid #e2e8f0;"></iframe>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"S'ha produït un error en processar el fitxer: {e}")
        st.info("Assegura't que les columnes de l'Excel coincideixen amb les de l'anàlisi.")

else:
    # Pantalla d'inici quan no hi ha dades
    st.image("https://cdn.pixabay.com/photo/2016/06/03/13/57/digital-marketing-1433427_1280.jpg", use_container_width=True)
    st.info("👈 Puja el fitxer de Snowflake des de la barra lateral per començar l'anàlisi.")
