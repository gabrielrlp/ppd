import socket
import pickle
import Queue
import time
from threading import Thread

port = 8066

class PerfectPoint2PointLinks():         
    def deliver(self, host, q_pp_beb, users_len):
        """
        Await for a connection request to start a new thread that will being listening
        this request for all the time.
        :param host: The host IP (e.g., 192.168.17.2)
        :param q_pp_beb: A python Queue object that being used between 
        the Perfect Point to Point Links and the Best Effort Broadcast.
        :param users_len: The users dictionary length (number of maximum connections).
        """
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(users_len)
        while True:
            c, addr = s.accept()
            t = Thread(target=self.deliver_t, args=[c, addr, q_pp_beb])
            t.start()

    def deliver_t(self, client, source, q_pp_beb):
        """
        Connection listener. Receive a data from the connection and delivers it
        to the next Queue to be manipulated.
        :param client: A python socket object.
        :param source: Source address from comunication.
        :param q_pp_beb: A python Queue object that being used between 
        the Perfect Point to Point Links and the Best Effort Broadcast.
        """
        while True:
            # Data received from client
            data = client.recv(1024)
            if data:
                data_arr = pickle.loads(data)
                # Put the message into the FIFO
                q_pp_beb.put(data_arr)

    def broadcast(self, q_beb_pp):
        """
        Create a dedicated broadcast thread to each target (user).
        :param q_beb_pp: A python Queue object that being used between 
        the Best Effort Broadcast and the Perfect Point to Point Links.
        """
        connections = {}

        while True:
            data = q_beb_pp.get()
            queue = connections.get(data[-1], None)
            if queue == None:
                q = Queue.Queue()
                q.put(data)
                connections.update([(data[-1], q)])
                t = Thread(target=self.broadcast_t, args=[q])
                t.start()
            else:
                queue.put(data)

    def broadcast_t(self, queue):
        """
        Tries to get a data from the dedicated queue and send it
        to the target by the network.
        :param queue: A dedicated queue to be monitoring.
        """
        data = queue.get()

        s = socket.socket()
        s.connect((data[-1], port))

        while True:
            del data[-1]
            data_str = pickle.dumps(data)
            s.sendall(data_str)
            data = queue.get()