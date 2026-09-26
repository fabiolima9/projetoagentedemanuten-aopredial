# banco.py - Módulo de Gerenciamento do Banco de Dados SQLite

import sqlite3
from datetime import datetime

# Caminho onde o arquivo do banco de dados será salvo
DB_PATH = "dados/manutencao.db"

def inicializar_banco():
    """
    Cria o arquivo do banco de dados e a tabela de Ordens de Serviço (OS) 
    caso ela ainda não exista.
    """
    # Conecta ao banco (se a pasta dados existir, o SQLite cria o arquivo automaticamente)
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Comando SQL para criar a tabela de ordens de serviço
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_criacao TEXT NOT NULL,
            descricao TEXT NOT NULL,
            local TEXT,
            setor TEXT,
            equipamento TEXT,
            categoria TEXT,
            tipo TEXT,
            prioridade TEXT,
            status TEXT,
            diagnostico TEXT
        )
    """)
    
    # Salva (commita) as alterações e fecha a conexão
    conexao.commit()
    conexao.close()

def salvar_ordem_servico(descricao, local, setor, equipamento, categoria, tipo, prioridade, diagnostico):
    """
    Insere uma nova Ordem de Serviço na tabela e retorna o ID gerado.
    """
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Obtém a data e hora atual formatada
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_inicial = "Aberta"
    
    # Executa a inserção dos dados de forma segura (prevenindo SQL Injection)
    cursor.execute("""
        INSERT INTO ordens_servico (
            data_criacao, descricao, local, setor, equipamento, 
            categoria, tipo, prioridade, status, diagnostico
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_atual, descricao, local, setor, equipamento, 
        categoria, tipo, prioridade, status_inicial, diagnostico
    ))
    
    conexao.commit()
    
    # Pega o ID da última OS inserida
    os_id = cursor.lastrowid
    
    conexao.close()
    return os_id
def buscar_todas_as_os():
    """
    Busca todas as Ordens de Serviço cadastradas no banco de dados 
    e retorna os registros.
    """
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Executa a consulta SQL para buscar todas as colunas ordenadas pelas mais recentes
    cursor.execute("""
        SELECT id, data_criacao, descricao, local, setor, equipamento, 
               categoria, tipo, prioridade, status, diagnostico
        FROM ordens_servico
        ORDER BY id DESC
    """)
    
    registros = cursor.fetchall()
    conexao.close()
    return registros
def obter_indicadores_gerais():
    """
    Retorna métricas consolidadas para o Dashboard:
    - Total de OS
    - OS Abertas
    - OS Críticas
    """
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Total de OS
    cursor.execute("SELECT COUNT(*) FROM ordens_servico")
    total_os = cursor.fetchone()[0]
    
    # OS com status 'Aberta'
    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = 'Aberta'")
    os_abertas = cursor.fetchone()[0]
    
    # OS com prioridade 'Crítica'
    cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE prioridade = 'Crítica'")
    os_criticas = cursor.fetchone()[0]
    
    conexao.close()
    return total_os, os_abertas, os_criticas

def obter_os_por_coluna(coluna):
    """
    Retorna a contagem de Ordens de Serviço agrupadas por uma coluna específica (ex: setor, categoria).
    """
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    # Monta a consulta de agrupamento de forma segura
    query = f"SELECT {coluna}, COUNT(*) FROM ordens_servico GROUP BY {coluna} ORDER BY COUNT(*) DESC"
    cursor.execute(query)
    dados = cursor.fetchall()
    
    conexao.close()
    return dados
def fechar_ordem_servico(os_id, solucao):
    """
    Atualiza o status de uma Ordem de Serviço para 'Concluída' 
    e registra a solução aplicada.
    """
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    
    data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        UPDATE ordens_servico 
        SET status = 'Concluída', 
            diagnostico = diagnostico || ' | Solução Aplicada: ' || ?
        WHERE id = ?
    """, (solucao, os_id))
    
    conexao.commit()
    conexao.close()
