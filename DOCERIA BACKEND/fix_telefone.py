"""
Script simples para corrigir a constraint NOT NULL na coluna telefone
Execute: python fix_telefone.py
"""
import sqlite3
import os

# Caminho do banco de dados
db_path = "doceria.db"

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    print("   Certifique-se de executar este script na pasta DOCERIA BACKEND")
    exit(1)

print(f"📦 Corrigindo banco de dados: {db_path}")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar estrutura atual
    cursor.execute("PRAGMA table_info(clientes)")
    columns = cursor.fetchall()
    
    print("\n📋 Estrutura atual da tabela clientes:")
    for col in columns:
        print(f"   - {col[1]}: {col[2]} (nullable={not col[3]})")
    
    # Verificar se telefone tem NOT NULL
    telefone_col = [col for col in columns if col[1] == 'telefone']
    if telefone_col and telefone_col[0][3] == 1:  # 1 = NOT NULL
        print("\n⚠️  Coluna telefone tem constraint NOT NULL")
        print("🔄 Recriando tabela para permitir NULL...")
        
        # 1. Criar tabela temporária
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
        
        # 2. Copiar dados
        cursor.execute("""
            INSERT INTO clientes_new 
            SELECT * FROM clientes
        """)
        
        # 3. Remover tabela antiga
        cursor.execute("DROP TABLE clientes")
        
        # 4. Renomear
        cursor.execute("ALTER TABLE clientes_new RENAME TO clientes")
        
        # 5. Recriar índices
        cursor.execute("CREATE UNIQUE INDEX ix_clientes_email ON clientes (email)")
        cursor.execute("CREATE INDEX ix_clientes_cpf ON clientes (cpf)")
        cursor.execute("CREATE INDEX ix_clientes_id ON clientes (id)")
        
        conn.commit()
        
        print("✅ Migração concluída com sucesso!")
        print("   A coluna telefone agora permite valores NULL")
    else:
        print("\n✅ Coluna telefone já permite NULL - nenhuma alteração necessária")
    
    # Verificar estrutura final
    cursor.execute("PRAGMA table_info(clientes)")
    columns = cursor.fetchall()
    print("\n📋 Estrutura final da tabela clientes:")
    for col in columns:
        nullable = "NULL" if not col[3] else "NOT NULL"
        print(f"   - {col[1]}: {col[2]} ({nullable})")
    
    conn.close()
    print("\n✅ Processo concluído!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    if conn:
        conn.rollback()
        conn.close()
    exit(1)

