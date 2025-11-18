import streamlit as st
from database import DatabaseManager
from modules.transactions import TransactionManager
from modules.categories import CategoryManager
from modules.reports import ReportGenerator
from modules.analytics import FinancialAnalytics
from auth import AuthManager

# Configuração
st.set_page_config(page_title="FinanceFlow", page_icon="💰", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# Inicializar gerenciadores
auth = AuthManager()

# Verificar se está logado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth.show_login_form()
    st.stop()

# App principal (só executa se estiver logado)
db = DatabaseManager()
analytics = FinancialAnalytics(db)
transaction_manager = TransactionManager(db)
category_manager = CategoryManager(db)
report_generator = ReportGenerator(db, analytics)

class FinanceApp:
    def run(self):
        st.sidebar.title(f"👋 Olá, {st.session_state.username}!")
        
        if st.sidebar.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.rerun()
        
        menu = st.sidebar.radio("Navegação", [
            "📊 Dashboard", "💸 Nova Transação", "📋 Histórico", 
            "📈 Relatórios", "🏷️ Categorias"
        ])
        
        if menu == "📊 Dashboard":
            self.show_dashboard()
        elif menu == "💸 Nova Transação":
            # Verificar se está editando
            if not transaction_manager.show_edit_form():
                transaction_manager.show_transaction_form()
        elif menu == "📋 Histórico":
            # Verificar se está editando
            if not transaction_manager.show_edit_form():
                transaction_manager.show_transaction_history()
        elif menu == "📈 Relatórios":
            report_generator.show_financial_reports()
        elif menu == "🏷️ Categorias":
            category_manager.show_category_management()
    
    def show_dashboard(self):
        st.header("📊 Dashboard Financeiro")
        
        # Métricas principais
        summary = db.get_financial_summary()
        
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
        monthly_data = db.get_monthly_summary()
        expense_by_category = db.get_category_analysis('expense')
        
        if not monthly_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de tendência
                trend_chart = analytics.create_monthly_trend_chart(monthly_data)
                st.plotly_chart(trend_chart, use_container_width=True)
            
            with col2:
                # Gráfico de pizza de gastos
                if not expense_by_category.empty:
                    pie_chart = analytics.create_expense_pie_chart(expense_by_category)
                    st.plotly_chart(pie_chart, use_container_width=True)
            
            # Últimas transações
            st.subheader("📝 Últimas Transações")
            recent_transactions = db.get_transactions(limit=10)
            
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
                <div style='background-color: #1E40AF; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #3B82F6;'>
                    <h3 style='color: white;'>📝 Primeiros Passos</h3>
                    <p style='color: white;'>1. Vá em <b>Nova Transação</b></p>
                    <p style='color: white;'>2. Adicione suas receitas e despesas</p>
                    <p style='color: white;'>3. Acompanhe seus gastos</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background-color: #047857; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #10B981;'>
                    <h3 style='color: white;'>📊 Visualizações</h3>
                    <p style='color: white;'>• Gráficos interativos</p>
                    <p style='color: white;'>• Relatórios detalhados</p>
                    <p style='color: white;'>• Análise por categoria</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background-color: #B45309; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #F59E0B;'>
                    <h3 style='color: white;'>🎯 Metas</h3>
                    <p style='color: white;'>• Controle financeiro</p>
                    <p style='color: white;'>• Economia inteligente</p>
                    <p style='color: white;'>• Planejamento futuro</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = FinanceApp()
    app.run()