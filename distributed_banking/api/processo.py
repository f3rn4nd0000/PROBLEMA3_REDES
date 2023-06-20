from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import requests
from . import paxos
from django.forms.models import model_to_dict
import paho.mqtt.client as mqtt_client
import uuid

SERVER_URL = "http://localhost:8000"


request_payload = {}
request_payload['type'] = ''
request_payload['data'] = {}

class Processo():
    def __init__(self, bank_acc, type_of_operation) -> None:
        self.token = None
        self.bank_acc = bank_acc
        self.type_of_operation = type_of_operation

    def send_payload(self, type_of_solicitation:str):
        request_payload['type'] = type_of_solicitation
        request_payload['operation'] = self.bank_acc.type_of_operation # saque, deposito, criar conta, deletar conta
        request_payload['data'] = self.bank_acc.to_json()

# Entra na seção crítica
def ask_to_enter_cs():
    has_token = requests.get(url = SERVER_URL).content
    # if has_token == 
