import streamlit as st
import pandas as pd
import os

# Nome do ficheiro Excel
EXCEL_FILE = "base_dados_stock.xlsx"

# Função para carregar os dados do Excel
def carregar_dados():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        # Garante que a coluna Artigo existe e não tem valores em branco escondidos
        if "Artigo" in df.columns:
            df["Artigo"] = df["Artigo"].astype(str).str.strip()
        return df
    else:
        # Nova estrutura sem Código e com Artigo
        columns = ["Artigo", "Und", "Fornecedor", "Observações", "Armazém", "Stock atual", "Preço"]
        return pd.DataFrame(columns=columns)

# Função para guardar os dados no Excel
def guardar_dados(df):
    df.to_excel(EXCEL_FILE, index=False)

# Configuração da página da App
st.set_page_config(page_title="Gestão de Stock", layout="wide")
st.title("📦 Sistema de Gestão de Stocks")

df_stock = carregar_dados()

# Menu lateral para navegação
menu = st.sidebar.radio("Navegação", ["📋 Listagem de Stock", "➕ Movimentos (Entrada/Saída)"])

# --- MENU 1: LISTAGEM ---
if menu == "📋 Listagem de Stock":
    st.header("Stock Atual")
    if df_stock.empty:
        st.warning("O inventário está vazio. Adicione artigos no menu de Movimentos.")
    else:
        st.dataframe(df_stock, use_container_width=True)

# --- MENU 2: MOVIMENTOS ---
elif menu == "➕ Movimentos (Entrada/Saída)":
    st.header("Registar Entrada ou Saída")
    
    # Obter a lista de artigos que já existem no Excel para a caixa de seleção
    artigos_existentes = []
    if not df_stock.empty and "Artigo" in df_stock.columns:
        # Pega nos artigos, remove duplicados e ordena de A-Z
        artigos_existentes = sorted(df_stock["Artigo"].unique().tolist())
    
    # Opção para o utilizador escolher se é um artigo novo ou existente
    tipo_artigo = st.radio("O artigo já existe no sistema?", ["Sim, selecionar da lista", "Não, é um artigo novo"])
    
    # Formulário para introduzir dados
    with st.form("form_movimento", clear_on_submit=True):
        
        # Se o artigo já existe, mostra uma lista de seleção (Dropdown)
        if tipo_artigo == "Sim, selecionar da lista":
            if len(artigos_existentes) == 0:
                st.info("Ainda não existem artigos registados. Escolha a opção 'Artigo novo'.")
                artigo_final = ""
            else:
                artigo_final = st.selectbox("Selecione o Artigo", artigos_existentes)
        else:
            # Se for novo, abre uma caixa de texto para ele escrever
            artigo_final = st.text_input("Nome do Novo Artigo").strip()
            
        und = st.selectbox("Unidade (Und)", ["Un", "Kg", "Cx", "Ltr"])
        fornecedor = st.text_input("Fornecedor")
        armazem = st.text_input("Armazém / Localização")
        preco = st.number_input("Preço (Opcional)", min_value=0.0, value=0.0, step=0.01)
        observacoes = st.text_area("Observações")
        
        tipo_movimento = st.radio("Tipo de Movimento", ["Entrada (Adicionar)", "Saída (Remover)"])
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
        
        botao_submeter = st.form_submit_button("Confirmar Movimento")
        
    if botao_submeter:
        if not artigo_final:
            st.error("Por favor, selecione ou introduza o nome do Artigo.")
        else:
            # Verificar se o artigo já existe na base de dados (pesquisa por texto exato)
            idx = df_stock[df_stock["Artigo"].astype(str) == str(artigo_final)].index
            
            if len(idx) > 0:
                # O artigo já existe, vamos atualizar o stock daquela linha
                stock_anterior = df_stock.loc[idx[0], "Stock atual"]
                
                # Se a célula estiver vazia no Excel por algum motivo, assume 0
                if pd.isna(stock_anterior): stock_anterior = 0
                
                if tipo_movimento == "Entrada (Adicionar)":
                    df_stock.loc[idx[0], "Stock atual"] = stock_anterior + quantidade
                    st.success(f"Entrada registada! Novo stock de '{artigo_final}': {stock_anterior + quantidade}")
                else:
                    if stock_anterior < quantidade:
                        st.error(f"Erro: Stock insuficiente! Só tem {stock_anterior} unidades de '{artigo_final}' em armazém.")
                    else:
                        df_stock.loc[idx[0], "Stock atual"] = stock_anterior - quantidade
                        st.success(f"Saída registada! Novo stock de '{artigo_final}': {stock_anterior - quantidade}")
                
                # Atualiza os dados opcionais se o utilizador preencheu algo novo
                if fornecedor: df_stock.loc[idx[0], "Fornecedor"] = fornecedor
                if armazem: df_stock.loc[idx[0], "Armazém"] = armazem
                if preco > 0: df_stock.loc[idx[0], "Preço"] = preco
                if observacoes: df_stock.loc[idx[0], "Observações"] = observacoes
                
            else:
                # É um artigo novo na base de dados
                if tipo_movimento == "Saída (Remover)":
                    st.error("Não pode dar saída de um artigo que nunca foi registado!")
                else:
                    nova_linha = {
                        "Artigo": artigo_final, "Und": und, "Fornecedor": fornecedor, 
                        "Observações": observacoes, "Armazém": armazem, 
                        "Stock atual": quantidade, "Preço": preco if preco > 0 else None
                    }
                    df_stock = pd.concat([df_stock, pd.DataFrame([nova_linha])], ignore_index=True)
                    st.success(f"Novo artigo '{artigo_final}' registado e adicionado ao stock!")
            
            # Grava as alterações no Excel
            guardar_dados(df_stock)
