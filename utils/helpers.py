import pandas as pd
from datetime import datetime

def format_currency(value):
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}"

def format_percentage(value):
    """Formata valor como porcentagem"""
    return f"{value:.1f}%"

def get_month_name(month_number):
    """Retorna o nome do mês"""
    months = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return months[month_number - 1]

def calculate_age_in_days(start_date, end_date=None):
    """Calcula diferença em dias entre duas datas"""
    if end_date is None:
        end_date = datetime.now().date()
    return (end_date - start_date).days

def validate_transaction_data(amount, type, category, date):
    """Valida dados da transação"""
    errors = []
    
    if amount <= 0:
        errors.append("Valor deve ser maior que zero")
    
    if type not in ['income', 'expense']:
        errors.append("Tipo deve ser 'income' ou 'expense'")
    
    if not category or category.strip() == "":
        errors.append("Categoria é obrigatória")
    
    if date > datetime.now().date():
        errors.append("Data não pode ser futura")
    
    return errors