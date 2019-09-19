# coding=utf-8
import argparse
import threading
import Queue
import time
import numpy as np

from threading import Lock
from cob import CausalOrderBroadcast
from rb import ReliableBroadcast
from beb import BestEfforBroadcast
from pp2pl import PerfectPoint2PointLinks

users = {
    0: '192.168.0.15',
    1: '192.168.0.17'
}

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help='The current machine IP address.', required=True)

class Application():
    def keyboard(self, q_api_cob):
        while True:
            msg = raw_input('>>> ')
            t = time.time()
            q_api_cob.put([msg, t])

    def display(self, q_cob_api):
        while True:
            data = q_cob_api.get()  # [host_key, W, m, t, ip]
            msg = '[user {}] {}'.format(data[0], data[2]) # msg, user
            print(msg)

if __name__ == '__main__':
    # Input arguments parser
    args = parser.parse_args()

    # Remove self IP from users array
	
    mutex_v = Lock()
    V = np.zeros(len(users), dtype=int)

    for key in users:
        if users[key] == args.ip:
            host_key = key

    # Create FIFOs
    # Broadcast
    qAC = Queue.Queue() # Queue between Application and Causal Order Broadcast
    qCR = Queue.Queue() # Queue between Causal Order and Reliable Broadcast
    qRB = Queue.Queue() # Queue between Reliable Broadcast and Best Effort Broadcast
    qBP = Queue.Queue() # Queue between Best Effort Broadcast and Perfect Point to Perfect Link
    # Deliver
    qPB = Queue.Queue() # Queue between Perfect Point to Perfect Link and Best Effort Broadcast
    qBR = Queue.Queue() # Queue between Best Effort Broadcast and Reliable Broadcast
    qRC = Queue.Queue() # Queue between Reliable Broadcast and Causal Order Broadcast
    qCA = Queue.Queue() # Queue between Causal Order Broadcast and Application

    api = Application()
    kbd_t = threading.Thread(target=api.keyboard, args=[qAC])
    display_t = threading.Thread(target=api.display, args=[qCA])
    kbd_t.start()
    display_t.start()

    co = CausalOrderBroadcast()
    co_broadcast_t = threading.Thread(target=co.broadcast, args=[qAC, qCR, V, host_key])
    co_deliver_t = threading.Thread(target=co.deliver, args=[qRC, qCA, V, mutex_v])
    co_broadcast_t.start()
    co_deliver_t.start()

    rb = ReliableBroadcast()
    rb_broadcast_t = threading.Thread(target=rb.broadcast, args=[qCR, qRB])
    rb_deliver_t = threading.Thread(target=rb.deliver, args=[qRB, qBR, qRC])
    rb_broadcast_t.start()
    rb_deliver_t.start()

    beb = BestEfforBroadcast()
    broadcast_t = threading.Thread(target=beb.broadcast, args=[qRB, qBP, users, host_key])
    deliver_t = threading.Thread(target=beb.deliver, args=[qPB, qBR])
    broadcast_t.start()
    deliver_t.start()

    pp2pl = PerfectPoint2PointLinks()
    send_t = threading.Thread(target=pp2pl.send, args=[qBP])
    server_t = threading.Thread(target=pp2pl.server, args=[args.ip, qPB, len(users)])
    send_t.start()
    server_t.start()

    kbd_t.join()
    display_t.join()
