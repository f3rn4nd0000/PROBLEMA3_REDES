from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import requests
from . import paxos
from django.forms.models import model_to_dict
import paho.mqtt.client as mqtt_client

"""
IPS DAS MAQUINAS NO LARSID:
HOST = '172.16.103.num_maquina'
"""

SERVER1 = "http://127.0.0.1:8001"
SERVER2 = "http://localhost:8002"
SERVER3 = "http://localhost:8003"
SERVER4 = "http://localhost:8004"


class ServerType():

    def __init__(self) -> None:
        self.type = ""

    def set_as_proposer(self):
        self.type += "proposer"

    def set_as_acceptor(self):
        self.type += "acceptor"

    def set_as_learner(self):
        self.type += "learner"

class Account():

    def __init__(self, acc_id = None, balance = None):
        self.acc_id = acc_id
        self.balance = 0

    @classmethod
    def create_new_account_with_id(cls, acc_id):
        return cls(acc_id)

    def default(self, o):
        return o.__dict__

    def deposit(self, value):
        self.balance += value

    def withdraw(self, value):
        if (value <= self.balance):
            self.balance -= value
        else:
            return "Impossivel sacar\nValor maior que o saldo\nTente novamente!"

class EnhancedRequest():

    def __init__(self, request) -> None:
        self.original_request = request
        self.order_of_request = 1

    def check_list_of_requests(self):
        return 

# ADICIONA UM ID AQUELE REQUEST! ISSO É ÚTIL PARA QUE OS SERVERS SE COMUNIQUEM ENTRE SI ATRAVÉS
# DO ESQUEMA PROPOSER, LEARNER, ACCEPTOR

sequence_of_requests = []
accs_ids     = []
accs_in_bank = []
mirror1      = []
mirror2      = []


@csrf_exempt
def index(request):
    if request.method == "GET":
        return JsonResponse(json.loads('''
                Envie um json no formato:{
                "tipo_operacao": "<criar_conta, remover_conta, saque, deposito>",
                "id_conta": "valor com 8 digitos aleatorios (letras/numeros/caracteres_especiais)",
                "valor": "<valor>" (apenas para deposito/saque)
            }"'''), safe = False)

    if request.method == "POST":
        print(request.body)

        tipo_operacao = json.loads(request.body).get("tipo_operacao")
        id_conta      = json.loads(request.body).get("id_conta")
        valor         = json.loads(request.body).get("valor")

        print(tipo_operacao, id_conta)

        if (id_conta in accs_in_bank):
            acc = accs_in_bank[accs_in_bank.index(id_conta)]
            if (tipo_operacao == "saque"):
                return JsonResponse(json.loads(request.body), safe=False)
            else :
                return JsonResponse("Erro!!!", safe=False)
            
        elif (tipo_operacao == "criar_conta"):
            # print(json.dumps(Account.create_new_account_with_id(acc_id=id_conta)).encode("utf-8"))
            accs_ids.append(id_conta)
            
            new_acc = Account.create_new_account_with_id(acc_id=id_conta)
            serialized_new_acc = json.dumps(new_acc.__dict__)
            accs_in_bank.append(serialized_new_acc)
            print("accs_in_bank")
            print(accs_in_bank)
            try:
                propose = send_propose(request)
                print("propose")
                print(propose)
                if (propose == 200):
                    return JsonResponse("Foi sincronizado", safe = False)
            except TypeError as e:
                print(e)

        else:
            return JsonResponse("Operacao abortada, razao: essa conta nao existe", safe=False)

@csrf_exempt
def send_propose(request):
    if request.method == "GET":
        return JsonResponse(accs_in_bank, safe = False)
    if request.method == "POST":
        print("data dentro de SYNC")
        print(accs_in_bank)
        sync_req = requests.post(url = SERVER1+"/api/receive_propose", data = json.dumps(str(accs_in_bank)))
        return sync_req.status_code

@csrf_exempt
def receive_propose(request):
    if request.method == "POST":
        print("inside recv sync data")
        print(request.body)
        data = json.dumps(request.body).encode("utf-8")
        print(f"dados recebidos do sync req.: {data}")
        accs_in_bank.append(json.dumps())
        return JsonResponse(accs_in_bank, safe = False)

