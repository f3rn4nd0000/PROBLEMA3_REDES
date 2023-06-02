from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
import uuid
# Create your views here.

# CADA SERVIDOR TERA SEU PROPRIO ID, SERAO 5 (1,2,3,4,5)
SERVER_ID = 1
accounts = []
accounts_uuid = []
request_ids = []
request_id = 0
proposal = (request_id, )
# class InterceptedRequest(HttpRequest):
    
#     def __init__(self) -> None:
#         request_id

# PROPOSER, LEARNER, ACCEPTOR

class

class Account():

    def __init__(self) -> None:
        self.acc_uuid = uuid.uuid1()
        self.list_of_users = []
        self.balance = 0

    def add_user(self, username):
        self.list_of_users.append(username)

    def remove_user(self, username):
        self.list_of_users.remove(username)

    def deposit(self, value):
        self.balance += value

    def withdraw(self, value):
        if (value <= self.balance):
            self.balance -= value
        else:
            return "Impossivel sacar\nValor maior que o saldo\nTente novamente!"

# ADICIONA UM ID AQUELE REQUEST! ISSO É ÚTIL PARA QUE OS SERVERS SE COMUNIQUEM ENTRE SI ATRAVÉS
# DO ESQUEMA PROPOSER, LEARNER, ACCEPTOR
def request_interceptor(request):

    if request.method == "POST":
        request_content = request.POST
        print(request_content)
        request_id += 1
        return dict({"request_id":request_id,"request_content":request_content})


def index(request):
    if request.method == "GET":
        return JsonResponse("Hello!", safe=False)
    
    elif request.method == "POST":
        return JsonResponse({"Dados":"whatever"})
    
def create_new_account(request):
    if request.method == "POST":

        new_acc_id = request.POST["acc_uuid"]
        user_list = request.POST["user_list"]
        password = request.POST["password"]

        new_acc = Account()
        new_acc.id = new_acc_id
        new_acc.user_list

        return JsonResponse("Nova conta criada com sucesso", safe=False)

def withdraw_from_account(request):
    if request.method == "POST":
        acc_uuid = request.POST["acc_uuid"]
        if (request.POST["withdraw_value"] < accounts_uuid[acc_uuid]):
            accounts_uuid
