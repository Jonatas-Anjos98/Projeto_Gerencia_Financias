import streamlit as st
import hashlib
import sqlite3
import os

class AuthManager:
    def __init__(self, db_path='data/finance.db'):
        self.db_path = db_path
        self.create_users_table()
        self.create_default_user()  # Cria usuário padrão automaticamente
    
    def create_users_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_default_user(self):
        """Cria um usuário padrão admin/1234 se não existir"""
        default_username = "admin"
        default_password = "1234"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se já existe
        cursor.execute('SELECT id FROM users WHERE username = ?', (default_username,))
        if not cursor.fetchone():
            password_hash = self.hash_password(default_password)
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (default_username, password_hash)
            )
            conn.commit()
            print("✅ Usuário padrão criado: admin / 1234")
        
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def verify_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT password_hash FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] == self.hash_password(password)
        return False
    
    def show_login_form(self):
        st.header("🔐 Login")
        
        # Informações do usuário padrão: admin / 1234
        
        with st.form("login_form"):
            username = st.text_input("Usuário", value="admin")
            password = st.text_input("Senha", type="password", value="1234")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                if self.verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha inválidos")
        
        # Registro (opcional)
        with st.expander("📝 Criar nova conta"):
            with st.form("register_form"):
                new_username = st.text_input("Novo usuário")
                new_password = st.text_input("Nova senha", type="password")
                confirm_password = st.text_input("Confirmar senha", type="password")
                registered = st.form_submit_button("Registrar")
                
                if registered:
                    if new_password != confirm_password:
                        st.error("❌ Senhas não coincidem")
                    elif len(new_username) < 3:
                        st.error("❌ Usuário deve ter pelo menos 3 caracteres")
                    elif len(new_password) < 4:
                        st.error("❌ Senha deve ter pelo menos 4 caracteres")
                    else:
                        if self.register_user(new_username, new_password):
                            st.success("✅ Conta criada com sucesso! Faça login.")
                        else:
                            st.error("❌ Usuário já existe")