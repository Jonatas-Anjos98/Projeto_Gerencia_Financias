import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime

# Configuração simples
st.set_page_config(page_title="Finance App", page_icon="💰", layout="wide")
st.title("💰 Gerenciador Financeiro Simples")

# Conexão direta com banco
conn = sqlite3.connect('data/finance.db', check_same_thread=False)
cursor = conn.cursor()

# Criar tabela se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date DATE NOT NULL
    )
''')
conn.commit()

st.success("✅ Aplicação carregada com sucesso!")
st.info("Adicione funcionalidades gradualmente.")