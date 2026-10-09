import base64
import json
import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Roleta de Sorteio", page_icon="🎰", layout="centered")

PASTA = Path(__file__).parent
TOTAL_NUMEROS = 50

# Mapeamento fixo de nomes para os números definidos
MAPEAMENTO_PONTUADO = {
    "Adelaine": 1,
    "Grazi": 2,
    "Barbara": 3,
    "Maria": 4,
    "Joyce": 5,
    "Victor": 7,
    "Thiago": 11
}

# Inicialização dos estados na sessão
if "tela" not in st.session_state:
    st.session_state.tela = "inicio"  # "inicio" ou "roleta"
if "alvo" not in st.session_state:
    st.session_state.alvo = None
if "nome_ganhador" not in st.session_state:
    st.session_state.nome_ganhador = ""
if "ganhador_selecionado" not in st.session_state:
    st.session_state.ganhador_selecionado = ""
if "giro_id" not in st.session_state:
    st.session_state.giro_id = 0


@st.cache_data
def imagem_base64(caminho):
    return base64.b64encode(Path(caminho).read_bytes()).decode()


def aplicar_estilo():
    fundo = imagem_base64(PASTA / "assets" / "fundo.jpg")
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&display=swap');

        .stApp {{
            background:
                linear-gradient(rgba(255, 248, 238, 0.55), rgba(255, 248, 238, 0.75)),
                url("data:image/jpeg;base64,{fundo}") center / cover fixed;
        }}
        [data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{
            background: rgba(255, 252, 246, 0.82);
            backdrop-filter: blur(6px);
            border-radius: 28px;
            border: 2px solid rgba(212, 167, 58, 0.55);
            box-shadow: 0 12px 40px rgba(120, 60, 20, 0.18);
            margin-top: 1.5rem;
            padding: 1.5rem 1.5rem 1rem;
            max-width: 720px;
            position: relative;
        }}
        .stMarkdown .titulo {{
            font-family: 'Fredoka', sans-serif;
            font-weight: 700;
            font-size: 3rem;
            color: #D7192A;
            text-align: center;
            line-height: 1.1;
            margin: 0;
        }}
        .stMarkdown .subtitulo {{
            font-family: 'Fredoka', sans-serif;
            color: #B8892B;
            text-align: center;
            letter-spacing: 0.25em;
            font-size: 0.9rem;
            margin: 0.2rem 0 0.5rem;
        }}

        /* Estilo do botão principal */
        .stButton > button {{
            font-family: 'Fredoka', sans-serif;
            font-size: 1.3rem;
            border-radius: 999px;
            background: #D7192A;
            color: white;
            border: none;
            padding: 0.75rem 0;
            width: 100% !important;
            margin-top: 0.5rem;
        }}
        .stButton > button:hover {{ background: #B81322; color: white; }}

        /* Estilo exclusivo para o botão de voltar no topo */
        div[data-testid="stColumn"]:first-child button {{
            background: transparent !important;
            color: #D7192A !important;
            border: 2px solid #D7192A !important;
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            font-size: 1.3rem !important;
            line-height: 1 !important;
            margin: 0 !important;
        }}
        div[data-testid="stColumn"]:first-child button:hover {{
            background: #D7192A !important;
            color: white !important;
        }}

        /* Telemóvel */
        @media (max-width: 640px) {{
            .stApp {{ background-attachment: scroll; }}
            .block-container {{
                margin: 0.5rem 0.25rem 0;
                padding: 1rem 0.75rem 0.75rem;
                border-radius: 20px;
            }}
            .stMarkdown .titulo {{ font-size: 2rem; }}
            .stMarkdown .subtitulo {{ font-size: 0.7rem; letter-spacing: 0.15em; }}
            .stButton > button {{ font-size: 1.1rem; padding: 0.6rem 0; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def roleta_html(numero_alvo, nome, giro_id):
    """Roleta em canvas que fica parada ou gira se numero_alvo for definido."""
    dados = json.dumps({"alvo