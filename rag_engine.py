"""
RAG Engine para Ocean AI
Carrega JSONs, cria embeddings, constrói índice FAISS
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle


class OceanRAG:
    """
    Sistema RAG local para consulta aos dados da Amazônia Azul
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.chunks: List[Dict] = []
        self.embeddings: np.ndarray = None
        self.index: faiss.IndexFlatL2 = None
        self.model = None
        self.index_path = "faiss_index"
        self.chunks_path = "chunks_metadata.pkl"
        
    def carregar_jsons(self) -> List[Dict]:
        """
        Carrega todos os JSONs da pasta data/
        Retorna lista de dicionários com conteúdo e metadados
        """
        print("📂 Carregando arquivos JSON...")
        
        arquivos_json = [
            'obis_ocorrencias.json',
            'gbif_ocorrencias.json',
            'copernicus_oceanografia.json',
            'icmbio_especies_ameacadas.json',
            'unidades_conservacao.json',
            'world_bank_climate.json',
            'ipcc_relatorios_oceanos.json',
            'decada_oceanos.json'
        ]
        
        documentos = []
        
        for arquivo in arquivos_json:
            caminho = os.path.join(self.data_dir, arquivo)
            
            if not os.path.exists(caminho):
                print(f"   ⚠️  Arquivo não encontrado: {arquivo}")
                continue
                
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    
                documentos.append({
                    'arquivo': arquivo,
                    'conteudo': dados,
                    'metadados': dados.get('metadados', {}),
                    'fonte': dados.get('metadados', {}).get('fonte', 'Fonte desconhecida'),
                    'url': dados.get('metadados', {}).get('url', '')
                })
                
                print(f"   ✅ Carregado: {arquivo}")
                
            except Exception as e:
                print(f"   ❌ Erro ao carregar {arquivo}: {str(e)}")
        
        print(f"\n✅ Total de arquivos carregados: {len(documentos)}")
        return documentos
    
    def criar_chunks(self, documentos: List[Dict]) -> List[Dict]:
        """
        Divide os documentos JSON em chunks menores
        Mantém a referência aos metadados em cada chunk
        """
        print("\n✂️  Criando chunks dos documentos...")
        
        chunks = []
        
        for doc in documentos:
            conteudo = doc['conteudo']
            fonte = doc['fonte']
            url = doc['url']
            arquivo = doc['arquivo']
            
            # Chunk 1: Metadados gerais
            if 'metadados' in conteudo:
                texto_metadados = f"Fonte: {fonte}\n\n"
                texto_metadados += self._dict_para_texto(conteudo['metadados'])
                
                chunks.append({
                    'texto': texto_metadados,
                    'fonte': fonte,
                    'url': url,
                    'arquivo': arquivo,
                    'tipo': 'metadados',
                    'secao': 'Informações Gerais'
                })
            
            # Chunks específicos por tipo de arquivo
            if 'obis' in arquivo or 'gbif' in arquivo:
                # Dados de biodiversidade
                if 'especies' in conteudo:
                    for especie in conteudo['especies']:
                        texto = f"Espécie: {especie.get('nome_cientifico', 'N/A')}\n"
                        texto += f"Fonte: {fonte}\n"
                        texto += f"Total de registros: {especie.get('total_registros_obis', especie.get('total_registros_gbif', 0))}\n\n"
                        
                        # Amostra de registros (primeiros 5)
                        registros = especie.get('registros', [])[:5]
                        if registros:
                            texto += "Ocorrências:\n"
                            for reg in registros:
                                texto += f"- Lat: {reg.get('latitude')}, Lon: {reg.get('longitude')}\n"
                                if reg.get('localidade'):
                                    texto += f"  Local: {reg.get('localidade')}\n"
                                if reg.get('data_observacao'):
                                    texto += f"  Data: {reg.get('data_observacao')}\n"
                        
                        chunks.append({
                            'texto': texto,
                            'fonte': fonte,
                            'url': url,
                            'arquivo': arquivo,
                            'tipo': 'especie',
                            'secao': especie.get('nome_cientifico', 'Espécie')
                        })
            
            elif 'copernicus' in arquivo:
                # Dados oceanográficos
                if 'produtos' in conteudo:
                    for produto in conteudo['produtos']:
                        texto = f"Produto Oceanográfico: {produto.get('produto', 'N/A')}\n"
                        texto += f"Fonte: {fonte}\n"
                        texto += f"ID: {produto.get('produto_id', 'N/A')}\n"
                        texto += f"Variáveis: {', '.join(produto.get('variaveis', []))}\n"
                        
                        if 'area_interesse' in produto:
                            area = produto['area_interesse']
                            texto += f"\nÁrea de Cobertura: {area.get('regiao', 'N/A')}\n"
                            texto += f"Latitude: {area.get('lat_min')} a {area.get('lat_max')}\n"
                            texto += f"Longitude: {area.get('lon_min')} a {area.get('lon_max')}\n"
                        
                        chunks.append({
                            'texto': texto,
                            'fonte': fonte,
                            'url': url,
                            'arquivo': arquivo,
                            'tipo': 'oceanografia',
                            'secao': produto.get('produto', 'Produto')
                        })
            
            elif 'world_bank' in arquivo:
                # Indicadores climáticos
                if 'indicadores_climaticos' in conteudo:
                    for indicador in conteudo['indicadores_climaticos']:
                        texto = f"Indicador: {indicador.get('indicador', 'N/A')}\n"
                        texto += f"Fonte: {fonte}\n"
                        texto += f"Código: {indicador.get('codigo', 'N/A')}\n"
                        texto += f"Relevância Oceânica: {indicador.get('relevancia_oceanica', 'N/A')}\n\n"
                        
                        # Dados temporais recentes (últimos 5 anos)
                        dados_temporais = indicador.get('dados_temporais', [])[:5]
                        if dados_temporais:
                            texto += "Dados Recentes:\n"
                            for dado in dados_temporais:
                                texto += f"- {dado.get('ano')}: {dado.get('valor')} {dado.get('unidade', '')}\n"
                        
                        chunks.append({
                            'texto': texto,
                            'fonte': fonte,
                            'url': url,
                            'arquivo': arquivo,
                            'tipo': 'indicador_climatico',
                            'secao': indicador.get('indicador', 'Indicador')
                        })
            
            elif 'ipcc' in arquivo:
                # Relatórios IPCC
                texto = f"Fonte: {fonte}\n\n"
                
                if 'relatorios_principais' in conteudo:
                    texto += "Relatórios Principais do IPCC:\n"
                    for key, url_rel in conteudo['relatorios_principais'].items():
                        texto += f"- {key}: {url_rel}\n"
                
                if 'temas_oceanicos_cobertos' in conteudo:
                    texto += "\nTemas Oceânicos Cobertos:\n"
                    for tema in conteudo['temas_oceanicos_cobertos']:
                        texto += f"- {tema}\n"
                
                if 'areas_relevancia_brasil' in conteudo:
                    texto += "\nÁreas de Relevância para o Brasil:\n"
                    for area in conteudo['areas_relevancia_brasil']:
                        texto += f"- {area}\n"
                
                chunks.append({
                    'texto': texto,
                    'fonte': fonte,
                    'url': url,
                    'arquivo': arquivo,
                    'tipo': 'relatorios',
                    'secao': 'Relatórios IPCC'
                })
            
            elif 'decada_oceanos' in arquivo:
                # Década dos Oceanos
                texto = f"Fonte: {fonte}\n"
                texto += f"Período: {conteudo.get('metadados', {}).get('periodo', 'N/A')}\n\n"
                
                if 'objetivos_decada' in conteudo:
                    texto += "Objetivos da Década dos Oceanos:\n"
                    for obj in conteudo['objetivos_decada']:
                        texto += f"{obj.get('numero')}. {obj.get('titulo')}: {obj.get('descricao')}\n\n"
                
                chunks.append({
                    'texto': texto,
                    'fonte': fonte,
                    'url': url,
                    'arquivo': arquivo,
                    'tipo': 'programa',
                    'secao': 'Década dos Oceanos'
                })
                
                # Chunk separado para áreas prioritárias do Brasil
                if 'areas_prioritarias_brasil' in conteudo:
                    texto_areas = f"Fonte: {fonte}\n\n"
                    texto_areas += "Áreas Prioritárias da Década dos Oceanos no Brasil:\n"
                    for area in conteudo['areas_prioritarias_brasil']:
                        texto_areas += f"- {area}\n"
                    
                    chunks.append({
                        'texto': texto_areas,
                        'fonte': fonte,
                        'url': url,
                        'arquivo': arquivo,
                        'tipo': 'programa',
                        'secao': 'Prioridades Brasil'
                    })
            
            else:
                # Outros arquivos - chunk genérico
                texto = f"Fonte: {fonte}\n\n"
                texto += self._dict_para_texto(conteudo, max_depth=2)
                
                chunks.append({
                    'texto': texto,
                    'fonte': fonte,
                    'url': url,
                    'arquivo': arquivo,
                    'tipo': 'geral',
                    'secao': 'Dados Gerais'
                })
        
        print(f"✅ Total de chunks criados: {len(chunks)}")
        return chunks
    
    def _dict_para_texto(self, obj, max_depth=3, current_depth=0, prefix="") -> str:
        """
        Converte dicionário/lista em texto legível
        """
        if current_depth > max_depth:
            return ""
        
        texto = ""
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['fonte', 'url', 'data_coleta']:  # Já incluído
                    continue
                    
                if isinstance(value, (dict, list)):
                    texto += f"{prefix}{key}:\n"
                    texto += self._dict_para_texto(value, max_depth, current_depth + 1, prefix + "  ")
                else:
                    texto += f"{prefix}{key}: {value}\n"
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):  # Limita a 10 itens
                if isinstance(item, (dict, list)):
                    texto += self._dict_para_texto(item, max_depth, current_depth + 1, prefix)
                else:
                    texto += f"{prefix}- {item}\n"
        
        return texto
    
    def criar_embeddings(self):
        """
        Cria embeddings dos chunks usando SentenceTransformers
        """
        print("\n🧠 Carregando modelo de embeddings...")
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        
        print("🔢 Gerando embeddings dos chunks...")
        textos = [chunk['texto'] for chunk in self.chunks]
        
        # Gera embeddings em batches
        self.embeddings = self.model.encode(
            textos,
            show_progress_bar=True,
            batch_size=32
        )
        
        print(f"✅ Embeddings gerados: {self.embeddings.shape}")
    
    def construir_indice_faiss(self):
        """
        Constrói índice FAISS para busca vetorial
        """
        print("\n🔍 Construindo índice FAISS...")
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        print(f"✅ Índice construído com {self.index.ntotal} vetores")
    
    def salvar_indice(self):
        """
        Salva índice FAISS e metadados dos chunks
        """
        print("\n💾 Salvando índice e metadados...")
        
        # Salvar índice FAISS
        faiss.write_index(self.index, self.index_path)
        
        # Salvar chunks (sem embeddings para economizar espaço)
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print("✅ Índice e metadados salvos!")
    
    def carregar_indice(self) -> bool:
        """
        Carrega índice FAISS e metadados salvos
        """
        try:
            if not os.path.exists(self.index_path) or not os.path.exists(self.chunks_path):
                return False
            
            print("📥 Carregando índice FAISS e metadados...")
            
            self.index = faiss.read_index(self.index_path)
            
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            # Carregar modelo
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
            
            print(f"✅ Índice carregado: {self.index.ntotal} vetores")
            print(f"✅ Chunks carregados: {len(self.chunks)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar índice: {str(e)}")
            return False
    
    def buscar(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Busca chunks relevantes para a query
        Retorna lista de (chunk, score)
        """
        if self.model is None or self.index is None:
            raise ValueError("Modelo ou índice não carregado. Execute setup() primeiro.")
        
        # Gerar embedding da query
        query_embedding = self.model.encode([query])
        
        # Buscar no FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Retornar chunks com scores
        resultados = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                resultados.append((self.chunks[idx], float(dist)))
        
        return resultados
    
    def setup(self, force_rebuild: bool = False):
        """
        Setup completo: carrega dados, cria embeddings, constrói índice
        """
        # Tentar carregar índice existente
        if not force_rebuild and self.carregar_indice():
            print("✅ Setup concluído (índice carregado do disco)")
            return
        
        # Rebuild completo
        print("🔨 Construindo índice do zero...")
        
        documentos = self.carregar_jsons()
        self.chunks = self.criar_chunks(documentos)
        self.criar_embeddings()
        self.construir_indice_faiss()
        self.salvar_indice()
        
        print("\n✅ Setup completo!")


if __name__ == "__main__":
    # Teste do sistema RAG
    rag = OceanRAG()
    rag.setup(force_rebuild=True)
    
    # Teste de busca
    print("\n" + "="*80)
    print("🔍 TESTE DE BUSCA")
    print("="*80)
    
    query = "Quais espécies marinhas foram encontradas?"
    print(f"\nQuery: {query}\n")
    
    resultados = rag.buscar(query, k=3)
    
    for i, (chunk, score) in enumerate(resultados, 1):
        print(f"\n--- Resultado {i} (Score: {score:.2f}) ---")
        print(f"Fonte: {chunk['fonte']}")
        print(f"Arquivo: {chunk['arquivo']}")
        print(f"Seção: {chunk['secao']}")
        print(f"\nTexto:\n{chunk['texto'][:300]}...")
