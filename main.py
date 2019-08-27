# coding=utf-8
import socket
import argparse
import threading
import time

# Arguments Parsing Settings
parser = argparse.ArgumentParser()
parser.add_argument('--ip', help="The current machine IP address.", required=True)

users = ['15.29.225.115', '15.8.142.92']
port = 8066

class Application():
    def listener(self):
        for u in users:
            t = PerfectPoint(u, port)
            t.start()
            # t.join()

    def input(self):
        while (True):
            msg = raw_input('>>> ')
            print(msg)

class BestEfforBroadcast():
    def broadcast(self, msg):
        print(msg)
    
    def deliver(self, p, msg):
        print(p, msg)

class PerfectPoint(threading.Thread):
    def __init__(self, ip, port):
	    # super(MyThread, self).__init__(group=group, target=target, name=name, verbose=verbose)
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = None
    
    def run(self):
        self.__connect(self.ip, self.port)

    def send(self, dest, msg):
        print(dest, msg)
    
    def deliver(self, src, msg):
        print(src, msg)

    def __connect(self, ip, port):
        """
        Cria conexão com outro usuário
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        timeout = time.time() + 10 # segundos para o timeout
        while True:
            if time.time() > timeout:
                break
            
            try:
                self.sock.connect((ip, port))
                break
            except Exception as e:
                pass
                # print(e)

        print('aham')
        # testar se a conexão foi estabelecida
        # começar a manipular as FIFOs

if __name__ == '__main__':
    # Input arguments parser
    args = parser.parse_args()
    # Remove self IP from users array
    users.remove(args.ip)

    api = Application()
    # Thread to listening connections
    listener_t = threading.Thread(target=api.listener)
    # Thread to reading the keyboard
    input_t = threading.Thread(target=api.input)
    
    listener_t.start()
    input_t.start()

    listener_t.join()
    input_t.join()  