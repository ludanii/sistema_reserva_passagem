from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models, schemas
from fastapi import HTTPException

# --- ATUALIZAÇÕES ---

# Atualização da ocupação dos voos de acordo com as reservas
def atualizar_ocupacao(db: Session, voo_id: int):
    ocupacao_atual = db.query(func.count(models.Reserva.id)).filter(models.Reserva.voo_id == voo_id).scalar()
    voo = db.query(models.Voo).filter(models.Voo.id == voo_id).first()
    if voo:
        voo.ocupacao = ocupacao_atual
        db.commit()

# --- VALIDAÇÕES ---

# Validação genérica de existencia no banco
def validar_existencia(db: Session, model, model_id: int, nome_modelo: str):
    db_objeto = db.query(model).filter(model.id == model_id).first()
    if not db_objeto:
        raise HTTPException(status_code=404, detail=f"{nome_modelo} com ID {model_id} não encontrado.")
    return db_objeto

# Validação do nome do passageiro
def validar_nome(nome: str):
    if not isinstance(nome, str):
        raise HTTPException(status_code=400, detail="O nome deve ser uma string.")

    partes = nome.split()
    if len(partes) < 2:
       raise HTTPException(status_code=400, detail="O nome deve conter pelo menos um nome e um sobrenome.")
    
    if ' ' not in nome:
        raise HTTPException(status_code=400, detail="O nome deve conter pelo menos um sobrenome.")

    if any(char.isdigit() for char in nome):
        raise HTTPException(status_code=400, detail="O nome não deve conter números.")

# Validação do email do passageiro
def validar_email(db: Session, email: str):
    email = email.lower()
    if '@' not in email:
        raise HTTPException(status_code=400, detail="O email deve conter '@'.")
    if db.query(models.Passageiro).filter(models.Passageiro.email == email).first():
        raise HTTPException(status_code=400, detail="O email já está cadastrado.")

# Validação do documento do passageiro
def validar_documento(db: Session, documento: str):
    if len(documento) != 11 or not documento.isdigit():
        raise HTTPException(status_code=400, detail="O CPF deve ter 11 dígitos numéricos.")
    if db.query(models.Passageiro).filter(models.Passageiro.documento == documento).first():
        raise HTTPException(status_code=400, detail="O CPF já está cadastrado.")

