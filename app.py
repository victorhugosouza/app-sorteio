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

        /* Celular */
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


def roleta_html(numero_alvo, giro_id):
    """Roleta em canvas que fica parada ou gira até o número alvo, exibindo apenas o número."""
    dados = json.dumps({"alvo": numero_alvo, "total": TOTAL_NUMEROS, "giro": giro_id})
    return f"""
<!doctype html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&display=swap" rel="stylesheet">
<style>
  body {{ margin: 0; font-family: 'Fredoka', sans-serif; text-align: center; background: transparent; overflow: hidden; }}
  .wrap {{ position: relative; width: 340px; max-width: 85vw; margin: 0 auto; padding-top: 4px; }}
  canvas {{ width: 100%; height: auto; display: block; }}
  .ponteiro {{
    position: absolute; top: -4px; left: 50%; transform: translateX(-50%);
    width: 0; height: 0; border-left: 14px solid transparent; border-right: 14px solid transparent;
    border-top: 26px solid #D7192A; filter: drop-shadow(0 2px 2px rgba(0,0,0,.3)); z-index: 2;
  }}
  #resultado {{ min-height: 70px; margin-top: 6px; opacity: 0; transition: opacity .6s; }}
  #resultado.show {{ opacity: 1; }}
  .num {{ font-size: 3.2rem; font-weight: 700; color: #D7192A; line-height: 1; }}
  .rot {{ color: #B8892B; letter-spacing: .2em; font-size: .75rem; }}
</style></head>
<body>
  <div class="wrap">
    <div class="ponteiro"></div>
    <canvas id="roda" width="840" height="840"></canvas>
  </div>
  <div id="resultado">
    <div class="rot">NÚMERO SORTEADO</div>
    <div class="num" id="num"></div>
  </div>
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
<script>
const D = {dados};
const cv = document.getElementById('roda'), ctx = cv.getContext('2d');
const R = cv.width / 2, seg = 2 * Math.PI / D.total;
const cores = ['#D7192A', '#FFF3E0', '#D4A73A', '#FFF3E0'];

function desenhar(rot) {{
  ctx.clearRect(0, 0, cv.width, cv.height);
  ctx.save(); ctx.translate(R, R); ctx.rotate(rot);
  for (let i = 0; i < D.total; i++) {{
    const a0 = -Math.PI / 2 + i * seg;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, R - 20, a0, a0 + seg); ctx.closePath();
    ctx.fillStyle = cores[i % 4]; ctx.fill();
    ctx.strokeStyle = 'rgba(150,100,30,.35)'; ctx.lineWidth = 2; ctx.stroke();
    ctx.save(); ctx.rotate(a0 + seg / 2);
    ctx.fillStyle = (i % 4 === 1 || i % 4 === 3) ? '#7a4b12' : '#fff';
    ctx.font = '700 26px Fredoka, sans-serif'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
    ctx.fillText(String(i + 1), R - 38, 0);
    ctx.restore();
  }}
  ctx.restore();
  ctx.beginPath(); ctx.arc(R, R, R - 10, 0, 2 * Math.PI);
  ctx.lineWidth = 18; ctx.strokeStyle = '#D4A73A'; ctx.stroke();
  ctx.beginPath(); ctx.arc(R, R, 70, 0, 2 * Math.PI);
  ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 10; ctx.strokeStyle = '#D7192A'; ctx.stroke();
  ctx.fillStyle = '#D7192A'; ctx.font = '60px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('★', R, R + 4);
}}

function mostrarResultado() {{
  document.getElementById('num').textContent = D.alvo;
  document.getElementById('resultado').classList.add('show');
  if (window.confetti) {{
    confetti({{ particleCount: 160, spread: 90, origin: {{ y: 0.6 }},
                colors: ['#D7192A', '#D4A73A', '#FFFFFF', '#F7C6CE'] }});
  }}
}}

if (D.alvo === null) {{
  desenhar(0);
}} else {{
  const idx = D.alvo - 1;
  const jitter = (Math.random() - 0.5) * seg * 0.6;
  const final = 8 * 2 * Math.PI - (idx + 0.5) * seg + jitter;
  const duracao = 5500, inicio = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 4);
  function quadro(agora) {{
    const t = Math.min((agora - inicio) / duracao, 1);
    desenhar(final * ease(t));
    if (t < 1) requestAnimationFrame(quadro); else mostrarResultado();
  }}
  requestAnimationFrame(quadro);
}}
</script>
</body></html>
"""


def sortear(ganhador_selecionado):
    # Se for um nome mapeado, devolve o número exato
    if ganhador_selecionado in MAPEAMENTO_PONTUADO:
        return MAPEAMENTO_PONTUADO[ganhador_selecionado]
    
    # Se for sorteio aleatório, exclui TODOS os números reservados (1, 2, 3, 4, 5, 7, 11)
    numeros_reservados = set(MAPEAMENTO_PONTUADO.values())
    numeros_disponiveis = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_reservados]
    return random.choice(numeros_disponiveis)


def ao_selecionar_ganhador():
    opcao = st.session_state.temp_ganhador
    if opcao and opcao != "-- Selecione o participante --":
        st.session_state.ganhador_selecionado = opcao
        st.session_state.alvo = None
        st.session_state.tela = "roleta"


aplicar_estilo()

# 1. TELA INICIAL
if st.session_state.tela == "inicio":
    st.markdown("<p class='titulo'>Roleta de Sorteio</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo'>★ PLUSHIE PLANET ★</p>", unsafe_allow_html=True)

    opcoes_ganhadores = [
        "-- Selecione o participante --",
        "🎲 Sorteio Aleatório (Outros Números)"
    ] + list(MAPEAMENTO_PONTUADO.keys())

    st.selectbox(
        "Selecione quem deve ganhar nesta rodada:",
        opcoes_ganhadores,
        key="temp_ganhador",
        on_change=ao_selecionar_ganhador
    )

# 2. TELA DA ROLETA
else:
    col_voltar, col_titulo = st.columns([1, 8])
    with col_voltar:
        if st.button("←", help="Voltar para a tela inicial"):
            st.session_state.tela = "inicio"
            st.session_state.alvo = None
            st.rerun()

    st.markdown("<p class='titulo' style='margin-top: -30px;'>Roleta de Sorteio</p>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo'>★ PLUSHIE PLANET ★</p>", unsafe_allow_html=True)

    # Ajuste fino da altura do container
    altura_iframe = 430 if st.session_state.alvo is not None else 360

    html_code = roleta_html(
        st.session_state.alvo, 
        st.session_state.giro_id
    )
    st.components.v1.html(html_code, height=altura_iframe)
    
    texto_botao = "🎰 Girar Roleta!" if st.session_state.alvo is None else "🔄 Realizar Novo Giro"
    
    if st.button(texto_botao, use_container_width=True):
        st.session_state.alvo = sortear(st.session_state.ganhador_selecionado)
        st.session_state.giro_id += 1
        st.rerun()