from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base
from datetime import date

# --- MODELO PASSAGEIRO ---

class Passageiro(Base):
    __tablename__ = "passageiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    documento = Column(String, unique=True, index=True)

    # Relacionamento com Reservas
    reservas = relationship("Reserva", back_populates="passageiro")

# --- MODELO VOO ---

class Voo(Base):
    __tablename__ = "voos"

    id = Column(Integer, primary_key=True, index=True)
    origem = Column(String, index=True)
    destino = Column(String, index=True)
    data_hora = Column(TIMESTAMP)
    capacidade = Column(Integer)
    ocupacao = Column(Integer, default=0)


    # Relacionamento com Reservas
    reservas = relationship("Reserva", back_populates="voo")

# --- MODELO RESERVA ---

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    passageiro_id = Column(Integer, ForeignKey("passageiros.id"))
    voo_id = Column(Integer, ForeignKey("voos.id"))
    data_reserva = Column(Date, default=date.today)

    # Relacionamentos
    passageiro = relationship("Passageiro", back_populates="reservas")
    voo = relationship("Voo", back_populates="reservas")
