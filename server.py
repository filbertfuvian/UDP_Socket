import socket
import threading
import time
import binascii  # Untuk menghitung checksum CRC32
import struct    # Untuk mengemas data dengan checksum

class UDPChatServer:
    def __init__(self, ip='127.0.0.1', port=12345, password='secret', caesar_shift=3):
        self.server_ip = ip
        self.server_port = port
        self.password = password
        self.clients = {}
        self.acknowledgments = {}
        self.lock = threading.Lock()
        self.caesar_shift = caesar_shift
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        print(f"[SERVER STARTED] Listening on {self.server_ip}:{self.server_port}")
    
    def caesar_encrypt(self, text):
        result = ""
        for char in text:
            if char.isalpha():
                shift = 65 if char.isupper() else 97
                result += chr((ord(char) + self.caesar_shift - shift) % 26 + shift)
            else:
                result += char
        return result

    def caesar_decrypt(self, text):
        result = ""
        for char in text:
            if char.isalpha():
                shift = 65 if char.isupper() else 97
                result += chr((ord(char) - self.caesar_shift - shift) % 26 + shift)
            else:
                result += char
        return result

    def calculate_checksum(self, data):
        return binascii.crc32(data.encode('utf-8'))

    def handle_messages(self):
        while True:
            message, client_addr = self.server_socket.recvfrom(4096)
            message = message.decode('utf-8')
            
            # Check if client is new and needs to authenticate
            if client_addr not in self.clients:
                if message.startswith("PASSWORD:"):
                    if message.split(":")[1] == self.password:
                        self.server_socket.sendto("Enter your username:".encode('utf-8'), client_addr)
                        username, _ = self.server_socket.recvfrom(1024)
                        username = username.decode('utf-8')
                        with self.lock:
                            self.clients[client_addr] = username
                            self.acknowledgments[client_addr] = 0
                        print(f"[NEW CONNECTION] {username} has joined from {client_addr}")
                        self.broadcast(f"{username} has joined the chat!", client_addr)
                    else:
                        self.server_socket.sendto("Incorrect password!".encode('utf-8'), client_addr)
                continue
            
            # Handle incoming message
            seq, checksum, msg_content = message.split(":", 2)
            seq = int(seq)
            received_checksum = int(checksum)
            decrypted_message = self.caesar_decrypt(msg_content)
            calculated_checksum = self.calculate_checksum(decrypted_message)
            
            if received_checksum != calculated_checksum:
                print(f"[ERROR] Message from {client_addr} is corrupted!")
                continue
            
            username = self.clients[client_addr]
            print(f"[MESSAGE RECEIVED] {username}: {decrypted_message}")
            
            # Send ACK back to the client
            ack_message = f"ACK:{seq}"
            self.server_socket.sendto(ack_message.encode('utf-8'), client_addr)
            
            # Broadcast message if it has correct sequence
            with self.lock:
                if seq == self.acknowledgments[client_addr]:
                    self.broadcast(f"{username}: {decrypted_message}", client_addr)
                    self.acknowledgments[client_addr] += 1

    def broadcast(self, message, sender_addr):
        encrypted_message = self.caesar_encrypt(message)
        checksum = self.calculate_checksum(message)
        for client_addr in self.clients:
            if client_addr != sender_addr:
                message_with_checksum = f"{checksum}:{encrypted_message}"
                self.server_socket.sendto(message_with_checksum.encode('utf-8'), client_addr)
    
    def start(self):
        print("[SERVER ACTIVE] Waiting for messages...")
        self.handle_messages()

if __name__ == "__main__":
    server = UDPChatServer()
    server.start()
