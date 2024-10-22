from fastapi import HTTPException
from sqlalchemy.orm import Session
import schemas, database, crud

# Funções auxiliares para o menu de Voos
from datetime import datetime, time

def criar_voo_menu(db: Session):

    origem = input("\nOrigem do voo (XX): ")
    destino = input("Destino do voo (XX): ")
    data_str = input("Data do voo (AAAA-MM-DD): ")
    hora_str = input("Horário do voo (HH24:MM): ")

    # Conversão de data e hora
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        print("Formato de data ou hora inválido. Tente novamente.")
        return
    
    capacidade = int(input("Capacidade do voo (50-500): "))
    
    voo_data = {
        "origem": origem,
        "destino": destino,
        "data": data,
        "hora": hora,
        "capacidade": capacidade
    }
    
    try:
        crud.criar_voo(db, schemas.VooCriar(**voo_data))
        print("\nVoo criado com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")


def atualizar_voo_menu(db: Session):
    voo_id = int(input("\nID do voo a ser atualizado: "))
    origem = input("Origem do voo (XX): ")
    destino = input("Destino do voo (XX): ")
    data_str = input("Data do voo (AAAA-MM-DD): ")
    hora_str = input("Horário do voo (HH24:MM): ")
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        print("Formato de data ou hora inválido. Tente novamente.")
        return
    capacidade = input("Capacidade do voo (50-500): ")

    voo_data = {
        "origem": origem,
        "destino": destino,
        "data": data,
        "hora": hora,
        "capacidade": capacidade,
    }

    try:
        crud.atualizar_voo(db, voo_id, schemas.VooAtualizar(**voo_data))
        print("\nVoo atualizado com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")

def listar_voos_menu(db: Session):
    voos = crud.listar_voos(db)
    for voo in voos:
        print(f"\nID: {voo.id}, Origem: {voo.origem}, Destino: {voo.destino}, Data: {voo.data}, Horario: {voo.hora}, Capacidade: {voo.capacidade}, Ocupacao: {voo.ocupacao}")

def gerar_relatorio_menu(db: Session):
    info_relatorio = crud.gerar_relatorio(db)

    # Voos por origem
    print("\n--- Voos por origem ---\n")
    voos_por_origem = info_relatorio.origens  # Atualizando para acessar corretamente a lista
    if voos_por_origem:
        for origem in voos_por_origem:
            print(f"Estado: {origem['estado']}, Total de voos: {origem['total_voos']}")
    else:
        print("Nenhum voo encontrado com essa origem.")

    # Voos por destino
    print("\n--- Voos por destino ---\n")
    voos_por_destino = info_relatorio.destinos  # Atualizando para acessar corretamente a lista
    if voos_por_destino:
        for destino in voos_por_destino:
            print(f"Estado: {destino['estado']}, Total de voos: {destino['total_voos']}")
    else:
        print("Nenhum voo encontrado com esse destino.")
    
    # Voos que já decolaram
    print("\n--- Voos que já decolaram ---\n")
    voos_decolados = info_relatorio.decolados  # Atualizando para acessar corretamente a lista
    if voos_decolados:
        for voo in voos_decolados:
            print(f"ID: {voo.id}, Origem: {voo.origem}, Destino: {voo.destino}, Data: {voo.data_hora.date()}, Horário: {voo.data_hora.time()}, Capacidade: {voo.capacidade}, Passageiros a bordo: {voo.ocupacao}")
    else:
        print("Nenhum voo já decolou.")

    # Voos que estão para decolar
    print("\n--- Voos que estão para decolar ---\n")
    voos_para_decolar = info_relatorio.para_decolar  # Atualizando para acessar corretamente a lista
    if voos_para_decolar:
        for voo in voos_para_decolar:
            print(f"ID: {voo.id}, Origem: {voo.origem}, Destino: {voo.destino}, Data: {voo.data_hora.date()}, Horário: {voo.data_hora.time()}, Capacidade: {voo.capacidade}, Passageiros a bordo: {voo.ocupacao}")
    else:
        print("Nenhum voo está para decolar.")

    # Outros voos (que ainda vão decolar, mas não estão nos próximos 10 minutos)
    print("\n--- Outros voos (futuros) ---\n")
    outros_voos = info_relatorio.outros  # Atualizando para acessar corretamente a lista
    if outros_voos:
        for voo in outros_voos:
            print(f"ID: {voo.id}, Origem: {voo.origem}, Destino: {voo.destino}, Data: {voo.data_hora.date()}, Horário: {voo.data_hora.time()}, Capacidade: {voo.capacidade}, Passageiros a bordo: {voo.ocupacao}")
    else:
        print("Não há outros voos futuros.")

