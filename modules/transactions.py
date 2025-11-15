import streamlit as st
import pandas as pd
from datetime import datetime, date

class TransactionManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_transaction_form(self):
        st.header("💸 Nova Transação")
        
        with st.form("transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input(
                    "Valor (R$)", 
                    min_value=0.01, 
                    step=0.01,
                    format="%.2f",
                    help="Digite o valor da transação"
                )
                
                transaction_type = st.radio(
                    "Tipo de Transação",
                    ["income", "expense"],
                    format_func=lambda x: "📈 Receita" if x == "income" else "📉 Despesa",
                    horizontal=True
                )
                
                transaction_date = st.date_input(
                    "Data",
                    date.today(),
                    help="Data da transação"
                )
            
            with col2:
                # Obter categorias baseadas no tipo
                categories_df = self.db.get_categories(type=transaction_type)
                category_options = categories_df['name'].tolist()
                category_icons = categories_df.set_index('name')['icon'].to_dict()
                
                # Formatar opções com ícones
                formatted_categories = [
                    f"{category_icons.get(cat, '💰')} {cat}" 
                    for cat in category_options
                ]
                
                selected_category_formatted = st.selectbox(
                    "Categoria",
                    formatted_categories,
                    help="Selecione a categoria da transação"
                )
                
                # Extrair nome da categoria sem o ícone
                selected_category = selected_category_formatted.split(' ', 1)[1]
                
                description = st.text_input(
                    "Descrição",
                    placeholder="Ex: Salário mensal, Conta de luz...",
                    help="Descrição opcional da transação"
                )
            
            submitted = st.form_submit_button(
                "💾 Adicionar Transação",
                use_container_width=True
            )
            
            if submitted:
                if amount > 0 and selected_category:
                    try:
                        self.db.add_transaction(
                            amount, 
                            transaction_type, 
                            selected_category, 
                            description, 
                            transaction_date
                        )
                        st.success("✅ Transação adicionada com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao adicionar transação: {e}")
                else:
                    st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    def show_transaction_history(self):
        st.header("📋 Histórico de Transações")
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_type = st.selectbox(
                "Tipo",
                ["Todos", "income", "expense"],
                format_func=lambda x: "Todos" if x == "Todos" else ("Receita" if x == "income" else "Despesa")
            )
        
        with col2:
            categories = self.db.get_categories()
            category_options = ["Todas"] + categories['name'].tolist()
            filter_category = st.selectbox("Categoria", category_options)
        
        with col3:
            filter_start_date = st.date_input("Data Inicial")
        
        with col4:
            filter_end_date = st.date_input("Data Final")
        
        # Aplicar filtros
        filters = {}
        if filter_type != "Todos":
            filters['type'] = filter_type
        if filter_category != "Todas":
            filters['category'] = filter_category
        if filter_start_date:
            filters['start_date'] = filter_start_date
        if filter_end_date:
            filters['end_date'] = filter_end_date
        
        # Obter transações
        transactions = self.db.get_transactions(filters=filters)
        
        if not transactions.empty:
            # Formatar dados para exibição
            display_df = transactions.copy()
            display_df['type_display'] = display_df['type'].map({
                'income': '📈 Receita', 
                'expense': '📉 Despesa'
            })
            display_df['amount_display'] = display_df['amount'].apply(
                lambda x: f"R$ {x:,.2f}"
            )
            display_df['date_display'] = display_df['date'].dt.strftime('%d/%m/%Y')
            display_df['category_display'] = display_df['icon'] + ' ' + display_df['category']
            
            # Colunas para exibição
            display_columns = [
                'date_display', 'type_display', 'category_display', 
                'amount_display', 'description'
            ]
            
            st.dataframe(
                display_df[display_columns],
                column_config={
                    'date_display': 'Data',
                    'type_display': 'Tipo',
                    'category_display': 'Categoria',
                    'amount_display': 'Valor',
                    'description': 'Descrição'
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Estatísticas rápidas
            total_income = display_df[display_df['type'] == 'income']['amount'].sum()
            total_expense = display_df[display_df['type'] == 'expense']['amount'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("📈 Total Receitas", f"R$ {total_income:,.2f}")
            col2.metric("📉 Total Despesas", f"R$ {total_expense:,.2f}")
            
            # Opção de exportar
            csv = transactions[['date', 'type', 'category', 'amount', 'description']].to_csv(index=False)
            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name="transacoes.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        else:
            st.info("📝 Nenhuma transação encontrada com os filtros selecionados.")