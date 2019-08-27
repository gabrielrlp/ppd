# coding=utf-8
import socket
import argparse
import threading
import Queue
import time

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help="The current machine IP address.", required=True)

users = ['15.29.225.115', '15.8.142.92']
port = 8066

class Application():
    def keyboard(self, q_api_beb):
        while True:
            msg = raw_input('>>> ')
            q_api_beb.put(msg)

    def display(self, q_beb_api):
        while True:
            print(q_beb_api.get())

class BestEfforBroadcast():
    def broadcast(self, q_api_beb, q_beb_pp):
        while True:
            msg = q_api_beb.get()
            # send N vezes para os usuarios
            for u in users:
                data = [u, msg]
                q_beb_pp.put(data)
    
    def deliver(self, q_pp_beb, q_beb_api):
        while True:
            data = q_pp_beb.get()
            msg = '[{}] {}'.format(data[0][0], data[1]) # msg, user
            q_beb_api.put(msg)

class PerfectPoint2PointLinks():         
    def server(self, host, q_pp_beb):
        s = socket.socket()
        s.bind((host, port))
        s.listen(len(users))
        while True:
            c, addr = s.accept()
            t = threading.Thread(target=self.deliver, args=[c, addr, q_pp_beb])
            t.start()

    def deliver(self, client, source, q_pp_beb):
        while True:
            # Data received from client
            data = client.recv(1024)
            if data:
                # Compose the message to populate the FIFO
                msg = [source, data]
                # Put the message into the FIFO
                q_pp_beb.put(msg)

    def send(self, q_beb_pp):
        connections = {}

        while True:
            data = q_beb_pp.get()
            queue = connections.get(data[0], None)
            if queue == None:
                q = Queue.Queue()
                q.put(data)
                connections.update([(data[0], q)])
                t = threading.Thread(target=self.send_t, args=[q])
                t.start()
            else:
                queue.put(data)

    def send_t(self, queue):
        data = queue.get()

        s = socket.socket()
        s.connect((data[0], port))

        while True:
            s.sendall(data[1])
            data = queue.get()

if __name__ == '__main__':
    # Input arguments parser
    args = parser.parse_args()

    # Remove self IP from users array
    users.remove(args.ip)

    # Create FIFOs
    qAB = Queue.Queue() # Queue between Application and Broadcast
    qBP = Queue.Queue() # Queue between Broadcast and Perfect Point
    qPB = Queue.Queue() # Queue between Perfect Point and Broadcast
    qBA = Queue.Queue() # Queue between Broadcast and Application

    api = Application()
    kbd_t = threading.Thread(target=api.keyboard, args=[qAB])
    display_t = threading.Thread(target=api.display, args=[qBA])
    kbd_t.start()
    display_t.start()

    beb = BestEfforBroadcast()
    broadcast_t = threading.Thread(target=beb.broadcast, args=[qAB, qBP])
    deliver_t = threading.Thread(target=beb.deliver, args=[qPB, qBA])
    broadcast_t.start()
    deliver_t.start()

    pp2pl = PerfectPoint2PointLinks()
    send_t = threading.Thread(target=pp2pl.send, args=[qBP])
    server_t = threading.Thread(target=pp2pl.server, args=[args.ip, qPB])
    send_t.start()
    server_t.start()

    kbd_t.join()
    display_t.join()