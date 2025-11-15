import sqlite3
import pandas as pd
from datetime import datetime, date
import os

class DatabaseManager:
    def __init__(self, db_path='data/finance.db'):
        # Garantir que o diretório data existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.insert_default_categories()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Tabela de categorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                color TEXT NOT NULL,
                icon TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK(amount > 0),
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category) REFERENCES categories (name)
            )
        ''')
        
        # Tabela de orçamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                month_year TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category) REFERENCES categories (name)
            )
        ''')
        
        self.conn.commit()
    
    def insert_default_categories(self):
        default_categories = [
            # Receitas
            ('Salário', 'income', '#22c55e', '💼'),
            ('Freelance', 'income', '#10b981', '👨‍💻'),
            ('Investimentos', 'income', '#059669', '📈'),
            ('Presente', 'income', '#65a30d', '🎁'),
            ('Outras Receitas', 'income', '#16a34a', '💰'),
            
            # Despesas
            ('Alimentação', 'expense', '#ef4444', '🍕'),
            ('Transporte', 'expense', '#f97316', '🚗'),
            ('Moradia', 'expense', '#dc2626', '🏠'),
            ('Lazer', 'expense', '#eab308', '🎮'),
            ('Saúde', 'expense', '#d97706', '🏥'),
            ('Educação', 'expense', '#9333ea', '📚'),
            ('Compras', 'expense', '#ec4899', '🛍️'),
            ('Outras Despesas', 'expense', '#6b7280', '💸')
        ]
        
        cursor = self.conn.cursor()
        for name, type, color, icon in default_categories:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, type, color, icon)
                    VALUES (?, ?, ?, ?)
                ''', (name, type, color, icon))
            except sqlite3.IntegrityError:
                pass
        
        self.conn.commit()
    
    # Métodos para Transações
    def add_transaction(self, amount, type, category, description, date):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (amount, type, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, type, category, description, date))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_transactions(self, limit=None, filters=None):
        query = '''
            SELECT t.*, c.color, c.icon 
            FROM transactions t
            LEFT JOIN categories c ON t.category = c.name
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('type'):
                query += ' AND t.type = ?'
                params.append(filters['type'])
            if filters.get('category'):
                query += ' AND t.category = ?'
                params.append(filters['category'])
            if filters.get('start_date'):
                query += ' AND t.date >= ?'
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += ' AND t.date <= ?'
                params.append(filters['end_date'])
        
        query += ' ORDER BY t.date DESC, t.created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        df = pd.read_sql_query(query, self.conn, params=params)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def delete_transaction(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Métodos para Categorias
    def get_categories(self, type=None):
        query = 'SELECT * FROM categories'
        params = []
        if type:
            query += ' WHERE type = ?'
            params.append(type)
        query += ' ORDER BY type, name'
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    # Métodos para Analytics
    def get_financial_summary(self, start_date=None, end_date=None):
        df = self.get_transactions(filters={'start_date': start_date, 'end_date': end_date})
        
        if df.empty:
            return {
                'total_income': 0,
                'total_expense': 0,
                'balance': 0,
                'savings_rate': 0
            }
        
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expense = df[df['type'] == 'expense']['amount'].sum()
        balance = total_income - total_expense
        savings_rate = (balance / total_income * 100) if total_income > 0 else 0
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'savings_rate': savings_rate
        }
    
    def get_monthly_summary(self):
        df = self.get_transactions()
        if df.empty:
            return pd.DataFrame()
        
        df['month'] = df['date'].dt.to_period('M').astype(str)
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        monthly['balance'] = monthly.get('income', 0) - monthly.get('expense', 0)
        monthly['savings_rate'] = (monthly['balance'] / monthly.get('income', 1) * 100).round(1)
        
        return monthly.reset_index()
    
    def get_category_analysis(self, type='expense'):
        df = self.get_transactions()
        if df.empty:
            return pd.DataFrame()
        
        category_df = df[df['type'] == type].groupby('category').agg({
            'amount': ['sum', 'count'],
            'color': 'first',
            'icon': 'first'
        }).round(2)
        
        category_df.columns = ['total_amount', 'transaction_count', 'color', 'icon']
        category_df = category_df.sort_values('total_amount', ascending=False)
        return category_df.reset_index()
    
    def close(self):
        self.conn.close()