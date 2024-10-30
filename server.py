import socket
import threading

class UDPChatServer:
    def __init__(self, ip='127.0.0.1', port=12345, password='secret'):
        self.server_ip = ip
        self.server_port = port
        self.password = password
        self.clients = {}  
        

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        print(f"[SERVER STARTED] Listening on {self.server_ip}:{self.server_port}")
    
    def handle_messages(self):
        while True:
            message, client_addr = self.server_socket.recvfrom(1024)
            message = message.decode('utf-8')
            

            if client_addr not in self.clients:
                if message.startswith("PASSWORD:"):
                    if message.split(":")[1] == self.password:

                        self.server_socket.sendto("Enter your username:".encode('utf-8'), client_addr)
                        username, _ = self.server_socket.recvfrom(1024)
                        username = username.decode('utf-8')
                        

                        self.clients[client_addr] = username
                        print(f"[NEW CONNECTION] {username} has joined from {client_addr}")
                        self.broadcast(f"{username} has joined the chat!", client_addr)
                    else:
                        self.server_socket.sendto("Incorrect password!".encode('utf-8'), client_addr)
                continue
            

            username = self.clients[client_addr]
            print(f"[MESSAGE RECEIVED] {username}: {message}")
            self.broadcast(f"{username}: {message}", client_addr)
    
    def broadcast(self, message, sender_addr):

        for client_addr in self.clients:
            if client_addr != sender_addr:
                self.server_socket.sendto(message.encode('utf-8'), client_addr)
    
    def start(self):
        print("[SERVER ACTIVE] Waiting for messages...")
        self.handle_messages()


if __name__ == "__main__":
    server = UDPChatServer()
    server.start()