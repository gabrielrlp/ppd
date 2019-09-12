# coding=utf-8
import socket
import argparse
import threading
import Queue
import time

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help="The current machine IP address.", required=True)

users = ['10.32.169.44', '10.32.169.74', '10.32.169.54']
port = 8066

class Application():
    def keyboard(self, q_api_co):
        while True:
            msg = raw_input('>>> ')
            q_api_co.put(msg)

    def display(self, q_co_api):
        while True:
            print(q_co_api.get())

class CausalOrderBroadcast():
    def __init__(self):
        print('start co')

    def broadcast(self, q_api_co, q_co_rb):
        pass
    
    def deliver(self, q_rb_co, q_co_api):
        pass

class ReliableBroadcast():
	def broadcast(self, q_co_rb, q_rb_beb):
		while True:
			msg = q_co_rb.get()
			q_rb_beb.put(msg)

	def deliver(self, q_rb_beb, q_beb_rb, q_rb_co):
		while True:		
			msg = q_beb_rb.get()	
			#msg[0] = ip
			d = delivered.get(msg[0],None)
			if d == None: 
				delivered.put(msg)
				q_rb_beb.put(msg)
				q_rb_co.put(msg)

class BestEfforBroadcast():
    def broadcast(self, q_rb_beb, q_beb_pp):
        while True:
            msg = q_rb_beb.get()
            # send N vezes para os usuarios
            for u in users:
                data = [u, msg]
                q_beb_pp.put(data)
    
    def deliver(self, q_pp_beb, q_beb_rb):
        while True:
            data = q_pp_beb.get()
            #msg = '[{}] {}'.format(data[0][0], data[1]) # msg, user
            msg = [data[0][0], data[1]]
            q_beb_rb.put(msg)

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
    co_broadcast_t = threading.Thread(target=co.broadcast, args=[qAC, qCR])
    co_deliver_t = threading.Thread(target=co.deliver, args=[qRC, qCA])
    co_broadcast_t.start()
    co_deliver_t.start()

    rb = ReliableBroadcast()
    rb_broadcast_t = threading.Thread(target=rb.broadcast, args=[qCR, qRB])
    rb_deliver_t = threading.Thread(target=rb.deliver, args=[qBR, qRC])
    rb_broadcast_t.start()
    rb_deliver_t.start()

    beb = BestEfforBroadcast()
    broadcast_t = threading.Thread(target=beb.broadcast, args=[qRB, qBP])
    deliver_t = threading.Thread(target=beb.deliver, args=[qPB, qBR])
    broadcast_t.start()
    deliver_t.start()

    pp2pl = PerfectPoint2PointLinks()
    send_t = threading.Thread(target=pp2pl.send, args=[qBP])
    server_t = threading.Thread(target=pp2pl.server, args=[args.ip, qPB])
    send_t.start()
    server_t.start()

    kbd_t.join()
    display_t.join()
