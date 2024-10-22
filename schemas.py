from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import date, datetime, time

# PASSAGEIRO
class PassageiroBase(BaseModel):
    nome: str
    email: str
    documento: str

class PassageiroCriar(PassageiroBase):
    pass

class PassageiroAtualizar(BaseModel):
    nome: Optional[str]
    email: Optional[str]
    documento: Optional[str]

class Passageiro(PassageiroBase):
    id: int

    class Config:
        from_attributes = True

# VOO
class VooResponse(BaseModel):
    id: int
    origem: str
    destino: str
    data_hora: datetime
    capacidade: int
    ocupacao: int

# MODELOS ALTERNATIVOS
class Relatorio(BaseModel):
    origens: List[Dict[str, Any]]
    destinos: List[Dict[str, Any]]
    decolados: List[VooResponse]
    para_decolar: List[VooResponse]
    outros: List[VooResponse]

class VooBase(BaseModel):
    origem: str
    destino: str
    data: date
    hora: time
    capacidade: int

class VooCriar(VooBase):
    pass

class VooAtualizar(BaseModel):
    origem: Optional[str]
    destino: Optional[str]
    data: Optional[date]
    hora: Optional[time]
    capacidade: Optional[int]

class Voo(VooBase):
    id: int
    ocupacao: int

    class Config:
        from_attributes = True

class VooBusca(BaseModel):
    origem: Optional[str] = None
    destino: Optional[str] = None
    data: Optional[date] = None
    hora: Optional[time] = None

# RESERVA
class ReservaBase(BaseModel):
    passageiro_id: int
    voo_id: int

class ReservaCriar(ReservaBase):
    pass

class ReservaAtualizar(BaseModel):
    passageiro_id: Optional[int]
    voo_id: Optional[int]

class Reserva(ReservaBase):
    id: int
    data_reserva: date

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True