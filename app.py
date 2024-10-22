from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import schemas, crud
from database import engine, Base
from main import obter_db

# Inicializar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar a instância da aplicação FastAPI
app = FastAPI()

# Rota raiz
@app.get("/")
def read_root(db: Session = Depends(obter_db)):
    return {"mensagem": "Bem-vindo ao sistema de reserva de passagens!"}

# Rotas Passageiros
@app.post("/passageiros/", response_model=schemas.Passageiro)
def criar_passageiro(passageiro: schemas.PassageiroCriar, db: Session = Depends(obter_db)):
    return crud.criar_passageiro(db, passageiro)

@app.get("/passageiros/", response_model=list[schemas.Passageiro])
def listar_passageiros(pular: int = 0, limite: int = 10, db: Session = Depends(obter_db)):
    return crud.listar_passageiros(db, pular=pular, limite=limite)

@app.put("/passageiros/{passageiro_id}", response_model=schemas.Passageiro)
def atualizar_passageiro(passageiro_id: int, passageiro: schemas.PassageiroAtualizar, db: Session = Depends(obter_db)):
    return crud.atualizar_passageiro(db, passageiro_id, passageiro)

@app.delete("/passageiros/{passageiro_id}")
def deletar_passageiro(passageiro_id: int, db: Session = Depends(obter_db)):
    return crud.deletar_passageiro(db, passageiro_id)

# Rotas Voos
@app.post("/voos/", response_model=schemas.Voo)
def criar_voo(voo: schemas.VooCriar, db: Session = Depends(obter_db)):
    return crud.criar_voo(db, voo)

@app.get("/voos/", response_model=list[schemas.Voo])
def listar_voos(pular: int = 0, limite: int = 10, db: Session = Depends(obter_db)):
    return crud.listar_voos(db, pular=pular, limite=limite)

@app.get("/voosfiltrados/", response_model=list[schemas.Voo])
def listar_voos_filtrados(filtros: schemas.VooBusca = Depends(), db: Session = Depends(obter_db)):
    return crud.buscar_voos_filtrados(db, filtros)

@app.put("/voos/{voo_id}", response_model=schemas.Voo)
def atualizar_voo(voo_id: int, voo: schemas.VooAtualizar, db: Session = Depends(obter_db)):
    return crud.atualizar_voo(db, voo_id, voo)

@app.delete("/voos/{voo_id}")
def deletar_voo(voo_id: int, db: Session = Depends(obter_db)):
    return crud.deletar_voo(db, voo_id)

@app.get("/relatorio/", response_model=schemas.Relatorio)
def obter_relatorio(db: Session = Depends(obter_db)):
    return crud.gerar_relatorio(db)

# Rotas Reservas
@app.post("/reservas/", response_model=schemas.Reserva)
def criar_reserva(reserva: schemas.ReservaCriar, db: Session = Depends(obter_db)):
    return crud.criar_reserva(db, reserva)

@app.get("/reservas/", response_model=list[schemas.Reserva])
def listar_reservas(pular: int = 0, limite: int = 10, db: Session = Depends(obter_db)):
    return crud.listar_reservas(db, pular=pular, limite=limite)

@app.put("/reservas/{reserva_id}", response_model=schemas.Reserva)
def atualizar_reserva(reserva_id: int, reserva: schemas.ReservaAtualizar, db: Session = Depends(obter_db)):
    return crud.atualizar_reserva(db, reserva_id, reserva)

@app.delete("/reservas/{reserva_id}")
def deletar_reserva(reserva_id: int, db: Session = Depends(obter_db)):
    return crud.deletar_reserva(db, reserva_id)
