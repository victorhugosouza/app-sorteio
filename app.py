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
    "M": 4,
    "Joyce": 5,
    "Victor": 7,
    "Thiago": 11
}


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
            margin-top: 2.5rem;
            padding: 2rem 2rem 1.5rem;
            max-width: 720px;
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
            margin: 0.4rem 0 0.5rem;
        }}
        .stButton > button {{
            font-family: 'Fredoka', sans-serif;
            font-size: 1.3rem;
            border-radius: 999px;
            background: #D7192A;
            border: none;
            padding: 0.6rem 0;
        }}
        .stButton > button:hover {{ background: #B81322; }}

        /* Celular */
        @media (max-width: 640px) {{
            .stApp {{ background-attachment: scroll; }}
            .block-container {{
                margin: 0.75rem 0.5rem 0;
                padding: 1.25rem 1rem 1rem;
                border-radius: 20px;
            }}
            .stMarkdown .titulo {{ font-size: 2.2rem; }}
            .stMarkdown .subtitulo {{ font-size: 0.75rem; letter-spacing: 0.18em; }}
            .stButton > button {{ font-size: 1.15rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def roleta_html(numero_alvo, nome, giro_id):
    """Roleta em canvas que gira até o número alvo e mostra o resultado embaixo."""
    dados = json.dumps({"alvo": numero_alvo, "nome": nome, "total": TOTAL_NUMEROS, "giro": giro_id})
    return f"""
<!doctype html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&display=swap" rel="stylesheet">
<style>
  body {{ margin: 0; font-family: 'Fredoka', sans-serif; text-align: center; background: transparent; }}
  .wrap {{ position: relative; width: 420px; max-width: 92vw; margin: 0 auto; padding-top: 4px; }}
  canvas {{ width: 100%; height: auto; display: block; }}
  .ponteiro {{
    position: absolute; top: -6px; left: 50%; transform: translateX(-50%);
    width: 0; height: 0; border-left: 18px solid transparent; border-right: 18px solid transparent;
    border-top: 34px solid #D7192A; filter: drop-shadow(0 3px 3px rgba(0,0,0,.3)); z-index: 2;
  }}
  #resultado {{ min-height: 120px; margin-top: 14px; opacity: 0; transition: opacity .6s; }}
  #resultado.show {{ opacity: 1; }}
  .num {{ font-size: 3.6rem; font-weight: 700; color: #D7192A; line-height: 1; }}
  .rot {{ color: #B8892B; letter-spacing: .2em; font-size: .85rem; }}
  .nome {{ font-size: 1.6rem; color: #3a2a1a; margin-top: 4px; }}
</style></head>
<body>
  <div class="wrap">
    <div class="ponteiro"></div>
    <canvas id="roda" width="840" height="840"></canvas>
  </div>
  <div id="resultado">
    <div class="rot">NÚMERO SORTEADO</div>
    <div class="num" id="num"></div>
    <div class="nome" id="nome"></div>
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
  // aro dourado e centro
  ctx.beginPath(); ctx.arc(R, R, R - 10, 0, 2 * Math.PI);
  ctx.lineWidth = 18; ctx.strokeStyle = '#D4A73A'; ctx.stroke();
  ctx.beginPath(); ctx.arc(R, R, 70, 0, 2 * Math.PI);
  ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 10; ctx.strokeStyle = '#D7192A'; ctx.stroke();
  ctx.fillStyle = '#D7192A'; ctx.font = '60px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('★', R, R + 4);
}}

function mostrarResultado() {{
  document.getElementById('num').textContent = D.alvo;
  document.getElementById('nome').textContent = D.nome;
  document.getElementById('resultado').classList.add('show');
  if (window.confetti) {{
    confetti({{ particleCount: 160, spread: 90, origin: {{ y: 0.6 }},
               colors: ['#D7192A', '#D4A73A', '#FFFFFF', '#F7C6CE'] }});
  }}
}}

if (D.alvo === null) {{
  desenhar(0);
}} else {{
  // ângulo final: centro do setor alvo embaixo do ponteiro, após várias voltas
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
    if ganhador_selecionado in MAPEAMENTO_PONTUADO:
        return MAPEAMENTO_PONTUADO[ganhador_selecionado], ganhador_selecionado
    # Número aleatório de 1 a 50, excluindo os números fixos para não repetir
    numeros_reservados = set(MAPEAMENTO_PONTUADO.values())
    numeros_disponiveis = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_reservados]
    numero = random.choice(numeros_disponiveis)
    return numero, f"Participante Nº {numero}"


aplicar_estilo()

st.markdown("<p class='titulo'>Roleta de Sorteio</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>★ PLUSHIE PLANET ★</p>", unsafe_allow_html=True)

# Opções de escolha para a organizadora
opcoes_ganhadores = ["🎲 Sorteio Aleatório (Outros Números)"] + list(MAPEAMENTO_PONTUADO.keys())
ganhador_selecionado = st.selectbox("Selecione quem deve ganhar nesta rodada:", opcoes_ganhadores)

if st.button("🎰 Girar Roleta!", type="primary", width="stretch"):
    numero, nome = sortear(ganhador_selecionado)
    st.session_state.giro = {"numero": numero, "nome": nome, "id": time.time()}

# Altura automática: acompanha o tamanho da roleta na tela (celular ou PC)
giro = st.session_state.get("giro")
if giro:
    st.iframe(roleta_html(giro["numero"], giro["nome"], giro["id"]), height="content")
else:
    st.iframe(roleta_html(None, "", 0), height="content")
