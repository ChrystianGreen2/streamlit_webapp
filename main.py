import streamlit as st
import qrcode
import sqlite3
from PIL import Image
import io

DB_NAME = "users.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, nfc_id TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def create_user(name, email, nfc_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email, nfc_id) VALUES (?, ?, ?)", (name, email, nfc_id))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

def update_user(user_id, name, email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_by_nfc_id(nfc_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE nfc_id = ?", (nfc_id,))
    user = c.fetchone()
    conn.close()
    return user

def pil_image_to_bytes(img):
    byte_stream = io.BytesIO()
    img.save(byte_stream, format='PNG')
    img_bytes = byte_stream.getvalue()
    return img_bytes

def generate_qrcode(nfc_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(nfc_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

create_table()

st.title("Gerenciador de Usuários")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Listar Usuários",
        "Adicionar Usuário",
        "Atualizar Usuário",
        "Remover Usuário",
        "Buscar Usuário por ID do Cartão",
        "Gerar QRCode",
    ],
)

if menu == "Listar Usuários":
    users = get_users()
    st.write(users)

elif menu == "Adicionar Usuário":
    name = st.text_input("Nome")
    email = st.text_input("Email")
    nfc_id = st.text_input("ID do Cartão NFC")
    if st.button("Adicionar Usuário"):
        create_user(name, email, nfc_id)
        st.write("Usuário adicionado com sucesso!")

elif menu == "Atualizar Usuário":
    user_id = st.number_input("ID do Usuário", value=None, format="%i")
    name =  st.text_input("Nome")
    email = st.text_input("Email")
    if st.button("Atualizar Usuário"):
        update_user(user_id, name, email)
        st.write("Usuário atualizado com sucesso!")

elif menu == "Remover Usuário":
    user_id = st.number_input("ID do Usuário", value=None, format="%i")
    if st.button("Remover Usuário"):
        delete_user(user_id)
        st.write("Usuário removido com sucesso!")

elif menu == "Buscar Usuário por ID do Cartão":
    nfc_id = st.text_input("ID do Cartão NFC")
    if st.button("Buscar Usuário"):
        user = get_user_by_nfc_id(nfc_id)
    if user:
        st.write("ID do Usuário:", user[0])
        st.write("Nome:", user[1])
        st.write("Email:", user[2])
    else:
        st.write("Nenhum usuário encontrado com este ID de cartão NFC.")

elif menu == "Gerar QRCode":
    nfc_id = st.text_input("ID do Cartão NFC")
    if st.button("Gerar QRCode"):
        img = generate_qrcode(nfc_id)
        img_bytes = pil_image_to_bytes(img)
        st.image(img_bytes, caption="QRCode", use_column_width=True, output_format='PNG')

