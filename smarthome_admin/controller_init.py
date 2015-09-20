__author__ = 'dmarkey'


def make_sockets(controller, number_of_sockets=4):
    from .models import Socket
    for i in range(1, number_of_sockets + 1):
        Socket(controller=controller, number=i).save()


CONTROLLER_INIT_MAP = {"Init Sockets": make_sockets}



