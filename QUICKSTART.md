# 🚀 QUICK START - Ocean AI

## Testando Localmente (5 minutos)

```bash
# 1. Obter chave Groq (gratuita)
# Acesse: https://console.groq.com/ e copie sua API key

# 2. Configurar
echo "GROQ_API_KEY=gsk_sua_chave_aqui" > .env

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Testar
python test_setup.py

# 5. Rodar o app
streamlit run app.py
```

Abra http://localhost:8501 e teste!

---

## Deploy Rápido (10 minutos)

### 1️⃣ GitHub

```bash
git init
git add .
git commit -m "Ocean AI chatbot"
git remote add origin https://github.com/SEU_USUARIO/oceania-chatbot.git
git push -u origin main
```

### 2️⃣ Streamlit Cloud

1. Acesse https://streamlit.io/cloud
2. Login com GitHub
3. Clique **New app**
4. Selecione seu repo `oceania-chatbot`
5. Main file: `app.py`
6. **Advanced Settings > Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_sua_chave_aqui"
   ```
7. **Deploy!**

Aguarde 5-10 minutos e seu app estará online! 🌊

---

## Perguntas para Testar

- Quais espécies marinhas foram registradas?
- Onde ocorre a tartaruga verde na costa brasileira?
- Quais são os objetivos da Década dos Oceanos?
- Quais indicadores climáticos afetam o Oceano Atlântico?
- O que são os dados do Copernicus Marine?

---

## Troubleshooting

### ❌ "GROQ_API_KEY not found"
→ Configure o secret no Streamlit Cloud

### ❌ App lento
→ Normal no primeiro acesso (carrega modelo de 500MB)

### ❌ Erro ao criar índice FAISS
→ Aguarde, é criado automaticamente na primeira vez

---

## 📚 Documentação Completa

- **DEPLOY_GUIDE.md** - Guia detalhado de deploy
- **README.md** - Documentação técnica completa

---

**Pronto!** Seu Ocean AI está no ar 🚀