@csrf_exempt
def get_state_machine(request):
    if request.method == "GET":
        print(f"dentro de get state machine: {sequence_of_requests}")
        return JsonResponse(sequence_of_requests, safe = False)


@csrf_exempt
def reach_consensus(request):
    if request.method == "GET":
        server_1_requests = requests.get(url=SERVER1+"/api/get_state_machine")
        server_2_requests = requests.get(url=SERVER2+"/api/get_state_machine")
        server_3_requests = requests.get(url=SERVER3+"/api/get_state_machine")
        server_4_requests = requests.get(url=SERVER4+"/api/get_state_machine")

        if (server_1_requests == server_2_requests and server_1_requests == server_3_requests and server_1_requests == server_4_requests):
            return JsonResponse("consensus reached", safe = False)
        else:
            return JsonResponse("consensus not reached")


# def listen_for_other_servers(request):
#     if request.method == "GET":
#         requests.post(url = SERVER1+"/data_to_be_returned", data = request_propposed)
#         # requests.post(url = SERVER2, data = sequence_of_requests)
#         # requests.post(url = SERVER3, data = sequence_of_requests)
#         return JsonResponse({"status_code":200,
#                              "data_posted": str(sequence_of_requests).encode("utf-8")
#                              })
    
#     if request.method == "POST":
#         sequence_of_requests.append(json.loads(request.body.data))


    
@csrf_exempt
def data_to_be_returned(request):
    if request.method == "POST":
        data = json.loads(request.body)
        data['type_of_request'] = 'proposer'
        print(data)
        sequence_of_requests.append(data)
        print(sequence_of_requests)
        return JsonResponse({"status_code":"200",
                             "data_received": str(data).decode("utf-8"),   
                            })
    

def withdraw_from_acc(request, value):
    if request.method == "POST":
        acc_to_be_withdraw = request.body.get('acc_id')
        value_to_be_withdraw = request.body.get('value')

        new_request = json.loads({
            "type_operation": "withdraw",
            "acc": str(acc_to_be_withdraw),
            "value": str(value_to_be_withdraw)
        })
        
        sequence_of_requests.append(json.loads(request.body.data)) 
        return JsonResponse(f"Saque no valor de {value_to_be_withdraw} da conta {acc_to_be_withdraw} realizado com suceso")


# @csrf_exempt
# def index(request):
#     if request.method == "GET":
#         return JsonResponse("Selecione um posto no qual deseja realizar a operacao:\n1-Banco A\n2-Banco B\n3-Banco C\n4-Banco D\n5-Banco E", safe=False)
    
#     elif request.method == "POST":
#         print(request.POST)
#         num_banco = json.loads(request.body).get("num_banco")
#         print(num_banco)
#         tipo_operacao = json.loads(request.body).get("tipo_operacao")
#         account = Account(num_banco, id_conta)

#         if (tipo_operacao == "consulta"):
#             id_conta = json.loads(request.body).get("id_conta")
            
#             return JsonResponse({"Saldo da conta: "saldo_conta})
#         elif (tipo_operacao == "saque"):
#             valor_saque = json.loads(request.body).get("valor_saque")
#             if (valor_saque < )

            
#             new_proposal = paxos.Proposer()
#             new_proposal.propose_value


#         elif (tipo_operacao == "deposito"):


#         return JsonResponse({"Banco selecionado":num_banco})

# @csrf_exempt    
# def create_new_account(request):
#     if request.method == "POST":

#         new_acc_id = request.POST["acc_uuid"]
#         user_list = request.POST["user_list"]
#         password = request.POST["password"]

#         new_acc = Account()
#         new_acc.id = new_acc_id
#         new_acc.user_list

#         return JsonResponse("Nova conta criada com sucesso", safe=False)


# @csrf_exempt
# def withdraw_from_account(request):
#     if request.method == "POST":
#         acc_uuid = request.POST["acc_uuid"]
#         if (request.POST["withdraw_value"] < accounts_uuid[acc_uuid]):
#             accounts_uuid

# Create your views here.

# CADA SERVIDOR TERA SEU PROPRIO ID, SERAO 5 (1,2,3,4,5)
# SERVER_ID = 1
# accounts = []
# accounts_uuid = []
# request_ids = []
# request_id = 0
# proposal = (request_id, )

