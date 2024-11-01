import socket
import threading
import binascii
import os

class UDPChatServer:
    def __init__(self, ip='192.168.100.73', port=12345, password='secret', caesar_shift=3):
        # Inisialisasi server dan atribut lain
        self.server_ip = ip
        self.server_port = port
        self.password = password
        self.caesar_shift = caesar_shift
        self.clients = {}
        self.acknowledgments = {}
        self.lock = threading.Lock()
        self.chat_history_file = "server_chat_history.txt"
        self.files_folder = "received_files"

        if not os.path.exists(self.files_folder):
            os.makedirs(self.files_folder)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.server_socket.bind((self.server_ip, self.server_port))
            print(f"[SERVER STARTED] Listening on {self.server_ip}:{self.server_port}")
        except socket.error as e:
            print(f"[ERROR] Server bind failed: {e}")
            self.server_socket.close()
            raise

    # Tambahkan fungsi is_username_taken di sini
    def is_username_taken(self, username):
        return username in self.clients.values()

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
    
    # untuk mengecek apakah username unique atau tidak
    def is_username_taken(self, username):
        with self.lock:
            return username in self.clients.values()

    def handle_client_auth(self, message, client_addr):
        if message.split(":")[1] == self.password:
            self.server_socket.sendto("Enter your username:".encode('utf-8'), client_addr)
            
            while True:
                username, _ = self.server_socket.recvfrom(1024)
                username = username.decode('utf-8')
                
                if self.is_username_taken(username):
                    self.server_socket.sendto("Username already taken. Please choose a different username.".encode('utf-8'), client_addr)
                else:
                    with self.lock:
                        self.clients[client_addr] = username
                        self.acknowledgments[client_addr] = 0
                    self.server_socket.sendto("Username accepted.".encode('utf-8'), client_addr)
                    print(f"[NEW CONNECTION] {username} has joined from {client_addr}")
                    self.broadcast(f"{username} has joined the chat!", client_addr)
                    self.save_message(f"[NEW CONNECTION] {username} has joined from {client_addr}")
                    break
        else:
            self.server_socket.sendto("Incorrect password!".encode('utf-8'), client_addr)


    def handle_messages(self):
        while True:
            try:
                message, client_addr = self.server_socket.recvfrom(4096)
                message = message.decode('utf-8')
                print(f"[DEBUG] Raw message from {client_addr}: {message}")

                if client_addr not in self.clients:
                    if message.startswith("PASSWORD:"):
                        self.handle_client_auth(message, client_addr)
                    continue

                if message.startswith("FILE:"):
                    # Parse the file message format: "FILE:filename:filedata_in_hex"
                    _, filename, filedata_hex = message.split(":", 2)
                    filedata = bytes.fromhex(filedata_hex)
                    
                    # Define the file path within the "received_files" folder
                    file_path = os.path.join(self.files_folder, filename)

                    # Save the file
                    with open(file_path, 'wb') as f:
                        f.write(filedata)
                    print(f"[FILE RECEIVED] {filename} saved to {file_path}")
                    self.save_message(f"[FILE RECEIVED] {filename} from {client_addr}")
                    
                    # Broadcast file notification to other clients
                    self.broadcast(f"FILE:{filename}:{filedata_hex}", client_addr)
                else:
                    # Text message handling code (no changes needed)
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
        if message.startswith("FILE:"):
            # Directly broadcast the file message to all clients
            for client_addr in self.clients:
                if client_addr != sender_addr:
                    self.server_socket.sendto(message.encode('utf-8'), client_addr)
        else:
            # For regular messages
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