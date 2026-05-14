import os
from io import BytesIO
import streamlit as st
from docx import Document
import google.generativeai as genai

st.set_page_config(
    page_title="Analisador de Histórias com IA",
    page_icon="📖",
    layout="wide"
)

def extrair_texto_docx(arquivo_docx):
    documento = Document(arquivo_docx)

    paragrafos_validos = []

    for paragrafo in documento.paragraphs:
        texto_limpo = paragrafo.text.strip()

        if texto_limpo:
            paragrafos_validos.append(texto_limpo)

    texto_completo = "\n".join(paragrafos_validos)

    return texto_completo


def configurar_gemini(chave_api):
    genai.configure(api_key=chave_api)

    modelo_gemini = genai.GenerativeModel(
        model_name="gemini-2.5-flash"
    )

    return modelo_gemini


def criar_prompt_analise(texto_historia, foco_usuario):
    prompt_base = f"""
Você é um crítico literário profissional especializado em análise de narrativas.

Sua função NÃO é reescrever a história.
Sua função é APENAS analisar criticamente o conteúdo enviado.

Você deve:

- Identificar falhas narrativas
- Apontar inconsistências
- Detectar furos de roteiro
- Detectar problemas de desenvolvimento
- Detectar personagens mal construídos
- Detectar diálogos artificiais
- Detectar problemas de ritmo
- Detectar excesso de exposição
- Detectar cenas desnecessárias
- Detectar problemas de coerência
- Detectar erros de continuidade
- Detectar mudanças bruscas de personalidade
- Detectar problemas de construção de mundo
- Detectar trechos confusos
- Detectar clichês excessivos
- Sugerir melhorias específicas

IMPORTANTE:
- NÃO reescreva a história
- NÃO continue a história
- NÃO invente partes novas
- Apenas faça comentários e sugestões
- Seja extremamente crítico, detalhado e organizado

Antes de analisar:
Você deve primeiro verificar se o documento realmente parece ser uma história, narrativa, conto, romance ou roteiro.

Se claramente NÃO for uma história:
- Recuse a análise
- Explique que o documento enviado não aparenta ser uma narrativa ficcional

Caso seja uma história:
Organize sua análise nos seguintes tópicos:

1. Visão Geral
2. Pontos Fortes
3. Problemas Narrativos
4. Problemas de Personagens
5. Problemas de Ritmo
6. Inconsistências
7. Qualidade dos Diálogos
8. Clareza da Escrita
9. Sugestões de Melhoria
10. Nota Geral da História

"""


    if foco_usuario.strip():
        prompt_base += f"""

O usuário pediu uma análise com foco especial no seguinte aspecto:

"{foco_usuario}"

Dê atenção extra a esse ponto durante a análise.
"""


    prompt_base += f"""

HISTÓRIA PARA ANÁLISE:

{texto_historia}
"""

    return prompt_base


def analisar_historia(modelo_gemini, prompt):
    resposta = modelo_gemini.generate_content(prompt)

    return resposta.text

st.title("Analisador de Histórias com IA")
st.markdown(
    """
Envie um arquivo `.docx` contendo os rascunhos da sua história e receba uma análise crítica detalhada feita por IA.
"""
)

st.divider()

with st.sidebar:
    st.header("Configurações")

    chave_api_gemini = st.text_input(
        "Chave da API Gemini",
        type="password",
        help="Cole sua chave da API do Gemini aqui"
    )

    st.markdown("---")

    st.markdown(
        """
### Como funciona

1. Você envia um `.docx`
2. A IA lê a história
3. A IA faz uma análise crítica
4. A IA aponta problemas e melhorias

A IA NÃO reescreve a história.
"""
    )

arquivo_enviado = st.file_uploader(
    "Envie sua história em formato .docx",
    type=["docx"]
)


foco_personalizado = st.text_area(
    "Deseja uma análise focada em algum ponto específico?",
    placeholder="Ex: desenvolvimento dos personagens, coerência do mundo, qualidade dos diálogos, ritmo da narrativa..."
)

if arquivo_enviado:

    st.success("Arquivo carregado com sucesso!")

    texto_extraido = extrair_texto_docx(arquivo_enviado)

    with st.expander("Pré-visualização do texto extraído"):
        st.text(texto_extraido[:5000])

    if st.button("Analisar História"):

        if not chave_api_gemini:
            st.error("Insira sua chave da API Gemini.")
            st.stop()

        if len(texto_extraido.strip()) < 300:
            st.warning(
                "O texto enviado parece muito curto para uma análise completa."
            )
            st.stop()

        try:
            with st.spinner("A IA está analisando sua história..."):

                modelo_gemini = configurar_gemini(chave_api_gemini)

                prompt_analise = criar_prompt_analise(
                    texto_historia=texto_extraido,
                    foco_usuario=foco_personalizado
                )

                resultado_analise = analisar_historia(
                    modelo_gemini=modelo_gemini,
                    prompt=prompt_analise
                )

            st.divider()

            st.subheader("Resultado da Análise")

            st.markdown(resultado_analise)

        except Exception as erro:
            st.error(f"Erro durante a análise: {erro}")

st.divider()

st.caption(
    "Projeto de análise crítica de histórias utilizando Streamlit + Gemini"
)