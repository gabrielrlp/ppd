import socket
import threading
import pickle
import Queue
import time

port = 8066

class PerfectPoint2PointLinks():         
    def server(self, host, q_pp_beb, users_len):
        s = socket.socket()
        s.bind((host, port))
        s.listen(users_len)
        while True:
            c, addr = s.accept()
            t = threading.Thread(target=self.deliver, args=[c, addr, q_pp_beb])
            t.start()

    def deliver(self, client, source, q_pp_beb):
        while True:
            # Data received from client
            data = client.recv(1024)
            if data:
                data_arr = pickle.loads(data)
                # Compose the message to populate the FIFO
                data_arr.append(source[0])
                # Put the message into the FIFO
                q_pp_beb.put(data_arr)

    def send(self, q_beb_pp):
        connections = {}

        while True:
            data = q_beb_pp.get()
            queue = connections.get(data[-1], None)
            if queue == None:
                q = Queue.Queue()
                q.put(data)
                connections.update([(data[-1], q)])
                t = threading.Thread(target=self.send_t, args=[q])
                t.start()
            else:
                queue.put(data)

    def send_t(self, queue):
        data = queue.get()

        s = socket.socket()
        s.connect((data[-1], port))

        while True:
            del data[-1]
            data_str = pickle.dumps(data)
            s.sendall(data_str)
            data = queue.get()