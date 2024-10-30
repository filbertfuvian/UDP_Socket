import socket
import threading

class UDPChatClient:
    def __init__(self, server_ip, server_port, password, username):
        self.server_ip = server_ip
        self.server_port = server_port
        self.password = password
        self.username = username
        

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        

        self.authenticate()
    
    def authenticate(self):

        self.client_socket.sendto(f"PASSWORD:{self.password}".encode('utf-8'), (self.server_ip, self.server_port))
        

        response, _ = self.client_socket.recvfrom(1024)
        if response.decode('utf-8') == "Enter your username:":

            self.client_socket.sendto(self.username.encode('utf-8'), (self.server_ip, self.server_port))
            print("[CONNECTED] Successfully connected to chat server.")
            threading.Thread(target=self.receive_messages).start()
        else:
            print("[ERROR] Incorrect password!")
    
    def send_message(self, message):

        self.client_socket.sendto(message.encode('utf-8'), (self.server_ip, self.server_port))
    
    def receive_messages(self):

        while True:
            message, _ = self.client_socket.recvfrom(1024)
            print(message.decode('utf-8'))
    
    def start(self):
        while True:
            message = input()
            self.send_message(message)


if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    password = input("Enter password: ")
    username = input("Enter your username: ")
    
    client = UDPChatClient(server_ip, server_port, password, username)
    client.start()