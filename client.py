import socket
import threading
import time
import binascii  # Untuk menghitung checksum CRC32
import struct    # Untuk mengemas data dengan checksum

class UDPChatClient:
    def __init__(self, server_ip, server_port, password, username, caesar_shift=3):
        self.server_ip = server_ip
        self.server_port = server_port
        self.password = password
        self.username = username
        self.sequence_number = 0
        self.ack_received = threading.Event()
        self.caesar_shift = caesar_shift
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.authenticate()
    
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

    def send_message(self, message):
        encrypted_message = self.caesar_encrypt(message)
        checksum = self.calculate_checksum(message)
        message_with_seq = f"{self.sequence_number}:{checksum}:{encrypted_message}"
        self.client_socket.sendto(message_with_seq.encode('utf-8'), (self.server_ip, self.server_port))
        
        if self.ack_received.wait(timeout=5):
            self.sequence_number += 1
            self.ack_received.clear()
        else:
            print("[ERROR] Timeout, message will be resent")
            self.send_message(message)

    def receive_messages(self):
        while True:
            message, _ = self.client_socket.recvfrom(4096)
            message = message.decode('utf-8')
            
            if message.startswith("ACK:"):
                ack_seq = int(message.split(":")[1])
                if ack_seq == self.sequence_number:
                    self.ack_received.set()
            else:
                checksum, msg_content = message.split(":", 1)
                calculated_checksum = self.calculate_checksum(msg_content)
                
                if int(checksum) != calculated_checksum:
                    print("[ERROR] Received message is corrupted!")
                else:
                    decrypted_message = self.caesar_decrypt(msg_content)
                    print(decrypted_message)

    def start(self):
        while True:
            command = input("")
            if command.startswith("sendfile "):
                filepath = command.split(" ", 1)[1]
                self.send_file(filepath)
            else:
                self.send_message(command)

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    password = input("Enter password: ")
    username = input("Enter your username: ")
    
    client = UDPChatClient(server_ip, server_port, password, username)
    client.start()