# Validação das siglas dos voos
siglas_estados_validas = {     "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",    
"MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}

def validar_sigla_estado(sigla: str):
    sigla = sigla.upper()
    if sigla not in siglas_estados_validas:
        raise HTTPException(status_code=400, detail=f"Sigla de estado '{sigla}' é inválida. Use uma sigla válida.")
    
# Validação da capacidade dos voos
def validar_capacidade(capacidade: str):
    if capacidade > 500:
        raise HTTPException(status_code=400, detail="A capacidade deve ser menor que 500")
    if capacidade < 50:
        raise HTTPException(status_code=400, detail="A capacidade deve ser maior que 50")

# --- CRUD PASSAGEIROS ---

# Criar Passageiro
def criar_passageiro(db: Session, passageiro: schemas.PassageiroCriar):
    validar_documento(db, passageiro.documento)
    validar_email(db, passageiro.email)
    passageiro.email = passageiro.email.lower()
    validar_nome(passageiro.nome)
    db_passageiro = models.Passageiro(**passageiro.dict())
    try:
        db.add(db_passageiro)
        db.commit()
        db.refresh(db_passageiro)
        return db_passageiro
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Passageiro já cadastrado.")

# Listar Passageiros
def listar_passageiros(db: Session, pular: int = 0, limite: int = 10):
    return db.query(models.Passageiro).offset(pular).limit(limite).all()

# Atualizar Passageiro
def atualizar_passageiro(db: Session, passageiro_id: int, passageiro: schemas.PassageiroAtualizar):
    db_passageiro = validar_existencia(db, models.Passageiro, passageiro_id, "Passageiro")
    if db_passageiro.documento != passageiro.documento:
        validar_documento(db, passageiro.documento)
    if db_passageiro.email != passageiro.email:
        passageiro.email = passageiro.email.lower()
        validar_email(db, passageiro.email)
    if db_passageiro.nome != passageiro.nome:
        validar_nome(passageiro.nome)
    for chave, valor in passageiro.dict(exclude_unset=True).items():
        setattr(db_passageiro, chave, valor)
    db.commit()
    db.refresh(db_passageiro)
    return db_passageiro 

# Deletar Passageiro
def deletar_passageiro(db: Session, passageiro_id: int):
    db_passageiro = validar_existencia(db, models.Passageiro, passageiro_id, "Passageiro")
    db.delete(db_passageiro)
    db.commit()
    return {"mensagem": "Passageiro deletado com sucesso"}

# --- CRUD VOOS ---

# Criar Voo
def criar_voo(db: Session, voo: schemas.VooCriar):
    validar_sigla_estado(voo.origem)
    validar_sigla_estado(voo.destino)
    voo.origem = voo.origem.upper()
    voo.destino = voo.destino.upper()
    validar_capacidade(voo.capacidade)
    data_hora_voo = datetime.combine(voo.data, voo.hora)
    if data_hora_voo < datetime.now():
        raise HTTPException(status_code=400, detail="Não é possível criar um voo no passado.")
    db_voo = models.Voo(origem=voo.origem,
        destino=voo.destino,
        data_hora=data_hora_voo.replace(second=0, microsecond=0),
        capacidade=voo.capacidade)
    db.add(db_voo)
    db.commit()
    db.refresh(db_voo)
    return schemas.Voo(
        id=db_voo.id,
        origem=db_voo.origem,
        destino=db_voo.destino,
        data=db_voo.data_hora.date(),
        hora=db_voo.data_hora.time(),
        capacidade=db_voo.capacidade,
        ocupacao=db_voo.ocupacao
    )

def gerar_relatorio(db: Session) -> schemas.Relatorio:
    origens = db.query(models.Voo.origem, func.count(models.Voo.id).label('total_voos')
    ).group_by(models.Voo.origem).all()
    destinos = db.query(models.Voo.destino, func.count(models.Voo.id).label('total_voos')
    ).group_by(models.Voo.destino).all()

    agora = datetime.now(timezone.utc)
    dez_minutos_antes = agora - timedelta(minutes=10)

    voos_decolados = db.query(models.Voo).filter(models.Voo.data_hora < agora).all()
    voos_para_decolar = db.query(models.Voo).filter(models.Voo.data_hora >= dez_minutos_antes, 
    models.Voo.data_hora <= agora).all()
    outros_voos = db.query(models.Voo).filter(models.Voo.data_hora > agora).all()

    relatorio = schemas.Relatorio(
        origens=[{"estado": origem, "total_voos": total_voos} for origem, total_voos in origens],
        destinos=[{"estado": destino, "total_voos": total_voos} for destino, total_voos in destinos],
        decolados=[schemas.VooResponse(**voo.__dict__) for voo in voos_decolados],
        para_decolar=[schemas.VooResponse(**voo.__dict__) for voo in voos_para_decolar],
        outros=[schemas.VooResponse(**voo.__dict__) for voo in outros_voos]
    )
    return relatorio

# Listar Voos
def listar_voos(db: Session, pular: int = 0, limite: int = 10):
    voos = db.query(models.Voo).offset(pular).limit(limite).all()
    voos_schema = [schemas.Voo(
        id=voo.id,
        origem=voo.origem,
        destino=voo.destino,
        data=voo.data_hora.date(),
        hora=voo.data_hora.time(),
        capacidade=voo.capacidade,
        ocupacao=voo.ocupacao
    ) for voo in voos]

    return voos_schema

# Listar os voos com filtros
def buscar_voos_filtrados(db: Session, filtros: schemas.VooBusca) -> List[schemas.Voo]:
    query = db.query(models.Voo)
    if filtros.origem:
        validar_sigla_estado(filtros.origem)
        filtros.origem = filtros.origem.upper()
        query = query.filter(models.Voo.origem == filtros.origem)
    if filtros.destino:
        validar_sigla_estado(filtros.destino)  
        filtros.destino = filtros.destino.upper()
        query = query.filter(models.Voo.destino == filtros.destino)
    if filtros.data:
        query = query.filter(func.trunc(models.Voo.data_hora) == filtros.data)
    if filtros.hora:
        query = query.filter(func.Extract('hour', models.Voo.data_hora) == filtros.hora.hour,
                             func.Extract('minute', models.Voo.data_hora) == filtros.hora.minute)
    voos = query.all()
    return [schemas.Voo(
                id=voo.id,
                origem=voo.origem,
                destino=voo.destino,
                data=voo.data_hora.date(),
                hora=voo.data_hora.time(),
                capacidade=voo.capacidade,
                ocupacao=voo.ocupacao
            ) for voo in voos]

# Atualizar Voo
def atualizar_voo(db: Session, voo_id: int, voo: schemas.VooAtualizar):

    db_voo = validar_existencia(db, models.Voo, voo_id, "Voo")

    if voo.origem:
        validar_sigla_estado(voo.origem)
        db_voo.origem = voo.origem.upper()
    if voo.destino:
        validar_sigla_estado(voo.destino)
        db_voo.destino = voo.destino.upper()
    if voo.capacidade:
        validar_capacidade(voo.capacidade)
        db_voo.capacidade = voo.capacidade
    if voo.data and voo.hora:
        data_hora_voo = datetime.combine(voo.data, voo.hora)
        if data_hora_voo < datetime.now():
            raise HTTPException(status_code=400, detail="Não é possível definir um voo no passado.")
        db_voo.data_hora = data_hora_voo

    db.commit()
    db.refresh(db_voo)                                                                                           
    return schemas.Voo(
        id=db_voo.id,
        origem=db_voo.origem,
        destino=db_voo.destino,
        data=db_voo.data_hora.date(),
        hora=db_voo.data_hora.time(),
        capacidade=db_voo.capacidade,
        ocupacao=db_voo.ocupacao
    )

# Deletar Voo
def deletar_voo(db: Session, voo_id: int):
    db_voo = validar_existencia(db, models.Voo, voo_id, "Voo")
    db.delete(db_voo)
    db.commit()
    return {"mensagem": "Voo deletado com sucesso"}

# --- CRUD RESERVAS ---

# Criar Reserva
def criar_reserva(db: Session, reserva: schemas.ReservaCriar):
    validar_existencia(db, models.Passageiro, reserva.passageiro_id, "Passageiro")
    voo = validar_existencia(db, models.Voo, reserva.voo_id, "Voo")
    if db.query(models.Reserva).filter_by(passageiro_id=reserva.passageiro_id, voo_id=reserva.voo_id).first():
        raise HTTPException(status_code=400, detail="Passageiro já possui uma reserva para este voo.")
    if voo.ocupacao < voo.capacidade:
        if voo.data_hora > datetime.now():
            db_reserva = models.Reserva(**reserva.dict())
            db.add(db_reserva)
            db.commit()
            db.refresh(db_reserva)
            atualizar_ocupacao(db, reserva.voo_id)
            return db_reserva
        else:
            raise HTTPException(status_code=400, detail=f"O voo de ID {reserva.voo_id} já decolou.")
    else:
        raise HTTPException(status_code=400, detail="Capacidade do voo excedida")
        
# Listar Reservas
def listar_reservas(db: Session, pular: int = 0, limite: int = 10):
    return db.query(models.Reserva).offset(pular).limit(limite).all()

# Atualizar Reserva
def atualizar_reserva(db: Session, reserva_id: int, reserva: schemas.ReservaAtualizar):
    db_reserva = validar_existencia(db, models.Reserva, reserva_id, "Reserva")

    if reserva.passageiro_id:
        validar_existencia(db, models.Passageiro, reserva.passageiro_id, "Passageiro")
        novo_passageiro_id = reserva.passageiro_id
    else:
        novo_passageiro_id = db_reserva.passageiro_id

    novo_voo_id = reserva.voo_id or db_reserva.voo_id
    novo_voo = validar_existencia(db, models.Voo, novo_voo_id, "Voo")

    if db.query(models.Reserva).filter_by(passageiro_id=novo_passageiro_id, voo_id=novo_voo_id).first():
        raise HTTPException(status_code=400, detail="Passageiro já possui uma reserva para este voo.")
    if novo_voo.ocupacao < novo_voo.capacidade:
        if novo_voo.data_hora > datetime.now():
            for chave, valor in reserva.dict(exclude_unset=True).items():
                setattr(db_reserva, chave, valor)
            db.commit()
            atualizar_ocupacao(db, db_reserva.voo_id) 
            atualizar_ocupacao(db, novo_voo_id) 
            db.refresh(db_reserva)
            return db_reserva
        else:
            raise HTTPException(status_code=400, detail=f"O voo de ID {reserva.voo_id} já decolou.")
    else:
        raise HTTPException(status_code=400, detail="Capacidade do voo excedida")

# Deletar Reserva
def deletar_reserva(db: Session, reserva_id: int):
    db_reserva = validar_existencia(db, models.Reserva, reserva_id, "Reserva")
    db.delete(db_reserva)
    db.commit()
    atualizar_ocupacao(db, db_reserva.voo_id)
    return {"mensagem": "Reserva deletada com sucesso"}