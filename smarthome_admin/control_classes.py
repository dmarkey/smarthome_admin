__author__ = 'dmarkey'


class ControlBase(object):
    @staticmethod
    def init(controller):
        pass

    @staticmethod
    def on_beacon(controller):
        pass


class Sockets(ControlBase):
    @staticmethod
    def init(controller, number_of_sockets=4):
        from .models import Socket

        for i in range(1, number_of_sockets + 1):
            Socket(controller=controller, number=i).save()

    @staticmethod
    def on_beacon(controller):
        from .models import Socket
        for s in Socket.objects.filter(controller=controller):
            s.send_state()

CONTROL_CLASSES = {"Sockets": Sockets}



