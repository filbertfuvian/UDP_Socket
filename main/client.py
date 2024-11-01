import socket
import threading
import binascii
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, filedialog
import os

class UDPChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Chat Client")
        
        # display utama dari GUI
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=10, pady=5, expand=True, fill=tk.BOTH)
        
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.file_button = tk.Button(self.root, text="Send File", command=self.send_file)
        self.file_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # inisialisasi sisi client
        self.server_ip = None
        self.server_port = None
        self.password = None
        self.username = None
        self.sequence_number = 0
        self.ack_received = threading.Event()
        self.caesar_shift = 3
        self.chat_history_file = "client_chat_history.txt"
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.setup_connection()

    def setup_connection(self):
        """ Prompt for server details and initialize connection """
        self.server_ip = simpledialog.askstring("Server IP", "Enter server IP:", parent=self.root)
        self.server_port = int(simpledialog.askstring("Server Port", "Enter server port:", parent=self.root))
        self.password = simpledialog.askstring("Password", "Enter password:", parent=self.root)
        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        
        self.display_chat_history()
        self.authenticate()

    def authenticate(self):
        """ Authenticate with the server """
        try:
            # Mengirim password ke server
            self.client_socket.sendto(f"PASSWORD:{self.password}".encode('utf-8'), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            
            if response.decode('utf-8') == "Enter your username:":
                # mengirim username ke server
                while True:
                    self.client_socket.sendto(self.username.encode('utf-8'), (self.server_ip, self.server_port))
                    response, _ = self.client_socket.recvfrom(1024)
                    response_message = response.decode('utf-8')
                    
                    if response_message == "Username accepted.":
                        self.add_message("[CONNECTED] Successfully connected to chat server.")
                        break
                    elif response_message == "Username already taken. Please choose a different username.": #jika username sudah ada, response diambil dari server
                        self.username = simpledialog.askstring("Username Taken", "Username is taken. Enter a different username:", parent=self.root)
                    else:
                        self.add_message("[ERROR] Unexpected response from server.")
                        break
                
                # Mulai thread untuk menerima pesan setelah username diterima
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                messagebox.showerror("Error", "Incorrect password!")
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")

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
            self.add_message(f"[ERROR] Failed to save message: {e}")

    def display_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "r") as f:
                self.add_message(f.read(), scroll=False)

    def send_message(self):
        message = self.message_entry.get()
        if not message:
            return
        
        encrypted_message = self.encrypt(message, self.caesar_shift)
        checksum = self.calculate_checksum(message)
        message_with_seq = f"{self.sequence_number}:{checksum}:{encrypted_message}"
        
        print(f"[DEBUG] Sending message: {message_with_seq}")  # Debug
        self.client_socket.sendto(message_with_seq.encode('utf-8'), (self.server_ip, self.server_port))
        self.message_entry.delete(0, tk.END)
        
        if self.ack_received.wait(timeout=5):
            self.sequence_number += 1
            self.ack_received.clear()
            self.save_message(f"{self.username}: {message}")
            self.add_message(f"{self.username}: {message}")
        else:
            self.add_message("[ERROR] Timeout, message will be resent")
            self.send_message()

    def send_file(self):
        """ Allow user to choose a file and send it """
        filepath = filedialog.askopenfilename()
        if not filepath:
            return  # jika tidak ada file yang dipilih, keluar dari fungsi
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
            
            file_message = f"FILE:{filename}:{file_data.hex()}"
            self.client_socket.sendto(file_message.encode('utf-8'), (self.server_ip, self.server_port))
            self.add_message(f"[FILE SENT] {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")

    def receive_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(4096)
                message = message.decode('utf-8')
                print(f"[DEBUG] Raw received message: {message}")

                # menerima pesan Acknowledgement
                if message.startswith("ACK:"):
                    ack_seq = int(message.split(":")[1])
                    if ack_seq == self.sequence_number:
                        self.ack_received.set()
                    continue  # melanjutkan proses
                
                elif message.startswith("FILE:"):
                    # mengatur file
                    _, filename, filedata_hex = message.split(":", 2)
                    filedata = bytes.fromhex(filedata_hex)
                    with open(filename, 'wb') as f:
                        f.write(filedata)
                    self.add_message(f"[FILE RECEIVED] {filename}")
                    continue  
                
            
                try:
                    received_checksum, encrypted_message = message.split(":", 1)
                    received_checksum = int(received_checksum)
                except ValueError:
                    print("[ERROR] Incorrect message format received!")
                    continue

                # melakukan decrypt pesan
                decrypted_message = self.decrypt(encrypted_message, self.caesar_shift)
                print(f"[DEBUG] Decrypted message: {decrypted_message}")

                
                calculated_checksum = self.calculate_checksum(decrypted_message)
                print(f"[DEBUG] Received checksum: {received_checksum}, Calculated checksum: {calculated_checksum}")

                
                if received_checksum != calculated_checksum:
                    self.add_message("[ERROR] Received message is corrupted!")
                else:
                    self.add_message(decrypted_message)
                    self.save_message(decrypted_message)
            except Exception as e:
                self.add_message(f"[ERROR] {e}")

    def add_message(self, message, scroll=True):
        """ Add a message to the chat area """
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        if scroll:
            self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = UDPChatClientGUI(root)
    root.mainloop()