import pickle

from constants import *
from time import time
from threading import Timer

alltimers = []

class Recordatorio:
    def __init__(self, message, uid, mychat):
        self.message_id = message.message_id
        self.text = message.text

        self.seg = -1  # si es -1, no esta activado. si es distinto marca en
        # cuanto tiempo se ejecutara el timer desde que se inicio con start
        self.timerindex = -1
        self.epoch_of_start = -1  # epoch del momento cuando se inicio el timer

        self.mychat = mychat

        self.uid = uid

        # En general, para agregarle caracteristicas a un rec.
        self.adjectives = set()

        # TODO- Fixear
        try:
            self.nombre = self.message.from_user.first_name
            assert (isinstance(self.nombre, str))
        except:
            self.nombre = "che"

    def setadj(self, adj, value):
        if value:
            self.adjectives.add(adj)
        elif adj in self.adjectives:
            self.adjectives.remove(adj)

    def get_my_chat_from_chats(self, chats):
        return

    def trigger(self):
        # Primero recuerda:
        self.mychat.clarify(self.nombre + " " + RECORDARTEXT, rec=self, reply_message_id=self.message_id, siosi=True)

        # Segundo, pone el mensaje este en actual_r
        self.mychat.actual_r = self

        # Y por las dudas lo pospone:
        if ALARM in self.adjectives:
            self.restart(max(MIN, self.seg / 3), autoset=True)
        if PERIODIC in self.adjectives:
            self.restart(self.seg, autoset=True)
        else:
            self.restart(self.seg * 2, autoset=True)

    # start o restart, es para poner el timer
    def restart(self, seg, autoset=False):
        self.cancel()
        timer = Timer(seg, self.trigger)
        self.timerindex = len(alltimers)
        alltimers.append(timer)
        self.seg = seg
        self.epoch_of_start = time()
        timer.start()
        self.setadj(AUTOSET, autoset)

    def cancel(self):
        if self.seg != -1 and self.timerindex in range(len(alltimers)):
            alltimers[self.timerindex].cancel()
        self.timerindex = -1
        self.seg = -1

    # retorna cuantos segundos faltan para que suene este rec
    def how_much_left(self):
        yapaso = time() - self.epoch_of_start
        return self.seg - yapaso

    # esta funcion se debe ejecutar 1 vez por cada recordatorio
    # cada vez que se apaga el bot y se prende de vuelta, ya que
    # los timers se han borrado y necesita llenar alltimers de vuelta.
    def recreate_timer(self):
        if self.seg == -1:
            # no hace falta, el timer ese ya no sirve mas
            return

        timer = Timer(self.how_much_left(), self.trigger)
        self.timerindex = len(alltimers)
        alltimers.append(timer)
        timer.start()