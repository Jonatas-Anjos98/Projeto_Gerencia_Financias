import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class FinancialAnalytics:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_income_vs_expense_chart(self, monthly_data):
        if monthly_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Garantir que os dados são arrays/lists
        fig.add_trace(go.Bar(
            name='Receitas',
            x=monthly_data['month'].tolist(),
            y=monthly_data.get('income', pd.Series([0] * len(monthly_data))).tolist(),
            marker_color='#22c55e',
            opacity=0.8
        ))
        
        fig.add_trace(go.Bar(
            name='Despesas',
            x=monthly_data['month'].tolist(),
            y=monthly_data.get('expense', pd.Series([0] * len(monthly_data))).tolist(),
            marker_color='#ef4444',
            opacity=0.8
        ))
        
        fig.add_trace(go.Scatter(
            name='Saldo',
            x=monthly_data['month'].tolist(),
            y=monthly_data['balance'].tolist(),
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Receitas vs Despesas Mensais',
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            yaxis2=dict(
                title='Saldo (R$)',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            barmode='group',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937')
        )
        
        return fig
    
    def create_expense_pie_chart(self, category_data):
        if category_data.empty:
            return go.Figure()
        
        fig = px.pie(
            category_data,
            values='total_amount',
            names='category',
            title='Distribuição de Gastos por Categoria',
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=['total_amount']
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937'),
            showlegend=False
        )
        
        return fig
    
    def create_income_pie_chart(self, category_data):
        if category_data.empty:
            return go.Figure()
        
        fig = px.pie(
            category_data,
            values='total_amount',
            names='category',
            title='Distribuição de Receitas por Categoria',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data=['total_amount']
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937'),
            showlegend=False
        )
        
        return fig
    
    def create_monthly_trend_chart(self, monthly_data):
        if monthly_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Converter para listas para garantir que são arrays
        months = monthly_data['month'].tolist()
        income_data = monthly_data.get('income', pd.Series([0] * len(monthly_data))).tolist()
        expense_data = monthly_data.get('expense', pd.Series([0] * len(monthly_data))).tolist()
        balance_data = monthly_data['balance'].tolist()
        
        fig.add_trace(go.Scatter(
            name='Receitas',
            x=months,
            y=income_data,
            mode='lines+markers',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            name='Despesas',
            x=months,
            y=expense_data,
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            name='Saldo',
            x=months,
            y=balance_data,
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3, dash='dot'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Tendência Mensal - Receitas, Despesas e Saldo',
            xaxis_title='Mês',
            yaxis_title='Valor (R$)',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_category_bar_chart(self, category_data, type='expense'):
        if category_data.empty:
            return go.Figure()
        
        title = 'Gastos por Categoria' if type == 'expense' else 'Receitas por Categoria'
        color = '#ef4444' if type == 'expense' else '#22c55e'
        
        fig = px.bar(
            category_data,
            x='category',
            y='total_amount',
            title=title,
            color='category',
            color_discrete_sequence=[color] * len(category_data),
            text='total_amount'
        )
        
        fig.update_traces(
            texttemplate='R$ %{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<br>%{customdata[0]} transações',
            customdata=category_data[['transaction_count']].values
        )
        
        fig.update_layout(
            xaxis_title='Categoria',
            yaxis_title='Valor Total (R$)',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#1f2937'),
            xaxis={'categoryorder': 'total descending'}
        )
        
        return fig