# coding=utf-8
import argparse
import Queue
import time
import numpy as np
from threading import Thread, Lock

from cob import CausalOrderBroadcast
from rb import ReliableBroadcast
from beb import BestEfforBroadcast
from pp2pl import PerfectPoint2PointLinks

users = {
    0: '10.32.160.190',
    1: '10.32.160.187',
    2: '10.32.160.189'
}

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help='The current machine IP address.', required=True)

class Application():
    """
    Basic application to demonstrate some concepts like Causal Order Broadcast (COB),
    Reliable Broadcast (RB), Best Effort Broadcast (BEB), and Perfect Point to Point Links (PP2PL).
    """
    def broadcast(self, q_api_cob):
        """
        Wait for an user input and store it in a FIFO Queue.
        :param q_api_cob: A python Queue object that being used between 
        the Application and the Causal Order Broadcast.
        """
        while True:
            msg = raw_input('>>> ')
            t = time.time()
            q_api_cob.put([msg, t])

    def deliver(self, q_cob_api):
        """
        Tries to get a data from the Queue to display.
        :param q_cob_api: A python Queue object that being used between 
        the Causal Order Broadcast and the Application.
        """
        while True:
            data = q_cob_api.get()  # [host_key, W, m, t]
            print('[ip={}] [w={}] [t={}] {}'.format(
                users[data[0]], 
                data[1],
                data[3],
                data[2]))

if __name__ == '__main__':
    # Input arguments parser
    args = parser.parse_args()

    # Remove self IP from users array

    mutex_v = Lock()
    V = []
    for i in range(len(users)):
        V.append(0)

    for key in users:
        if users[key] == args.ip:
            host_key = key

    # Create FIFOs
    # Broadcast
    qAC = Queue.Queue() # Queue between Application and Causal Order Broadcast
    qCR = Queue.Queue() # Queue between Causal Order and Reliable Broadcast
    qRB = Queue.Queue() # Queue between Reliable Broadcast and Best Effort Broadcast
    qBP = Queue.Queue() # Queue between Best Effort Broadcast and Perfect Point to Point Links
    # Deliver
    qPB = Queue.Queue() # Queue between Perfect Point to Point Links and Best Effort Broadcast
    qBR = Queue.Queue() # Queue between Best Effort Broadcast and Reliable Broadcast
    qRC = Queue.Queue() # Queue between Reliable Broadcast and Causal Order Broadcast
    qCA = Queue.Queue() # Queue between Causal Order Broadcast and Application

    api = Application()
    api_broadcast_t = Thread(target=api.broadcast, args=[qAC])
    api_deliver_t = Thread(target=api.deliver, args=[qCA])
    api_broadcast_t.start()
    api_deliver_t.start()

    co = CausalOrderBroadcast()
    co_broadcast_t = Thread(target=co.broadcast, args=[qAC, qCR, V, mutex_v, host_key])
    co_deliver_t = Thread(target=co.deliver, args=[qRC, qCA, V, mutex_v])
    co_broadcast_t.start()
    co_deliver_t.start()

    rb = ReliableBroadcast()
    rb_broadcast_t = Thread(target=rb.broadcast, args=[qCR, qRB])
    rb_deliver_t = Thread(target=rb.deliver, args=[qRB, qBR, qRC])
    rb_broadcast_t.start()
    rb_deliver_t.start()

    beb = BestEfforBroadcast()
    beb_broadcast_t = Thread(target=beb.broadcast, args=[qRB, qBP, users, host_key])
    beb_deliver_t = Thread(target=beb.deliver, args=[qPB, qBR])
    beb_broadcast_t.start()
    beb_deliver_t.start()

    pp2pl = PerfectPoint2PointLinks()
    pp2pl_broadcast_t = Thread(target=pp2pl.broadcast, args=[qBP])
    pp2pl_deliver_t = Thread(target=pp2pl.deliver, args=[args.ip, qPB, len(users)])
    pp2pl_broadcast_t.start()
    pp2pl_deliver_t.start()

    api_broadcast_t.join()
    api_deliver_t.join()
