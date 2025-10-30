"""
Ocean AI - Chatbot sobre Amazônia Azul
Interface Streamlit com RAG local
"""

import streamlit as st
import os
from groq import Groq
from rag_engine import OceanRAG
from datetime import datetime


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Ocean AI - Amazônia Azul",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CSS CUSTOMIZADO
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f8ff;
        border-left: 4px solid #1E88E5;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INICIALIZAÇÃO DO SISTEMA RAG
# ============================================================================

@st.cache_resource
def inicializar_rag():
    """
    Inicializa o sistema RAG (cached para não recarregar a cada interação)
    """
    with st.spinner("🔄 Inicializando sistema RAG..."):
        rag = OceanRAG()
        rag.setup(force_rebuild=False)
    return rag


@st.cache_resource
def inicializar_groq():
    """
    Inicializa cliente Groq
    """
    # Tenta pegar a chave do Streamlit secrets (deploy) ou .env (local)
    api_key = None
    
    if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
        api_key = st.secrets['GROQ_API_KEY']
    else:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        st.error("❌ GROQ_API_KEY não encontrada! Configure em .streamlit/secrets.toml ou .env")
        st.stop()
    
    return Groq(api_key=api_key)


# ============================================================================
# FUNÇÃO PRINCIPAL DO CHAT
# ============================================================================

def gerar_resposta(query: str, rag: OceanRAG, groq_client: Groq) -> dict:
    """
    Gera resposta usando RAG + Groq
    """
    # 1. Buscar contexto relevante
    resultados = rag.buscar(query, k=5)
    
    if not resultados:
        return {
            'resposta': "Desculpe, não encontrei informações relevantes na base de dados sobre sua pergunta.",
            'fontes': [],
            'contexto_usado': False
        }
    
    # 2. Montar contexto
    contexto = "\n\n".join([
        f"[FONTE: {chunk['fonte']} - {chunk['url']}]\n{chunk['texto']}"
        for chunk, score in resultados
    ])
    
    # 3. Criar prompt do sistema (CRÍTICO!)
    system_prompt = """Você é o Ocean AI, um assistente especializado em dados sobre as águas marinhas brasileiras do Oceano Atlântico.

REGRAS ABSOLUTAS:
1. Você DEVE responder APENAS usando as informações fornecidas no CONTEXTO abaixo.
2. Você é PROIBIDO de usar seu conhecimento geral ou dados que não estejam no contexto.
3. TODA afirmação ou dado DEVE incluir a citação da fonte usando o formato: [Fonte: NOME_DA_FONTE]
4. Se a informação não estiver no contexto, responda: "Não encontrei essa informação na base de dados disponível."
5. Nunca invente, deduza ou assuma informações que não estejam explicitamente no contexto.
6. Sempre cite a URL da fonte quando disponível.

FORMATO DE CITAÇÃO:
- Use [Fonte: OBIS] para dados do OBIS
- Use [Fonte: GBIF] para dados do GBIF
- Use [Fonte: World Bank] para indicadores climáticos
- E assim por diante...

Seja preciso, objetivo e sempre referencie suas fontes."""

    # 4. Montar mensagens para o LLM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""CONTEXTO DA BASE DE DADOS:
{contexto}

PERGUNTA DO USUÁRIO:
{query}

