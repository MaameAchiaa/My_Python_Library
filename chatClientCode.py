
#import required modues
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

IP_SERVER = "localhost"
PORT = 10000
ADDRESS = (IP_SERVER, PORT)

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application Client")
        self.root.geometry("800x600")

        self.username = ""
        self.client_socket = None
        self.connected = False

        self.create_widgets()

    def create_widgets(self):
        #Connection Frame
        connection_frame = tk.Frame(self.root)
        connection_frame.pack(pady=10)

        tk.Label(connection_frame, text="Username:").pack(side=tk.LEFT, padx=10)
        self.username_entry = tk.Entry(connection_frame)
        self.username_entry.pack(side=tk.LEFT, padx=10)

        self.connect_button = tk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=10)

        self.disconnect_button = tk.Button(connection_frame, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=10)


        #Chat Display
        self.chat_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)


        #Message Entry
        message_frame = tk.Frame(self.root)
        message_frame.pack(pady=10, fill=tk.X)

        self.message_entry = tk.Entry(message_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(message_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_button.pack(side=tk.LEFT, padx=10)


        #Private Message Button
        self.private_button = tk.Button(message_frame, text="Private Message", command=self.send_private_message, state=tk.DISABLED)
        self.private_button.pack(side=tk.LEFT, padx=10)

        #Client List
        client_frame = tk.Frame(self.root)
        client_frame.pack(pady=10, fill=tk.X)

        tk.Label(client_frame, text="Connected Clients:").pack(anchor=tk.W)
        self.client_listbox = tk.Listbox(client_frame, width=50)
        self.client_listbox.pack(fill=tk.BOTH, expand=True)
        self.client_listbox.bind("<Double-Button-1>", self.start_private_chat)


    def log_message(self, message):
        self.chat_text.config(state='normal')
        self.chat_text.insert(tk.END, message + "\n")
        self.chat_text.config(state='disabled')
        self.chat_text.see(tk.END)


    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        try:
            self.client_socket = socket.socket()
            self.client_socket.connect(ADDRESS)

            #Send username to server
            self.client_socket.send(self.username.encode("utf-8"))

            self.connected = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.private_button.config(state=tk.NORMAL)
            self.username_entry.config(state=tk.DISABLED)


            self.log_message(f"Connected to server as {self.username}")

            receive_thread = threading.Thread(target=self.message_from_server, daemon=True)
            receive_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {str(e)}")


    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.send("exit".encode("utf-8"))
                self.client_socket.close()

            except:
                pass

        self.connected = False
        self.client_socket = None

        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.private_button.config(state=tk.DISABLED)
        self.username_entry.config(state=tk.NORMAL)

        self.log_message("Disconnected from server")
           
            
    def message_from_server(self):
        while self.connected:
            try:
                message = self.client_socket.recv(2050).decode("utf-8")
                if not message:
                    break

                if message.startswith("CLIENTLIST~"):
                    user_list = message.split("~", 1)[1]
                    self.update_client_list(user_list)
                elif message.startswith("SERVER~"):
                    self.log_message(message.split("~", 1)[1])
                    if "has joined the chat!" in message or "has left the chat!" in message:
                        self.request_client_list()
                elif message.startswith("[PRIVATE]"):
                    self.chat_text.tag_config("private", foreground="green")
                    self.chat_text.config(state='normal')
                    self.chat_text.insert(tk.END, message + "\n", "private")
                    self.chat_text.config(state='disabled')
                elif "~" in message:
                    sender, msg = message.split("~", 1)
                    self.log_message(f"{sender}: {msg}")
                else:
                    self.log_message(message)
            except Exception as e:
                if self.connected:
                    self.log_message(f"Connection lost: {str(e)}")
                break

        

    def request_client_list(self):
        if self.connected:
            try:
                self.client_socket.send(f"/list".encode("utf-8"))
                #The server will respond with the list, which you can handle in message_from_server

            except:
                self.disconnect_from_server()


    def update_client_list(self, user_list):
        self.client_listbox.delete(0, tk.END)
        for user in user_list.split("\n"):
            if user and user != self.username:
               self.client_listbox.insert(tk.END, user)
               

    def send_message(self, _event=None):
        if not self.connected:
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            self.client_socket.send(message.encode("utf-8"))
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.log_message(f"Error sending message: {str(e)}")
            self.disconnect_from_server()


    def start_private_chat(self, event):
        selection = self.client_listbox.curselection()
        if selection:
            recipient = self.client_listbox.get(selection[0])
            message = simpledialog.askstring("Private Message", f"Message to {recipient}:", parent=self.root)

            if message:
                self.send_private_message_to_user(recipient, message)


    def send_private_message(self):
        recipient = simpledialog.askstring("Private Message", "Enter recipient username:", parent=self.root)

        if recipient:
            message = simpledialog.askstring("Private Message", f"Message to {recipient}:", parent=self.root)

            if message:
                self.send_private_message_to_user(recipient, message)


    def send_private_message_to_user(self, recipient, message):
        if not self.connected:
            return
        
        try:
            private_msg = f"/private {recipient} {message}"
            self.client_socket.send(private_msg.encode("utf-8"))

        except Exception as e:
            self.log_message(f"Error sending private message: {str(e)}")
            self.disconnect_from_server()
    


if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ChatClientGUI(root)
    root.mainloop()
