import socket
import threading
import time
import binascii
import os

class UDPChatServer:
    def __init__(self, ip='127.0.0.1', port=12345, password='secret', caesar_shift=3):
        self.server_ip = ip
        self.server_port = port
        self.password = password
        self.caesar_shift = caesar_shift
        self.clients = {}
        self.acknowledgments = {}
        self.lock = threading.Lock()
        self.chat_history_file = "server_chat_history.txt"

        # Inisialisasi socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.server_socket.bind((self.server_ip, self.server_port))
            print(f"[SERVER STARTED] Listening on {self.server_ip}:{self.server_port}")
        except socket.error as e:
            print(f"[ERROR] Server bind failed: {e}")
            self.server_socket.close()
            raise

    def encrypt(self, text, shift):
        result = ""
        for char in text:
            if char.isalpha():
                base = 65 if char.isupper() else 97
                result += chr((ord(char) + shift - base) % 26 + base)
            else:
                result += char
        return result

    def decrypt(self, text, shift):
        return self.encrypt(text, -shift)

    def calculate_checksum(self, data):
        return binascii.crc32(data.encode('utf-8'))

    def save_message(self, message):
        try:
            with open(self.chat_history_file, "a") as f:
                f.write(message + "\n")
        except IOError as e:
            print(f"[ERROR] Failed to save message: {e}")

    def handle_client_auth(self, message, client_addr):
        if message.split(":")[1] == self.password:
            self.server_socket.sendto("Enter your username:".encode('utf-8'), client_addr)
            username, _ = self.server_socket.recvfrom(1024)
            username = username.decode('utf-8')
            with self.lock:
                self.clients[client_addr] = username
                self.acknowledgments[client_addr] = 0
            print(f"[NEW CONNECTION] {username} has joined from {client_addr}")
            self.broadcast(f"{username} has joined the chat!", client_addr)
            self.save_message(f"[NEW CONNECTION] {username} has joined from {client_addr}")
        else:
            self.server_socket.sendto("Incorrect password!".encode('utf-8'), client_addr)

    def handle_messages(self):
        while True:
            try:
                message, client_addr = self.server_socket.recvfrom(4096)
                message = message.decode('utf-8')

                if client_addr not in self.clients:
                    if message.startswith("PASSWORD:"):
                        self.handle_client_auth(message, client_addr)
                    continue

                seq, checksum, msg_content = message.split(":", 2)
                seq = int(seq)
                received_checksum = int(checksum)
                decrypted_message = self.decrypt(msg_content, self.caesar_shift)
                calculated_checksum = self.calculate_checksum(decrypted_message)

                if received_checksum != calculated_checksum:
                    print(f"[ERROR] Message from {client_addr} is corrupted!")
                    continue

                username = self.clients[client_addr]
                log_message = f"[MESSAGE RECEIVED] {username}: {decrypted_message}"
                print(log_message)
                self.save_message(log_message)

                ack_message = f"ACK:{seq}"
                self.server_socket.sendto(ack_message.encode('utf-8'), client_addr)

                with self.lock:
                    if seq == self.acknowledgments[client_addr]:
                        self.broadcast(f"{username}: {decrypted_message}", client_addr)
                        self.acknowledgments[client_addr] += 1
            except Exception as e:
                print(f"[ERROR] {e}")

    def broadcast(self, message, sender_addr):
        encrypted_message = self.encrypt(message, self.caesar_shift)
        checksum = self.calculate_checksum(message)
        self.save_message(message)
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