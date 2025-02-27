# network.py
import socket
import threading
import queue

class NetworkClient:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.sock = None
        self.recv_queue = queue.Queue()
        self.running = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.running = True
        threading.Thread(target=self.listen, daemon=True).start()
        print("[Network] Connected to server at {}:{}".format(self.host, self.port))

    def listen(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if data:
                    message = data.decode()
                    self.recv_queue.put(message)
                    print("[Network] Received:", message)
                else:
                    self.running = False
            except Exception as e:
                print("[Network] Listen error:", e)
                self.running = False
                break

    def send(self, message):
        try:
            self.sock.sendall(message.encode())
            print("[Network] Sent:", message)
        except Exception as e:
            print("[Network] Send error:", e)

    def get_message(self):
        if not self.recv_queue.empty():
            return self.recv_queue.get()
        return None

    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()
