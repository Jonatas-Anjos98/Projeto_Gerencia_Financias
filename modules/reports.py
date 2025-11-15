import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class ReportGenerator:
    def __init__(self, db_manager, analytics):
        self.db = db_manager
        self.analytics = analytics
    
    def show_financial_reports(self):
        st.header("📈 Relatórios Financeiros")
        
        # Período de análise
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data Inicial",
                datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input("Data Final", datetime.now())
        
        # Resumo financeiro
        summary = self.db.get_financial_summary(start_date, end_date)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "💰 Saldo", 
                f"R$ {summary['balance']:,.2f}",
                delta=f"R$ {summary['balance']:,.2f}"
            )
        with col2:
            st.metric(
                "📈 Receitas", 
                f"R$ {summary['total_income']:,.2f}"
            )
        with col3:
            st.metric(
                "📉 Despesas", 
                f"R$ {summary['total_expense']:,.2f}"
            )
        with col4:
            st.metric(
                "🎯 Taxa de Economia", 
                f"{summary['savings_rate']:.1f}%"
            )
        
        # Gráficos
        monthly_data = self.db.get_monthly_summary()
        expense_by_category = self.db.get_category_analysis('expense')
        income_by_category = self.db.get_category_analysis('income')
        
        if not monthly_data.empty:
            # Gráficos de tendência
            col1, col2 = st.columns(2)
            
            with col1:
                trend_chart = self.analytics.create_monthly_trend_chart(monthly_data)
                st.plotly_chart(trend_chart, use_container_width=True)
            
            with col2:
                bar_chart = self.analytics.create_income_vs_expense_chart(monthly_data)
                st.plotly_chart(bar_chart, use_container_width=True)
            
            # Gráficos de pizza
            col3, col4 = st.columns(2)
            
            with col3:
                if not expense_by_category.empty:
                    expense_pie = self.analytics.create_expense_pie_chart(expense_by_category)
                    st.plotly_chart(expense_pie, use_container_width=True)
            
            with col4:
                if not income_by_category.empty:
                    income_pie = self.analytics.create_income_pie_chart(income_by_category)
                    st.plotly_chart(income_pie, use_container_width=True)
            
            # Gráficos de barras por categoria
            col5, col6 = st.columns(2)
            
            with col5:
                if not expense_by_category.empty:
                    expense_bar = self.analytics.create_category_bar_chart(expense_by_category, 'expense')
                    st.plotly_chart(expense_bar, use_container_width=True)
            
            with col6:
                if not income_by_category.empty:
                    income_bar = self.analytics.create_category_bar_chart(income_by_category, 'income')
                    st.plotly_chart(income_bar, use_container_width=True)
        
        else:
            st.info("📊 Adicione transações para visualizar os relatórios.")