Responda a pergunta usando APENAS as informações do contexto acima. Cite as fontes."""}
    ]
    
    # 5. Chamar Groq API
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modelo Llama 3.3 70B atualizado
            messages=messages,
            temperature=0.1,  # Baixa temperatura para respostas mais factuais
            max_tokens=1024,
            top_p=0.9
        )
        
        resposta = completion.choices[0].message.content
        
        # 6. Extrair fontes únicas dos chunks
        fontes_unicas = {}
        for chunk, score in resultados:
            fonte_key = chunk['fonte']
            if fonte_key not in fontes_unicas:
                fontes_unicas[fonte_key] = {
                    'nome': chunk['fonte'],
                    'url': chunk['url'],
                    'arquivo': chunk['arquivo'],
                    'secoes': []
                }
            fontes_unicas[fonte_key]['secoes'].append({
                'secao': chunk['secao'],
                'score': score
            })
        
        return {
            'resposta': resposta,
            'fontes': list(fontes_unicas.values()),
            'contexto_usado': True,
            'num_chunks': len(resultados)
        }
        
    except Exception as e:
        return {
            'resposta': f"Erro ao gerar resposta: {str(e)}",
            'fontes': [],
            'contexto_usado': False
        }


# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    # Header
    st.markdown('<div class="main-header">🌊 Ocean AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Assistente Inteligente sobre o Oceano Atlântico adjacente ao Brasil</div>', unsafe_allow_html=True)
    
    # Inicializar sistemas
    rag = inicializar_rag()
    groq_client = inicializar_groq()
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown("### 📊 Base de Dados")
        st.info(f"""
        - **OBIS**: Biodiversidade marinha
        - **GBIF**: Ocorrências de espécies
        - **Copernicus**: Dados oceanográficos
        - **World Bank**: Indicadores climáticos
        - **IPCC**: Relatórios sobre clima
        - **ICMBio**: Espécies ameaçadas
        - **Década dos Oceanos**: Programas UNESCO
        - **Dados.gov.br**: Unidades de conservação
        
        **Total de chunks**: {len(rag.chunks)}
        """)
        
        st.markdown("### ⚠️ Limitações")
        st.warning("""
        Este chatbot responde APENAS com base nos dados coletados.
        Não possui conhecimento geral sobre oceanos.
        """)
        
        st.markdown("### 🔬 Tecnologia")
        st.markdown("""
        - **RAG**: Retrieval-Augmented Generation
        - **Embeddings**: SentenceTransformers
        - **Busca**: FAISS
        - **LLM**: Llama 3.1 70B (Groq)
        """)
        
        if st.button("🔄 Recarregar Base de Dados"):
            st.cache_resource.clear()
            st.rerun()
    
    # Inicializar histórico do chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Exibir histórico do chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Exibir fontes se disponível
            if message["role"] == "assistant" and "fontes" in message:
                if message["fontes"]:
                    with st.expander("📚 Fontes Consultadas"):
                        for fonte in message["fontes"]:
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>{fonte['nome']}</strong><br>
                                <small>Arquivo: {fonte['arquivo']}</small><br>
                                <small>URL: <a href="{fonte['url']}" target="_blank">{fonte['url']}</a></small><br>
                                <small>Seções: {', '.join([s['secao'] for s in fonte['secoes'][:3]])}</small>
                            </div>
                            """, unsafe_allow_html=True)
    
    # Input do usuário
    if prompt := st.chat_input("Pergunte sobre o Oceano Atlântico e a costa brasileira..."):
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant"):
            with st.spinner("🤔 Consultando base de dados..."):
                resultado = gerar_resposta(prompt, rag, groq_client)
            
            st.markdown(resultado['resposta'])
            
            # Exibir fontes
            if resultado['fontes']:
                with st.expander("📚 Fontes Consultadas"):
                    for fonte in resultado['fontes']:
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>{fonte['nome']}</strong><br>
                            <small>Arquivo: {fonte['arquivo']}</small><br>
                            <small>URL: <a href="{fonte['url']}" target="_blank">{fonte['url']}</a></small><br>
                            <small>Seções: {', '.join([s['secao'] for s in fonte['secoes'][:3]])}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Adicionar ao histórico
            st.session_state.messages.append({
                "role": "assistant",
                "content": resultado['resposta'],
                "fontes": resultado['fontes']
            })
    
    # Exemplos de perguntas
    if len(st.session_state.messages) == 0:
        st.markdown("### 💡 Exemplos de perguntas:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - Quais espécies marinhas foram registradas?
            - Onde ocorre a tartaruga verde no Brasil?
            - Quais são os indicadores de mudanças climáticas?
            - O que são os objetivos da Década dos Oceanos?
            """)
        
        with col2:
            st.markdown("""
            - Quais dados oceanográficos estão disponíveis?
            - Qual a temperatura do oceano na costa brasileira?
            - Quais espécies estão ameaçadas?
            - Quantas unidades de conservação marinha existem?
            """)


# ============================================================================
# EXECUTAR APP
# ============================================================================

if __name__ == "__main__":
    main()
