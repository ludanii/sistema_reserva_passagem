import oracledb
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Função para criar uma conexão com o banco de dados Oracle
def create_oracle_connection():
    dsn_str = oracledb.makedsn("oracle.fiap.com.br", 1521, "ORCL")
    con = oracledb.connect(
        user="rm555292",
        password="070905",
        dsn=dsn_str
    )
    return con

# Conexão com o banco de dados
base = create_oracle_connection()
print("Conexão com o banco de dados estabelecida com sucesso.")

# Criação do motor (engine)
DATABASE_URL = "oracle+oracledb://rm555292:070905@oracle.fiap.com.br:1521/ORCL"
engine = create_engine(DATABASE_URL)

# Definição de Base para uso com SQLAlchemy
Base = declarative_base()

# Criação da classe SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cursor para execução de comandos
cur = base.cursor()

#     # Criar tabela voos

#             CREATE TABLE voos (
#                 id NUMBER PRIMARY KEY,
#                 origem VARCHAR2(100) NOT NULL,
#                 destino VARCHAR2(100) NOT NULL,
#                 data_hora TIMESTAMP NOT NULL,
#                 capacidade INT NOT NULL,
#                 ocupacao INT DEFAULT 0

#     # Criar tabela passageiros

#             CREATE TABLE passageiros (
#                 id NUMBER PRIMARY KEY,
#                 email VARCHAR2(100) NOT NULL UNIQUE,
#                 nome VARCHAR2(100) NOT NULL,
#                 documento VARCHAR2(50) NOT NULL UNIQUE

#     # Criar tabela reservas

#             CREATE TABLE reservas (
#                 id NUMBER PRIMARY KEY,
#                 id_passageiro NUMBER NOT NULL,
#                 id_voo NUMBER NOT NULL,
#                 data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (id_passageiro) REFERENCES passageiros(id) ON DELETE CASCADE,
#                 FOREIGN KEY (id_voo) REFERENCES voos(id) ON DELETE CASCADE

# # Criar sequences
#     # Criar sequência de passageiros

#             CREATE SEQUENCE passageiro_seq
#             START WITH 1
#             INCREMENT BY 1
#             NOCACHE
#             NOCYCLE

#     # Criar sequência de reservas

#             CREATE SEQUENCE reserva_seq
#             START WITH 1
#             INCREMENT BY 1
#             NOCACHE
#             NOCYCLE

#     # Criar sequência de voos

#             CREATE SEQUENCE voo_seq
#             START WITH 1
#             INCREMENT BY 1
#             NOCACHE
#             NOCYCLE


cur.close()
base.close()
