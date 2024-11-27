import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def gerar_arquivo_fluxo(df_filtrado):
    # Função para criar o resumo e exportar como arquivo Excel
    resumo_detalhado = df_filtrado.groupby(['Tipo de unidade, segundo o município informante', 'UF'])[
        ['Dom+Pub', 'Entulho', 'Podas', 'Saúde', 'Outros']
    ].sum().reset_index()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resumo_detalhado.to_excel(writer, index=False, sheet_name="Resumo por Unidade e UF")
        worksheet = writer.sheets["Resumo por Unidade e UF"]
        for i, width in enumerate([20] * resumo_detalhado.shape[1]):
            worksheet.set_column(i, i, width)
    output.seek(0)
    return output

# Configurações iniciais da página
st.set_page_config(page_title="Análise de Resíduos", layout="wide")
st.title("Análise de Gestão de Resíduos")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue sua tabela", type=["xlsx", "csv"])

if uploaded_file:
    # Carregar arquivo com base na extensão
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    st.write("Tabela carregada:")
    st.write(df)

    # Seleção de filtros
    tipos_unidade = st.multiselect("Escolha os Tipos de Unidade", df['Tipo de unidade, segundo o município informante'].unique())
    ufs = st.multiselect("Escolha os Estados (UF)", df['UF'].unique())

    if tipos_unidade and ufs:
        # Filtrar os dados com base nos filtros selecionados
        df_filtrado = df[
            (df['Tipo de unidade, segundo o município informante'].isin(tipos_unidade)) & 
            (df['UF'].isin(ufs))
        ]

        # Resumo dos dados
        composicao_total = df_filtrado[['Dom+Pub', 'Entulho', 'Podas', 'Saúde', 'Outros']].sum()
        total_residuos = composicao_total.sum()

        # Criar abas para diferentes visualizações
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Visão Geral Nacional", "Comparação entre UFs", 
            "Destinação de Resíduos por Unidade", "Projeções e Cenários", "Educação e Boas Práticas"
        ])

        with tab1:
            st.subheader("Indicadores-Chave")
            st.metric("Total de Resíduos (ton)", f"{total_residuos:,.2f}")
            st.metric("Tipo de Resíduo Predominante", composicao_total.idxmax())
            
            st.subheader("Distribuição de Resíduos por UF")
            resumo_por_uf = df_filtrado.groupby(['UF'])[['Dom+Pub', 'Entulho', 'Podas', 'Saúde', 'Outros']].sum()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(resumo_por_uf, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=0.5, ax=ax)
            ax.set_title("Mapa de Calor da Geração de Resíduos por UF")
            st.pyplot(fig)

        with tab2:
            st.subheader("Comparação entre UFs")
            fig, ax = plt.subplots(figsize=(12, 8))
            resumo_por_uf.plot(kind='bar', stacked=True, ax=ax, color=['#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#FFC107'])
            ax.set_title("Distribuição de Resíduos por Tipo e UF")
            ax.set_xlabel("UF")
            ax.set_ylabel("Massa (toneladas)")
            ax.legend(title="Tipo de Resíduo")
            st.pyplot(fig)

        with tab3:
            st.subheader("Destinação de Resíduos por Unidade")
            for unidade in tipos_unidade:
                unidade_df = df_filtrado[df_filtrado['Tipo de unidade, segundo o município informante'] == unidade]
                resumo_unidade = unidade_df.groupby('UF')[['Dom+Pub', 'Entulho', 'Podas', 'Saúde', 'Outros']].sum()

                fig, ax = plt.subplots(figsize=(10, 6))
                resumo_unidade.plot(kind='bar', stacked=True, ax=ax, color=['#4CAF50', '#FF9800', '#9C27B0', '#00BCD4', '#FFC107'])
                ax.set_title(f"Destinação de Resíduos por UF para '{unidade}'")
                ax.set_xlabel("UF")
                ax.set_ylabel("Massa (toneladas)")
                ax.legend(title="Tipo de Resíduo")
                st.pyplot(fig)

        with tab4:
            st.subheader("Projeções e Cenários")
            st.write("Projeções futuras baseadas nos dados fornecidos.")

        with tab5:
            st.subheader("Educação e Boas Práticas")
            st.write("Sugestões de boas práticas para gestão de resíduos.")

        # Botão para download do arquivo Excel
        arquivo_fluxo = gerar_arquivo_fluxo(df_filtrado)
        st.download_button(
            label="Baixar Resumo em XLSX",
            data=arquivo_fluxo,
            file_name="resumo_fluxo_residuos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Selecione pelo menos um Tipo de Unidade e um Estado (UF).")
