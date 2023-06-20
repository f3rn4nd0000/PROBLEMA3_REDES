from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import requests
from . import paxos
from . import processo
from django.forms.models import model_to_dict
import paho.mqtt.client as mqtt_client
import uuid

request_payload = {}
request_payload['type'] = ''
request_payload['data'] = {}


class BankAcc():
    def __init__(self) -> None:
        self.id = None
        self.balance = None

    def withdraw(self, value):
        if value > self.balance:
            return "Impossible, reduce the value!"
        else:
            return self.balance - value

    def deposit(self, value):
        return self.balance + value

    def to_json(self):
        return json.dumps(self.__dict__)


class CentralServer():
    def __init__(self) -> None:
        self.master_queue = []  # FILA DE PROCESSOS
        self.special_token = uuid.uuid1()
        self.critical_section = []
        self.accounts = []

    def receive_request_from_processes(self, request):
        if request.method == "GET":
            return JsonResponse(f'{self.special_token}')
        
        if request.method == "POST":
            print(type(request.body))
            process_request = json.loads(request.body)
            
            # if queue of processes is not empty
            if ((process_request['special_token'] is None) 
                    and (self.special_token is not None)):
                process_request['special_token'] = self.special_token
                self.special_token = None
            
            elif ((process_request['special_token'] is not None) 
                    and (self.special_token == None)):
                self.master_queue.append(json.loads(process_request))
                # if (len(self.master_queue) != 0):
