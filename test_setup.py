"""
Script de teste para verificar se tudo está funcionando
Execute antes do deploy: python test_setup.py
"""

import os
import sys

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("📋 Verificando arquivos necessários...\n")
    
    arquivos_obrigatorios = [
        'app.py',
        'rag_engine.py',
        'coletar_dados_amazonia_azul.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        '.streamlit/secrets.toml'
    ]
    
    arquivos_data = [
        'data/obis_ocorrencias.json',
        'data/gbif_ocorrencias.json',
        'data/copernicus_oceanografia.json',
        'data/icmbio_especies_ameacadas.json',
        'data/unidades_conservacao.json',
        'data/world_bank_climate.json',
        'data/ipcc_relatorios_oceanos.json',
        'data/decada_oceanos.json'
    ]
    
    todos_ok = True
    
    # Verificar arquivos principais
    for arquivo in arquivos_obrigatorios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO!")
            todos_ok = False
    
    # Verificar pasta data
    print("\n📂 Verificando dados (data/)...\n")
    
    for arquivo in arquivos_data:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo) / 1024  # KB
            print(f"✅ {arquivo} ({tamanho:.1f} KB)")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO!")
            todos_ok = False
    
    return todos_ok


def verificar_env():
    """Verifica variáveis de ambiente"""
    print("\n🔑 Verificando configuração...\n")
    
    # Verificar se .env existe (local)
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado (para testes locais)")
        
        # Verificar se tem GROQ_API_KEY
        with open('.env', 'r') as f:
            conteudo = f.read()
            if 'GROQ_API_KEY' in conteudo and 'sua_chave_aqui' not in conteudo:
                print("✅ GROQ_API_KEY configurada no .env")
            else:
                print("⚠️  GROQ_API_KEY não configurada ou usando placeholder")
                print("   Configure sua chave real do Groq no .env")
    else:
        print("⚠️  Arquivo .env não encontrado")
        print("   Crie um com: echo 'GROQ_API_KEY=sua_chave' > .env")
    
    # Verificar .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            conteudo = f.read()
            if '.env' in conteudo:
                print("✅ .env está no .gitignore (seguro)")
            else:
                print("❌ .env NÃO está no .gitignore - ADICIONE AGORA!")
                return False
    
    return True


def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n📦 Verificando dependências Python...\n")
    
    dependencias = [
        'streamlit',
        'sentence_transformers',
        'faiss',
        'groq',
        'dotenv'
    ]
    
    todos_ok = True
    
    for dep in dependencias:
        try:
            if dep == 'dotenv':
                __import__('dotenv')
            elif dep == 'sentence_transformers':
                __import__('sentence_transformers')
            else:
                __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO!")
            todos_ok = False
    
    if not todos_ok:
        print("\n💡 Instale as dependências com:")
        print("   pip install -r requirements.txt")
    
    return todos_ok


def testar_rag():
    """Testa o carregamento do RAG"""
    print("\n🧪 Testando RAG Engine...\n")
    
    try:
        from rag_engine import OceanRAG
        
        rag = OceanRAG()
        
        # Tentar carregar documentos
        docs = rag.carregar_jsons()
        
        if len(docs) > 0:
            print(f"✅ {len(docs)} arquivos JSON carregados com sucesso")
            
            # Criar chunks
            chunks = rag.criar_chunks(docs)
            print(f"✅ {len(chunks)} chunks criados")
            
            return True
        else:
            print("❌ Nenhum arquivo JSON foi carregado")
            print("   Execute: python coletar_dados_amazonia_azul.py")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar RAG: {str(e)}")
        return False


def main():
    print("="*80)
    print("🧪 TESTE DE SETUP - OCEAN AI")
    print("="*80)
    print()
    
    resultados = []
    
    # 1. Verificar arquivos
    resultados.append(verificar_arquivos())
    
    # 2. Verificar env
    resultados.append(verificar_env())
    
    # 3. Verificar dependências
    resultados.append(verificar_dependencias())
    
    # 4. Testar RAG
    resultados.append(testar_rag())
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO")
    print("="*80)
    print()
    
    if all(resultados):
        print("✅ TUDO OK! Seu projeto está pronto para deploy!")
        print()
        print("Próximos passos:")
        print("1. Teste localmente: streamlit run app.py")
        print("2. Commit no GitHub: git add . && git commit -m 'Ready for deploy'")
        print("3. Push: git push origin main")
        print("4. Deploy no Streamlit Cloud")
        print()
        print("Leia o DEPLOY_GUIDE.md para instruções detalhadas.")
        return 0
    else:
        print("❌ Alguns problemas foram encontrados.")
        print("   Corrija-os antes de fazer o deploy.")
        print()
        print("Veja os detalhes acima e corrija cada ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())
