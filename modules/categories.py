import streamlit as st
import pandas as pd

class CategoryManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_category_management(self):
        st.header("🏷️ Gerenciar Categorias")
        
        # Mostrar categorias existentes
        categories = self.db.get_categories()
        
        if not categories.empty:
            st.subheader("Categorias Existentes")
            
            # Dividir em receitas e despesas
            income_categories = categories[categories['type'] == 'income']
            expense_categories = categories[categories['type'] == 'expense']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Receitas")
                for _, cat in income_categories.iterrows():
                    st.markdown(f"{cat['icon']} **{cat['name']}**")
            
            with col2:
                st.markdown("### 📉 Despesas")
                for _, cat in expense_categories.iterrows():
                    st.markdown(f"{cat['icon']} **{cat['name']}**")
        
        # Adicionar nova categoria
        st.subheader("Adicionar Nova Categoria")
        
        with st.form("new_category_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_name = st.text_input("Nome da Categoria")
            with col2:
                category_type = st.selectbox("Tipo", ["income", "expense"])
            with col3:
                category_icon = st.selectbox("Ícone", ["💰", "💼", "👨‍💻", "📈", "🎁", "🍕", "🚗", "🏠", "🎮", "🏥", "📚", "🛍️", "💸"])
            
            submitted = st.form_submit_button("Adicionar Categoria")
            
            if submitted:
                if category_name and category_type and category_icon:
                    # Em uma versão futura, implementar adição de categorias
                    st.success("🎉 Funcionalidade de adição de categorias em desenvolvimento!")
                else:
                    st.error("Por favor, preencha todos os campos.")