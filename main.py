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

def create_user(name, email, phone, address, nfc_id, img_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email, phone, address, nfc_id, img_data) VALUES (?, ?, ?, ?, ?, ?)", (name, email, phone, address, nfc_id, img_data))
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
        nfc_id TEXT NOT NULL,
        img_data BLOB
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

st.image("https://geticom.uema.br/static/media/header-logo.bba4ba401721d8fd6422.png", width=1000)

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

st.title("Bem vindo")

menu = st.sidebar.selectbox("Menu", ["Informações do Usuário", "Gerar QR Code"])

if menu == "Informações do Usuário":
    nfc_id = st.experimental_get_query_params().get("nfc_id")
    if nfc_id:
        nfc_id = nfc_id[0]
        user = get_user_by_nfc_id(nfc_id)
        if user:
            st.subheader("Informações do Usuário")

            st.markdown("""
            <style>
                .user-info {
                    display: flex;
                    flex-direction: column;
                    background-color: #F0F2F6;
                    border-radius: 5px;
                    padding: 20px;
                    width: 100%;
                    max-width: 500px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .user-info p {
                    font-size: 18px;
                    margin-bottom: 10px;
                }
                .user-info p:last-child {
                    margin-bottom: 0;
                }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="user-info">
                <p><strong>ID:</strong> {user[0]}</p>
                <p><strong>Nome:</strong> {user[1]}</p>
                <p><strong>Email:</strong> {user[2]}</p>
                <p><strong>Telefone:</strong> {user[3]}</p>
                <p><strong>Endereço:</strong> {user[4]}</p>
                <!-- Adicione campos adicionais aqui, se necessário -->
            </div>
            """, unsafe_allow_html=True)
            # img_data = user[5]
            # if img_data is not None:
            #     st.image(img_data, caption="Imagem do usuário", use_column_width=True)
            # else:
            #     st.write("Nenhuma imagem disponível.")
        else:
            st.info('Nenhum usuário encontrado com este ID de cartão NFC.', icon="ℹ️")
            st.info("Por favor, cadastre-se abaixo.")
            
            with st.form("register_form"):
                name = st.text_input("Nome")
                email = st.text_input("Email")
                phone = st.text_input("Telefone")
                address = st.text_input("Endereço")
                uploaded_file = st.file_uploader("Escolha uma imagem", type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("Cadastrar Usuário"):
                    if uploaded_file is not None:
                        img_data = uploaded_file.read()
                    else:
                        img_data = None

                    create_user(name, email, phone, address, nfc_id, img_data)
                    st.success('Usuário cadastrado com sucesso!', icon="✅")


elif menu == "Gerar QR Code":
    base_url = "https://chrystiangreen2-streamlit-webapp-main-vp911m.streamlit.app/"
    nfc_id = st.text_input("Digite o ID do cartão NFC:")
    if st.button("Gerar QR Code"):
        url = f"{base_url}?nfc_id={nfc_id}"
        img = generate_qrcode(url)
        img_bytes = pil_image_to_bytes(img)
        st.image(img_bytes, caption="QR Code", use_column_width=True, output_format='PNG')