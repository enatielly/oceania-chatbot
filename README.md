# Ocean AI - Chatbot sobre o Oceano Atlântico

Sistema de chat inteligente com RAG (Retrieval-Augmented Generation) para consulta de dados sobre o Oceano Atlântico adjacente à costa brasileira.

## 🌊 Sobre o Projeto

Ocean AI é um chatbot especializado que responde perguntas sobre as águas marinhas brasileiras no Oceano Atlântico usando **apenas dados oficiais** de 8 fontes científicas.

### Fontes de Dados

1. **OBIS** - Ocean Biodiversity Information System
2. **GBIF** - Global Biodiversity Information Facility
3. **Copernicus Marine** - Dados oceanográficos europeus
4. **ICMBio SALVE** - Espécies ameaçadas
5. **Dados.gov.br** - Unidades de conservação
6. **World Bank** - Indicadores climáticos
7. **IPCC** - Relatórios sobre mudanças climáticas
8. **UNESCO** - Década dos Oceanos

### Tecnologias

- **Frontend**: Streamlit
- **RAG Engine**: SentenceTransformers + FAISS
- **LLM**: Llama 3.1 70B via Groq API
- **Embeddings**: paraphrase-multilingual-mpnet-base-v2

## 🚀 Como Executar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/oceania-chatbot.git
cd oceania-chatbot
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure a API Key do Groq

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
```

**Como obter a chave Groq**:
1. Acesse https://console.groq.com/
2. Crie uma conta gratuita
3. Gere uma API key
4. Cole no arquivo `.env`

### 4. Colete os dados (primeira execução)

```bash
python coletar_dados_amazonia_azul.py
```

Isso irá criar a pasta `data/` com 8 arquivos JSON.

### 5. Execute o chatbot

```bash
streamlit run app.py
```

O app abrirá em http://localhost:8501

## 📦 Estrutura do Projeto

```
oceania-chatbot/
├── app.py                          # Interface Streamlit
├── rag_engine.py                   # Sistema RAG (embeddings + FAISS)
├── coletar_dados_amazonia_azul.py  # Coleta de dados das APIs
├── requirements.txt                # Dependências Python
├── .env                            # Chaves de API (não commitar!)
├── .streamlit/
│   └── secrets.toml               # Secrets para deploy
├── data/                          # JSONs com dados coletados
│   ├── obis_ocorrencias.json
│   ├── gbif_ocorrencias.json
│   ├── copernicus_oceanografia.json
│   ├── icmbio_especies_ameacadas.json
│   ├── unidades_conservacao.json
│   ├── world_bank_climate.json
│   ├── ipcc_relatorios_oceanos.json
│   └── decada_oceanos.json
├── faiss_index                    # Índice vetorial FAISS
└── chunks_metadata.pkl            # Metadados dos chunks
```

## 🌐 Deploy no Streamlit Community Cloud

### 1. Prepare o repositório

Certifique-se de que todos os arquivos estão commitados:

```bash
git add .
git commit -m "Preparando para deploy"
git push origin main
```

**IMPORTANTE**: Adicione `.env` ao `.gitignore`:

```bash
echo ".env" >> .gitignore
```

### 2. Acesse o Streamlit Community Cloud

1. Vá para https://streamlit.io/cloud
2. Faça login com GitHub
3. Clique em "New app"

### 3. Configure o deploy

- **Repository**: Selecione `seu-usuario/oceania-chatbot`
- **Branch**: `main`
- **Main file path**: `app.py`

### 4. Configure os Secrets

No painel do Streamlit Cloud, vá em **Settings > Secrets** e adicione:

```toml
GROQ_API_KEY = "sua_chave_groq_aqui"
```

### 5. Deploy!

Clique em "Deploy" e aguarde. O Streamlit irá:
- Instalar as dependências do `requirements.txt`
- Executar o `app.py`
- Gerar o índice FAISS automaticamente

Seu app estará disponível em: `https://seu-app.streamlit.app`

## ⚙️ Configurações Avançadas

### Rebuild do índice FAISS

Se você atualizar os dados JSON, force rebuild:

```python
# No app.py ou rag_engine.py
rag.setup(force_rebuild=True)
```

Ou no Streamlit, use o botão "🔄 Recarregar Base de Dados" na sidebar.

### Ajustar número de chunks retornados

No `app.py`, função `gerar_resposta`:

```python
resultados = rag.buscar(query, k=5)  # Altere k para mais/menos chunks
```

### Trocar o modelo LLM

No `app.py`, função `gerar_resposta`:

```python
completion = groq_client.chat.completions.create(
    model="llama-3.1-70b-versatile",  # Outros: mixtral-8x7b, llama-3.1-8b
    ...
)
```

### Ajustar temperatura do LLM

```python
temperature=0.1,  # 0.0 = mais factual, 1.0 = mais criativo
```

## 🔒 Segurança

- **Nunca commite** sua `GROQ_API_KEY` no código
- Use `.env` localmente e Streamlit Secrets no deploy
- Adicione `.env` ao `.gitignore`

## 📝 Limitações

1. **Conhecimento limitado**: O chatbot responde APENAS com dados da base local
2. **Sem conhecimento geral**: Não possui informações além dos 8 JSONs
3. **Dados estáticos**: Dados não atualizam automaticamente (requer nova coleta)
4. **Rate limits**: API Groq tem limite de requisições no plano gratuito

## 🐛 Troubleshooting

### Erro: "GROQ_API_KEY não encontrada"

- **Local**: Verifique se `.env` existe e contém a chave
- **Deploy**: Configure o secret no Streamlit Cloud

### Erro: "Índice FAISS não encontrado"

Execute localmente primeiro para gerar o índice:

```bash
python rag_engine.py
```

### App lento no primeiro acesso

É normal! O Streamlit precisa:
1. Carregar modelo de embeddings (~500MB)
2. Carregar índice FAISS
3. Inicializar o Groq client

Após o cache, fica rápido.

## 📊 Estatísticas

- **Modelo de embeddings**: 278M parâmetros
- **Dimensão dos vetores**: 768
- **Chunks na base**: ~150-300 (depende dos dados coletados)
- **Tamanho do índice FAISS**: ~50-100MB
- **Tempo de resposta**: 2-5 segundos

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças grandes:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto. Os dados pertencem às suas respectivas fontes oficiais.

## 🙏 Créditos

Dados fornecidos por:
- OBIS (UNESCO-IOC)
- GBIF
- Copernicus Marine Service
- ICMBio
- Dados.gov.br
- World Bank
- IPCC
- UNESCO Ocean Decade

---

Desenvolvido com 🌊 para as águas brasileiras do Oceano Atlântico
