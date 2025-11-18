import streamlit as st
import pandas as pd
from datetime import datetime, date

class TransactionManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_transaction_form(self):
        st.header("💸 Nova Transação")
        
        # Inicializar session state para controle
        if 'last_transaction_type' not in st.session_state:
            st.session_state.last_transaction_type = "income"
        
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Valor (R$)", 
                min_value=0.01, 
                step=0.01,
                format="%.2f",
                key="amount_input"
            )
            
            transaction_type = st.radio(
                "Tipo de Transação",
                ["income", "expense"],
                format_func=lambda x: "📈 Receita" if x == "income" else "📉 Despesa",
                horizontal=True,
                key="type_radio"
            )
            
            transaction_date = st.date_input(
                "Data",
                date.today(),
                key="date_input"
            )
        
        with col2:
            # Forçar atualização quando o tipo mudar
            if transaction_type != st.session_state.last_transaction_type:
                st.session_state.last_transaction_type = transaction_type
                st.rerun()
            
            # Obter categorias baseadas no tipo
            categories_df = self.db.get_categories(type=transaction_type)
            
            if not categories_df.empty:
                category_options = categories_df['name'].tolist()
                category_icons = categories_df.set_index('name')['icon'].to_dict()
                
                # Criar dropdown com ícones
                selected_category = st.selectbox(
                    "Categoria",
                    options=category_options,
                    format_func=lambda x: f"{category_icons.get(x, '💰')} {x}",
                    key=f"category_{transaction_type}"
                )
            else:
                st.error("❌ Nenhuma categoria encontrada")
                selected_category = ""
            
            description = st.text_input(
                "Descrição",
                placeholder="Ex: Salário mensal, Conta de luz...",
                key="description_input"
            )
        
        # Botão para adicionar
        if st.button("💾 Adicionar Transação", use_container_width=True, type="primary"):
            if amount > 0 and selected_category:
                try:
                    self.db.add_transaction(
                        float(amount), 
                        transaction_type, 
                        selected_category, 
                        description, 
                        transaction_date
                    )
                    st.success("✅ Transação adicionada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
            else:
                st.error("❌ Preencha valor e categoria")
    
    def show_transaction_history(self):
        st.header("📋 Histórico de Transações")
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_type = st.selectbox(
                "Tipo",
                ["Todos", "income", "expense"],
                format_func=lambda x: "Todos" if x == "Todos" else ("Receita" if x == "income" else "Despesa"),
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
            # Adicionar coluna de ações
            display_df = transactions.copy()
            display_df['Ações'] = "🗑️"
            
            # Formatar dados
            display_df['Tipo'] = display_df['type'].map({'income': '📈 Receita', 'expense': '📉 Despesa'})
            display_df['Valor'] = display_df['amount'].apply(lambda x: f"R$ {x:,.2f}")
            display_df['Data'] = display_df['date'].dt.strftime('%d/%m/%Y')
            display_df['Categoria'] = display_df['icon'] + ' ' + display_df['category']
            
            # Colunas para exibição
            display_columns = ['Data', 'Tipo', 'Categoria', 'Valor', 'description', 'Ações']
            
            # Mostrar tabela
            for idx, row in display_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 3, 1])
                
                with col1:
                    st.write(row['Data'])
                with col2:
                    st.write(row['Tipo'])
                with col3:
                    st.write(row['Categoria'])
                with col4:
                    st.write(row['Valor'])
                with col5:
                    st.write(row['description'] or "-")
                with col6:
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        if self.db.delete_transaction(row['id']):
                            st.success("✅ Transação excluída!")
                            st.rerun()
            
            # Estatísticas
            total_income = display_df[display_df['type'] == 'income']['amount'].sum()
            total_expense = display_df[display_df['type'] == 'expense']['amount'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("📈 Total Receitas", f"R$ {total_income:,.2f}")
            col2.metric("📉 Total Despesas", f"R$ {total_expense:,.2f}")
            
            # Exportar
            csv = transactions[['date', 'type', 'category', 'amount', 'description']].to_csv(index=False)
            st.download_button("📥 Exportar CSV", data=csv, file_name="transacoes.csv", mime="text/csv")
            
        else:
            st.info("📝 Nenhuma transação encontrada")