def listar_voos_filtrados_menu(db: Session):
    print(f"\nListagem dos voos com filtracao")
    print("1. Origem")
    print("2. Destino")
    print("3. Data")
    print("4. Horário")
    opcao = input("\nInsira qual atributo deseja usar como filtro dos voos cadastrados: ")

    origem = None
    destino = None
    data = None
    hora = None

    if opcao == "1":
        origem = input("\nOrigem do voo (XX): ")
    elif opcao == "2":
        destino = input("\nDestino do voo (XX): ")
    elif opcao == "3":
        data_str = input("\nData do voo (AAAA-MM-DD): ")
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            print("Formato de data inválido. Tente novamente.")
            return
    elif opcao == "4":
        hora_str = input("\nHorário do voo (HH24:MM): ")
        try:
            hora = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            print("Formato de data inválido. Tente novamente.")
            return

    try:
        voo_data = {"origem": origem, "destino": destino, "data": data, "hora": hora}
        voos = crud.buscar_voos_filtrados(db, schemas.VooBusca(**voo_data))
        if not voos:
            print("\nNenhum voo encontrado com os filtros aplicados.")
        for voo in voos:
            print(f"\nID: {voo.id}, Origem: {voo.origem}, Destino: {voo.destino}, Data: {voo.data}, Horario: {voo.hora}, Capacidade: {voo.capacidade}, Ocupacao: {voo.ocupacao}")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")

def deletar_voo_menu(db: Session):
    voo_id = int(input("\nID do voo a ser deletado: "))
    try:
        crud.deletar_voo(db, voo_id)
        print("\nVoo deletado com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")


# Funções auxiliares para o menu de Passageiros
def criar_passageiro_menu(db: Session):
    nome = input("\nNome do passageiro: ")
    email = input("Email do passageiro: ")
    documento = input("Documento do passageiro: ")
    passageiro_data = {"nome": nome, "email": email, "documento": documento}
    try:
        novo_passsageiro = crud.criar_passageiro(db, schemas.PassageiroCriar(**passageiro_data))
        print(f"\nPassageiro criado com sucesso! Seu ID é {novo_passsageiro.id}, lembre-se dessa informação.")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")


def listar_passageiros_menu(db: Session):
    passageiros = crud.listar_passageiros(db)
    for passageiro in passageiros:
        print(
            f"\nID: {passageiro.id}, Nome: {passageiro.nome}, Email: {passageiro.email}, Documento: {passageiro.documento}")


def atualizar_passageiro_menu(db: Session):
    passageiro_id = int(input("\nID do passageiro a ser atualizado: "))
    nome = input("Novo nome: ")
    email = input("Novo email: ")
    documento = input("Novo documento: ")

    passageiro_data = {
        "nome": nome,
        "email": email,
        "documento": documento
    }

    try:
        crud.atualizar_passageiro(db, passageiro_id, schemas.PassageiroAtualizar(**passageiro_data))
        print("\nPassageiro atualizado com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")

def deletar_passageiro_menu(db: Session):
    passageiro_id = int(input("\nID do passageiro a ser deletado: "))
    try:
        crud.deletar_passageiro(db, passageiro_id)
        print("\nPassageiro deletado com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")


