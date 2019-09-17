# coding=utf-8
import socket
import argparse
import threading
from threading import Lock
import Queue
import time
import json

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help="The current machine IP address.", required=True)

#users = ['10.32.169.44', '10.32.169.74', '10.32.169.54']
users = ['localhost']
port = 8066

class Application():
    def keyboard(self, q_api_co):
        while True:
            raw_msg = raw_input('>>> ')
            msg = [raw_msg, time.time()]
            print("api data: ", msg)
            q_api_co.put(msg)

    def display(self, q_co_api):
        while True:
            print(q_co_api.get())

class CausalOrderBroadcast():
    def broadcast(self, q_api_co, q_co_rb, V):
        lsn = 0
        while True:
            m = q_api_co.get()
            W = V
            W[0] = lsn
            lsn += 1
            #data = [W, m]
            m.append(W)
            print("CO data: ", m)
            q_co_rb.put(m)
    
    def deliver(self, q_rb_co, q_co_api, V, mutex):
        pending = []
        while True:
            data = None
            try:
                data = q_rb_co.get_nowait()
            except:
                pass
            if data:
                pending.append(data)
            for p in pending:
                mutex.acquire()
                print("CO data deliver",data)
                mutex.release()         

class ReliableBroadcast():
	def broadcast(self, q_co_rb, q_rb_beb):
		while True:
			msg = q_co_rb.get()
			print("RB data: ", msg)
			q_rb_beb.put(msg)

	def deliver(self, q_rb_beb, q_beb_rb, q_rb_co):
		delivered = {}
		while True:
			msg = q_beb_rb.get() 
			# print("RB data deliver[0]: ",msg[0])
			# print("RB data deliver[2]: ",msg[2])
			#msg[0]: ip e  msg[2]: time
			ip = delivered.get(msg[0],None)
			time = delivered.get(msg[2],None)
			if ip == None and time == None: 
				delivered.update(msg)
				q_rb_beb.put(msg)
				q_rb_co.put(msg)

class BestEfforBroadcast():
    def broadcast(self, q_rb_beb, q_beb_pp):
        while True:
            msg = q_rb_beb.get()
            # send N vezes para os usuarios
            for u in users:
                # data = [u, msg]
                msg.insert(0,u) #insere ip na posição 0
                print("BEB data: ", msg)
                q_beb_pp.put(msg)
    
    def deliver(self, q_pp_beb, q_beb_rb):
        while True:
            data = q_pp_beb.get()
            #msg = '[{}] {}'.format(data[0][0], data[1]) # msg, user
            #msg = [data[0][0], data[1]]#, data[2]]
            print("BEB data deliver: ",data)
            q_beb_rb.put(data)

class PerfectPoint2PointLinks():         
    def server(self, host, q_pp_beb):
        # pass
        s = socket.socket()
        s.bind((host, port))
        s.listen(len(users))
        while True:
            c, addr = s.accept()
            t = threading.Thread(target=self.deliver, args=[c, addr, q_pp_beb])
            t.start()

    def deliver(self, client, source, q_pp_beb):
        # pass
        while True:
            # Data received from client
            json_string = client.recv(1024)
            data = json.loads(json_string)
            if data:
                # Compose the message to populate the FIFO
                data.insert(0,source[0])
                # Put the message into the FIFO
            	print("pp2pl data deliver: ",data)
                q_pp_beb.put(data)

    def send(self, q_beb_pp):
        connections = {}

        while True:
            data = q_beb_pp.get()
            # print(data)	
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
			# print("pp2pl data: ",data)
			data.pop(0) #remove ip
			msg = json.dumps(data)
			print("pp2pl data: ",msg)
			s.sendall(msg)
			data = queue.get()

if __name__ == '__main__':
    # Input arguments parser
    args = parser.parse_args()

    # Remove self IP from users array
   # users.remove(args.ip)

    mutex_v = Lock()
    V = [0, 0]

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
    co_broadcast_t = threading.Thread(target=co.broadcast, args=[qAC, qCR, V])
    co_deliver_t = threading.Thread(target=co.deliver, args=[qRC, qCA, V, mutex_v])
    co_broadcast_t.start()
    co_deliver_t.start()

    rb = ReliableBroadcast()
    rb_broadcast_t = threading.Thread(target=rb.broadcast, args=[qCR, qRB])
    rb_deliver_t = threading.Thread(target=rb.deliver, args=[qRB, qBR, qRC])
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