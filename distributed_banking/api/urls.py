from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("if_asked_return", views.if_asked_return, name="if_asked_return"),
    # path("data_to_be_returned", views.data_to_be_returned, name="data_to_be_returned"),
    path("send_propose", views.send_propose, name="send_propose"),  
    path("receive_propose", views.receive_propose, name="receive_propose"),
    path("reach_consensus", views.reach_consensus, name="reach_consensus"),
    path("get_state_machine", views.get_state_machine, name="get_state_machine"),
    path("all_accs", views.all_accs, name="all_accs"),
    path("sequence_of_requests", views.sequence_of_requests, name="sequence_of_requests")
]