# Funções auxiliares para o menu de Reservas
def criar_reserva_menu(db: Session):
    passageiro_id = int(input("\nID do passageiro: "))
    voo_id = int(input("ID do voo: "))
    reserva_data = {"passageiro_id": passageiro_id, "voo_id": voo_id}
    try:
        crud.criar_reserva(db, schemas.ReservaCriar(**reserva_data))
        print("\nReserva criada com sucesso!")
    except HTTPException as e :
        print(f"\nErro: {e.detail}")

def atualizar_reserva_menu(db: Session):
    reserva_id = int(input("\nID da reserva a ser atualizada: "))
    voo_id = int(input("\nID do voo: "))
    passageiro_id = int(input("\nID do passageiro: "))
    reserva_data = {"passageiro_id": passageiro_id, "voo_id": voo_id}

    try:
        crud.atualizar_reserva(db, reserva_id, schemas.ReservaAtualizar(**reserva_data))
        print("\nReserva atualizada com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")

def listar_reservas_menu(db: Session):
    reservas = crud.listar_reservas(db)
    for reserva in reservas:
        print(f"\nID: {reserva.id}, Passageiro ID: {reserva.passageiro_id}, Voo ID: {reserva.voo_id}")


def deletar_reserva_menu(db: Session):
    reserva_id = int(input("\nID da reserva a ser deletada: "))
    try:
        crud.deletar_reserva(db, reserva_id)
        print("\nReserva deletada com sucesso!")
    except HTTPException as e:
        print(f"\nErro: {e.detail}")

# Menu principal dos voos
def menu_voos(db: Session):
    while True:
        print("\n--- Menu de Voos ---")
        print("1. Criar Voo")
        print("2. Atualizar Voo")
        print("3. Listar Voos")
        print("4. Listar Voos com filtros")
        print("5. Deletar Voo")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            criar_voo_menu(db)
        elif opcao == "2":
            atualizar_voo_menu(db)
        elif opcao == "3":
            listar_voos_menu(db)
        elif opcao == "4":
            listar_voos_filtrados_menu(db)
        elif opcao == "5":
            deletar_voo_menu(db)
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida! Tente novamente.")

# Menu principal dos passageiros
def menu_passageiros(db: Session):
    while True:
        print("\n--- Menu de Passageiros ---")
        print("1. Criar Passageiro")
        print("2. Listar Passageiros")
        print("3. Atualizar Passageiro")
        print("4. Deletar Passageiro")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            criar_passageiro_menu(db)
        elif opcao == "2":
            listar_passageiros_menu(db)
        elif opcao == "3":
            atualizar_passageiro_menu(db)
        elif opcao == "4":
            deletar_passageiro_menu(db)
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida! Tente novamente.")

# Menu principal das reservas
def menu_reservas(db: Session):
    while True:
        print("\n--- Menu de Reservas ---")
        print("1. Criar Reserva")
        print("2. Atualizar Reserva")
        print("3. Listar Reservas")
        print("4. Deletar Reserva")
        print("0. Voltar ao Menu Principal")
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            criar_reserva_menu(db)
        elif opcao == "2":
            atualizar_reserva_menu(db)
        elif opcao == "3":
            listar_reservas_menu(db)
        elif opcao == "4":
            deletar_reserva_menu(db)
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida! Tente novamente.")

# Menu principal
def menu_principal(db: Session):
    while True:
        print("\n--- Menu Principal ---")
        print("1. Gerenciar Voos")
        print("2. Gerenciar Passageiros")
        print("3. Gerenciar Reservas")
        print("4. Gerar relatório administrativo")
        print("0. Sair")
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            menu_voos(db)
        elif opcao == "2":
            menu_passageiros(db)
        elif opcao == "3":
            menu_reservas(db)
        elif opcao == "4":
            gerar_relatorio_menu(db)
        elif opcao == "0":
            print("\nSaindo do sistema.")
            break
        else:
            print("\nOpção inválida! Tente novamente.")

# Conexao
if __name__ == "__main__":
    db = database.SessionLocal()
menu_principal(db)