# class InterceptedRequest(HttpRequest):
    
#     def __init__(self) -> None:
#         request_id

# PROPOSER, LEARNER, ACCEPTOR

# class Proposal():

#     def __init__(self) -> None:
#         self.proposal_id = SERVER_ID
#         ...

#     def propose_to_acceptor(self):
#         self.proposal_id += 1
#         requests.post(  )

################################################################################################################################################
# BACKUP DO DIA 18/06

"""
def listen_for_other_servers(request):
    if request.method == "GET":
        requests.post(url = SERVER1+"/data_to_be_returned", data = request_propposed)
        # requests.post(url = SERVER2, data = sequence_of_requests)
        # requests.post(url = SERVER3, data = sequence_of_requests)
        return JsonResponse({"status_code":200,
                             "data_posted": str(sequence_of_requests).encode("utf-8")
                             })
    
    if request.method == "POST":
        sequence_of_requests.append(json.loads(request.body.data))

# Porta de espelhamento, onde irao passar as requisicoes proposing, learning.
def mirroring_port(request):
    if request.method == "POST":
        sequence_of_requests.append(json.loads(request.body.data))



# Essa rota serve especificamente quando um servidor quer saber qual o status de outro servidor.
@csrf_exempt 
def if_asked_return(request):
    if request.method == "GET":
        requests.post(url = SERVER1+"/data_to_be_returned", data = request_propposed)
        # requests.post(url = SERVER2, data = sequence_of_requests)
        # requests.post(url = SERVER3, data = sequence_of_requests)
        # requests.post(url = SERVER4, data = sequence_of_requests)
        return JsonResponse({"status_code":200,
                             "data_posted": str(sequence_of_requests).encode("utf-8")
                             })
    
@csrf_exempt
def data_to_be_returned(request):
    if request.method == "POST":
        data = request.body
        sequence_of_requests.append(data)
        print(sequence_of_requests)
        return JsonResponse({"status_code":200,
                             "data_received": str(data).decode("utf-8"),   
                             })

@csrf_exempt
def request_interceptor(request):
    if request.method == "POST":
        request_content = request.POST
        print(request_content)
        request_id += 1
        return dict({"request_id":request_id,"request_content":request_content})


# Porta de espelhamento, onde irao passar as requisicoes proposing, learning.
def mirroring_port(request):
    if request.method == "POST":
        sequence_of_requests.append(json.loads(request.body.data))

        

##############################################################################################################################

@csrf_exempt
def receive_sync_data(request):
    if request.method == "POST":
        print("inside recv sync data")
        print(request.body)
        data = json.dumps(request.body).encode("utf-8")
        print(f"dados recebidos do sync req.: {data}")
        accs_in_bank.append(json.dumps())
        return JsonResponse(accs_in_bank, safe = False)


@csrf_exempt
def sync(request):
    # if request.method == "GET":
    #     return JsonResponse(accs_in_bank, safe = False)
    if request.method == "POST":
        print("data dentro de SYNC")
        print(accs_in_bank)
        sync_req = requests.post(url = SERVER1+"/api/receive_sync_data", data = json.dumps(str(accs_in_bank)))
        # print(sync_req.status_code) 
        return sync_req.status_code
        # requests.post(url = SERVER2, data = sequence_of_requests)
        # requests.post(url = SERVER3, data = sequence_of_requests)
        # requests.post(url = SERVER4, data = sequence_of_requests)
        
        # return JsonResponse({"status_code":200,
        #                      "data_posted": str(sequence_of_requests).encode("utf-8")
        #                      })

@csrf_exempt
def if_asked_return(request):
    if request.method == "POST":
        request_proposed = request.body
        requests.get(url = SERVER1+"/data_to_be_returned", data = request_proposed)
        # requests.post(url = SERVER2, data = sequence_of_requests)
        # requests.post(url = SERVER3, data = sequence_of_requests)
        # requests.post(url = SERVER4, data = sequence_of_requests)
        return JsonResponse({"status_code":"200",
                             "data_posted": str(sequence_of_requests).encode("utf-8")
                             })

@csrf_exempt
def show_accs(request):
    if request.method == "GET":
        return JsonResponse()



        
"""