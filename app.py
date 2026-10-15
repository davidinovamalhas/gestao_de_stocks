import streamlit as st
import pandas as pd
import os

# Nome do ficheiro Excel que guardou na pasta
EXCEL_FILE = "base_dados_stock.xlsx"

# Função para carregar os dados do Excel
def carregar_dados():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        # Se o ficheiro não existir, cria um modelo com as suas colunas
        columns = ["Código", "Descrição", "Und", "Fornecedor", "Observações", "Armazém", "Stock atual", "Preço"]
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
        st.warning("O inventário está vazio. Adicione produtos no menu de Movimentos.")
    else:
        # Mostra a tabela interativa
        st.dataframe(df_stock, use_container_width=True)

# --- MENU 2: MOVIMENTOS ---
elif menu == "➕ Movimentos (Entrada/Saída)":
    st.header("Registar Entrada ou Saída")
    
    # Formulário para introduzir dados
    with st.form("form_movimento", clear_on_submit=True):
        codigo = st.text_input("Código do Produto")
        descricao = st.text_input("Descrição / Nome")
        und = st.selectbox("Unidade (Und)", ["Un", "Kg", "Cx", "Ltr"])
        fornecedor = st.text_input("Fornecedor")
        armazem = st.text_input("Armazém / Localização")
        preco = st.number_input("Preço (Opcional)", min_value=0.0, value=0.0, step=0.01)
        observacoes = st.text_area("Observações")
        
        tipo_movimento = Skinner = st.radio("Tipo de Movimento", ["Entrada (Adicionar)", "Saída (Remover)"])
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
        
        botao_submeter = st.form_submit_button("Confirmar Movimento")
        
    if botao_submeter:
        if not codigo or not descricao:
            st.error("Por favor, preencha pelo menos o Código e a Descrição.")
        else:
            # Verificar se o produto já existe no Excel
            idx = df_stock[df_stock["Código"].astype(str) == str(codigo)].index
            
            if len(idx) > 0:
                # Produto já existe, vamos atualizar o stock
                stock_atual = df_stock.loc[idx[0], "Stock atual"]
                if tipo_movimento == "Entrada (Adicionar)":
                    df_stock.loc[idx[0], "Stock atual"] = stock_atual + quantidade
                else:
                    df_stock.loc[idx[0], "Stock atual"] = max(0, stock_atual - quantity)
                
                # Atualiza preço e observações se foram preenchidos
                if preco > 0: df_stock.loc[idx[0], "Preço"] = preco
                if observacoes: df_stock.loc[idx[0], "Observações"] = observacoes
                
                st.success(f"Stock do produto '{descricao}' atualizado com sucesso!")
            else:
                # Produto novo, vamos adicionar uma nova linha
                if tipo_movimento == "Saída (Remover)":
                    st.error("Não pode dar saída de um produto que não existe no stock!")
                else:
                    nova_linha = {
                        "Código": codigo, "Descrição": descricao, "Und": und,
                        "Fornecedor": fornecedor, "Observações": observacoes,
                        "Armazém": armazem, "Stock atual": quantidade, "Preço": preco if preco > 0 else None
                    }
                    df_stock = pd.concat([df_stock, pd.DataFrame([nova_linha])], ignore_index=True)
                    st.success(f"Novo produto '{descricao}' registado com sucesso!")
            
            # Grava as alterações de volta no Excel automaticamente
            guardar_dados(df_stock)
