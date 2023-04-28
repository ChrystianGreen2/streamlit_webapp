import streamlit as st
import sqlite3
import qrcode
import io
from PIL import Image

st.set_page_config(
    page_title="NFC Authentication",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "users.db"

def get_user_by_nfc_id(nfc_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE nfc_id = ?", (nfc_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(name, email, phone, address, nfc_id):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email, phone, address, nfc_id) VALUES (?, ?, ?, ?, ?)", (name, email, phone, address, nfc_id))
    conn.commit()
    conn.close()

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        nfc_id TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def pil_image_to_bytes(img):
    byte_stream = io.BytesIO()
    img.save(byte_stream, format='PNG')
    img_bytes = byte_stream.getvalue()
    return img_bytes

def generate_qrcode(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

create_table()

st.markdown("""
<style>
    .header {
        display: flex;
        align-items: center;
    }
    .header img {
        height: 80px;
    }
    .header h1 {
        font-size: 48px;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <img src="https://geticom.uema.br/static/media/header-logo.bba4ba401721d8fd6422.png" />
</div>
""", unsafe_allow_html=True)

st.title("Bem vindo")

menu = st.sidebar.selectbox("Menu", ["Informações do Usuário", "Gerar QR Code"])

if menu == "Informações do Usuário":
    nfc_id = st.experimental_get_query_params().get("nfc_id")
    if nfc_id:
        nfc_id = nfc_id[0]
        user = get_user_by_nfc_id(nfc_id)
        if user:
            st.subheader("Informações do Usuário")
            st.write(f"**ID:** {user[0]}")
            st.write(f"**Nome:** {user[1]}")
            st.write(f"**Email:** {user[2]}")
            st.write(f"**Telefone:** {user[3]}")
            st.write(f"**Endereço:** {user[4]}")
            
            # Adicione campos adicionais aqui, se necessário
        else:
            st.info('Nenhum usuário encontrado com este ID de cartão NFC.', icon="ℹ️")
            st.info("Por favor, cadastre-se abaixo.")
            name = st.text_input("Nome")
            email = st.text_input("Email")
            phone = st.text_input("Telefone")
            address = st.text_input("Endereço")
            # Adicione campos adicionais aqui, se necessário
            if st.button("Cadastrar Usuário"):
                create_user(name, email, phone, address, nfc_id)  # Atualize a função create_user para aceitar campos adicionais
                st.success('Usuário cadastrado com sucesso!', icon="✅")
    else:
        st.write("Seja bem-vindo à página de autenticação via NFC.")

elif menu == "Gerar QR Code":
    base_url = "https://chrystiangreen2-streamlit-webapp-main-vp911m.streamlit.app/"
    nfc_id = st.text_input("Digite o ID do cartão NFC:")
    if st.button("Gerar QR Code"):
        url = f"{base_url}?nfc_id={nfc_id}"
        img = generate_qrcode(url)
        img_bytes = pil_image_to_bytes(img)
        st.image(img_bytes, caption="QR Code", use_column_width=True, output_format='PNG')