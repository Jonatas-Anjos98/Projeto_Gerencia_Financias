import streamlit as st
import pandas as pd
from datetime import datetime

# Import dos módulos
from database import DatabaseManager
from modules.transactions import TransactionManager
from modules.categories import CategoryManager
from modules.reports import ReportGenerator
from modules.analytics import FinancialAnalytics

# Configuração da página
st.set_page_config(
    page_title="FinanceFlow - Gerenciador Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
    }
    .sidebar .sidebar-content {
        background-color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

class FinanceApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = FinancialAnalytics(self.db)
        self.transaction_manager = TransactionManager(self.db)
        self.category_manager = CategoryManager(self.db)
        self.report_generator = ReportGenerator(self.db, self.analytics)
    
    def run(self):
        # Header principal
        st.markdown('<h1 class="main-header">💸 FinanceFlow</h1>', unsafe_allow_html=True)
        st.markdown("### Seu gerenciador financeiro pessoal inteligente")
        
        # Sidebar com navegação
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=80)
            st.title("Navegação")
            
            menu_option = st.radio(
                "Selecione uma opção:",
                ["📊 Dashboard", "💸 Nova Transação", "📋 Histórico", "📈 Relatórios", "🏷️ Categorias", "ℹ️ Sobre"]
            )
            
            st.markdown("---")
            
            # Resumo rápido na sidebar
            summary = self.db.get_financial_summary()
            st.metric("💰 Saldo Atual", f"R$ {summary['balance']:,.2f}")
            st.metric("🎯 Economia", f"{summary['savings_rate']:.1f}%")
            
            st.markdown("---")
            st.markdown("*Desenvolvido com ❤️ usando Streamlit*")
        
        # Navegação entre páginas
        if menu_option == "📊 Dashboard":
            self.show_dashboard()
        elif menu_option == "💸 Nova Transação":
            self.transaction_manager.show_transaction_form()
        elif menu_option == "📋 Histórico":
            self.transaction_manager.show_transaction_history()
        elif menu_option == "📈 Relatórios":
            self.report_generator.show_financial_reports()
        elif menu_option == "🏷️ Categorias":
            self.category_manager.show_category_management()
        elif menu_option == "ℹ️ Sobre":
            self.show_about()
    
    def show_dashboard(self):
        st.header("📊 Dashboard Financeiro")
        
        # Métricas principais
        summary = self.db.get_financial_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "💰 Saldo Total", 
                f"R$ {summary['balance']:,.2f}",
                delta=f"R$ {summary['balance']:,.2f}" if summary['balance'] >= 0 else f"-R$ {abs(summary['balance']):,.2f}",
                delta_color="normal" if summary['balance'] >= 0 else "inverse"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📈 Total Receitas", f"R$ {summary['total_income']:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📉 Total Despesas", f"R$ {summary['total_expense']:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🎯 Taxa de Economia", f"{summary['savings_rate']:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráficos do dashboard
        monthly_data = self.db.get_monthly_summary()
        expense_by_category = self.db.get_category_analysis('expense')
        
        if not monthly_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de tendência
                trend_chart = self.analytics.create_monthly_trend_chart(monthly_data)
                st.plotly_chart(trend_chart, use_container_width=True)
            
            with col2:
                # Gráfico de pizza de gastos
                if not expense_by_category.empty:
                    pie_chart = self.analytics.create_expense_pie_chart(expense_by_category)
                    st.plotly_chart(pie_chart, use_container_width=True)
            
            # Últimas transações
            st.subheader("📝 Últimas Transações")
            recent_transactions = self.db.get_transactions(limit=10)
            
            if not recent_transactions.empty:
                display_df = recent_transactions.copy()
                display_df['type_display'] = display_df['type'].map({
                    'income': '📈', 
                    'expense': '📉'
                })
                display_df['amount_display'] = display_df['amount'].apply(
                    lambda x: f"R$ {x:,.2f}"
                )
                display_df['date_display'] = display_df['date'].dt.strftime('%d/%m/%Y')
                
                st.dataframe(
                    display_df[['date_display', 'type_display', 'category', 'amount_display', 'description']],
                    column_config={
                        'date_display': 'Data',
                        'type_display': 'Tipo',
                        'category': 'Categoria',
                        'amount_display': 'Valor',
                        'description': 'Descrição'
                    },
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("🎉 Bem-vindo ao FinanceFlow! Adicione sua primeira transação para começar.")
            
            # Cards de instrução
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background-color: #f0f9ff; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #3b82f6;'>
                    <h3>📝 Primeiros Passos</h3>
                    <p>1. Vá em <b>Nova Transação</b></p>
                    <p>2. Adicione suas receitas e despesas</p>
                    <p>3. Acompanhe seus gastos</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown