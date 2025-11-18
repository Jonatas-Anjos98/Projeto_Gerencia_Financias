import streamlit as st
import pandas as pd
from datetime import datetime, date

class TransactionManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_transaction_form(self, edit_transaction=None):
        st.header("💸 Nova Transação" if not edit_transaction else "✏️ Editar Transação")
        
        # Valores padrão para edição
        default_amount = edit_transaction['amount'] if edit_transaction else 0.01
        default_type = edit_transaction['type'] if edit_transaction else "income"
        default_category = edit_transaction['category'] if edit_transaction else ""
        default_description = edit_transaction['description'] if edit_transaction else ""
        default_date = edit_transaction['date'] if edit_transaction else date.today()
        
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                "Valor (R$)", 
                min_value=0.01, 
                step=0.01,
                format="%.2f",
                value=float(default_amount),
                key="amount_input"
            )
            
            transaction_type = st.radio(
                "Tipo de Transação",
                ["income", "expense"],
                index=0 if default_type == "income" else 1,
                format_func=lambda x: "📈 Receita" if x == "income" else "📉 Despesa",
                horizontal=True,
                key="type_radio"
            )
            
            transaction_date = st.date_input(
                "Data",
                value=default_date,
                key="date_input"
            )
        
        with col2:
            # Obter categorias baseadas no tipo
            categories_df = self.db.get_categories(type=transaction_type)
            
            if not categories_df.empty:
                category_options = categories_df['name'].tolist()
                category_icons = categories_df.set_index('name')['icon'].to_dict()
                
                # Encontrar índice da categoria atual para seleção
                default_index = category_options.index(default_category) if default_category in category_options else 0
                
                selected_category = st.selectbox(
                    "Categoria",
                    options=category_options,
                    index=default_index,
                    format_func=lambda x: f"{category_icons.get(x, '💰')} {x}",
                    key=f"category_{transaction_type}"
                )
            else:
                st.error("❌ Nenhuma categoria encontrada")
                selected_category = ""
            
            description = st.text_input(
                "Descrição",
                value=default_description,
                placeholder="Ex: Salário mensal, Conta de luz...",
                key="description_input"
            )
        
        # Botões de ação
        col1, col2 = st.columns(2)
        
        with col1:
            if edit_transaction:
                if st.button("💾 Atualizar Transação", use_container_width=True, type="primary"):
                    if amount > 0 and selected_category:
                        try:
                            if self.update_transaction(
                                edit_transaction['id'],
                                float(amount), 
                                transaction_type, 
                                selected_category, 
                                description, 
                                transaction_date
                            ):
                                st.success("✅ Transação atualizada com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao atualizar transação")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                    else:
                        st.error("❌ Preencha valor e categoria")
            else:
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
        
        with col2:
            if st.button("🗑️ Cancelar", use_container_width=True):
                st.rerun()
    
    def update_transaction(self, transaction_id, amount, type, category, description, date):
        """Atualiza uma transação existente"""
        try:
            conn = self.db.conn
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions 
                SET amount = ?, type = ?, category = ?, description = ?, date = ?
                WHERE id = ?
            ''', (amount, type, category, description, date, transaction_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Erro ao atualizar: {e}")
            return False
    
    def show_transaction_history(self):
        st.header("📋 Histórico de Transações")
        
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_type = st.selectbox(
                "Tipo",
                ["Todos", "income", "expense"],
                format_func=lambda x: "Todos" if x == "Todos" else ("Receita" if x == "income" else "Despesa"),
                key="filter_type"
            )
        
        with col2:
            categories = self.db.get_categories()
            category_options = ["Todas"] + categories['name'].tolist()
            filter_category = st.selectbox("Categoria", category_options, key="filter_category")
        
        with col3:
            filter_start_date = st.date_input("Data Inicial", key="start_date")
        
        with col4:
            filter_end_date = st.date_input("Data Final", key="end_date")
        
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
            # Mostrar estatísticas
            total_income = transactions[transactions['type'] == 'income']['amount'].sum()
            total_expense = transactions[transactions['type'] == 'expense']['amount'].sum()
            balance = total_income - total_expense
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Total Receitas", f"R$ {total_income:,.2f}")
            col2.metric("📉 Total Despesas", f"R$ {total_expense:,.2f}")
            col3.metric("💰 Saldo", f"R$ {balance:,.2f}")
            
            st.markdown("---")
            
            # Tabela de transações com ações
            for idx, row in transactions.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 2, 2, 3, 2])
                    
                    with col1:
                        st.write(f"**{row['date'].strftime('%d/%m/%Y')}**")
                    
                    with col2:
                        if row['type'] == 'income':
                            st.success("📈 Receita")
                        else:
                            st.error("📉 Despesa")
                    
                    with col3:
                        st.write(f"{row['icon']} {row['category']}")
                    
                    with col4:
                        st.write(f"**R$ {row['amount']:,.2f}**")
                    
                    with col5:
                        st.write(row['description'] or "-")
                    
                    with col6:
                        subcol1, subcol2 = st.columns(2)
                        with subcol1:
                            if st.button("✏️", key=f"edit_{row['id']}", help="Editar"):
                                st.session_state.editing_transaction = {
                                    'id': row['id'],
                                    'amount': row['amount'],
                                    'type': row['type'],
                                    'category': row['category'],
                                    'description': row['description'],
                                    'date': row['date']
                                }
                                st.rerun()
                        
                        with subcol2:
                            if st.button("🗑️", key=f"delete_{row['id']}", help="Excluir"):
                                if self.db.delete_transaction(row['id']):
                                    st.success("✅ Transação excluída!")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao excluir transação")
            
            # Exportar dados
            st.markdown("---")
            csv = transactions[['date', 'type', 'category', 'amount', 'description']].to_csv(index=False)
            st.download_button(
                "📥 Exportar CSV", 
                data=csv, 
                file_name="transacoes.csv", 
                mime="text/csv",
                use_container_width=True
            )
            
        else:
            st.info("📝 Nenhuma transação encontrada com os filtros selecionados")
    
    def show_edit_form(self):
        """Mostra formulário de edição se houver transação para editar"""
        if 'editing_transaction' in st.session_state:
            self.show_transaction_form(st.session_state.editing_transaction)
            
            # Botão para cancelar edição
            if st.button("❌ Cancelar Edição"):
                del st.session_state.editing_transaction
                st.rerun()
            return True
        return False