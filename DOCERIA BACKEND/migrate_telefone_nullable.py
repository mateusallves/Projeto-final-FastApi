"""
Script de migração para tornar a coluna telefone nullable na tabela clientes
"""
import sqlite3
import os
from app.config import settings

def migrate_telefone_nullable():
    """Altera a tabela clientes para permitir telefone NULL"""
    
    # Extrair o caminho do banco de dados da URL
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    print(f"📦 Migrando banco de dados: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna telefone já permite NULL
        cursor.execute("PRAGMA table_info(clientes)")
        columns = cursor.fetchall()
        telefone_info = None
        for col in columns:
            if col[1] == 'telefone':
                telefone_info = col
                break
        
        if telefone_info:
            # SQLite não permite ALTER TABLE para remover NOT NULL diretamente
            # Precisamos recriar a tabela
            
            print("🔄 Recriando tabela clientes com telefone nullable...")
            
            # 1. Criar tabela temporária com a estrutura correta
            cursor.execute("""
                CREATE TABLE clientes_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    nome VARCHAR NOT NULL,
                    email VARCHAR NOT NULL UNIQUE,
                    telefone VARCHAR,
                    cpf VARCHAR UNIQUE,
                    endereco VARCHAR,
                    numero VARCHAR,
                    complemento VARCHAR,
                    bairro VARCHAR,
                    cidade VARCHAR,
                    estado VARCHAR,
                    cep VARCHAR,
                    data_nascimento VARCHAR,
                    observacoes VARCHAR,
                    ativo BOOLEAN,
                    data_cadastro DATETIME,
                    data_atualizacao DATETIME
                )
            """)
            
            # 2. Copiar dados da tabela antiga para a nova
            cursor.execute("""
                INSERT INTO clientes_new 
                SELECT * FROM clientes
            """)
            
            # 3. Remover tabela antiga
            cursor.execute("DROP TABLE clientes")
            
            # 4. Renomear tabela nova
            cursor.execute("ALTER TABLE clientes_new RENAME TO clientes")
            
            # 5. Recriar índices
            cursor.execute("CREATE UNIQUE INDEX ix_clientes_email ON clientes (email)")
            cursor.execute("CREATE INDEX ix_clientes_cpf ON clientes (cpf)")
            cursor.execute("CREATE INDEX ix_clientes_id ON clientes (id)")
            
            conn.commit()
            print("✅ Migração concluída com sucesso!")
            print("   A coluna telefone agora permite valores NULL")
            return True
        else:
            print("⚠️ Coluna telefone não encontrada na tabela clientes")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Migração: Tornar telefone nullable em clientes")
    print("=" * 50)
    migrate_telefone_nullable()

