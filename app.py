import streamlit as st
import random
import time

st.set_page_config(page_title="Roleta de Sorteio", page_icon="🎰", layout="centered")

st.title("🎰 Roleta de Sorteio")

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

# Opções de escolha para a organizadora
opcoes_ganhadores = ["🎲 Sorteio Aleatório (Outros Números)"] + list(MAPEAMENTO_PONTUADO.keys())

st.subheader("Configuração da Rodada")
ganhador_selecionado = st.selectbox("Selecione quem deve ganhar nesta rodada:", opcoes_ganhadores)

if st.button("🎰 Girar Roleta!", type="primary", width="stretch"):
    placeholder = st.empty()

    # Animação visual da roleta girando
    for _ in range(25):
        num_temp = random.randint(1, 50)
        placeholder.markdown(
            f"<h1 style='text-align: center; color: #FF4B4B; font-size: 48px;'>🔄 Giro: Nº {num_temp}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(0.08)

    # Definição do número vencedor com base na seleção
    if ganhador_selecionado in MAPEAMENTO_PONTUADO:
        numero_vencedor = MAPEAMENTO_PONTUADO[ganhador_selecionado]
        nome_exibido = ganhador_selecionado
    else:
        # Pega um número aleatório de 1 a 50 (excluindo os números fixos para não repetir)
        numeros_reservados = set(MAPEAMENTO_PONTUADO.values())
        numeros_disponiveis = [n for n in range(1, 51) if n not in numeros_reservados]
        numero_vencedor = random.choice(numeros_disponiveis)
        nome_exibido = f"Participante Nº {numero_vencedor}"

    # Limpa a animação e mostra o resultado com comemoração
    placeholder.empty()
    st.balloons()
    st.success("🎉 **SORTEIO REALIZADO COM SUCESSO!**")
    st.markdown(f"<h2 style='text-align: center;'>🏆 Número Sorteado: <span style='color: #2E7D32;'>{numero_vencedor}</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Ganhador(a): <b>{nome_exibido}</b></h3>", unsafe_allow_html=True)
