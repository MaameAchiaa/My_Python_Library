
#import required modules
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# This is a simple chat server that allows multiple clients to connect and communicate with each other.
# It uses sockets for communication and threading to handle multiple clients simultaneously.
# It listens for incoming connections, receives messages from clients, and broadcasts them to all connected clients.
# It also handles client disconnections and displays messages in a GUI window.
IP_SERVER = "localhost"
PORT = 10000
ADDRESS = (IP_SERVER, PORT)
active_clients = [] # List of curently connected users

# This is the GUI class for the chat server application.
class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application Server")
        self.root.geometry("800x600")

        self.create_widgets()
        self.server_running = False
        self.server_socket = None

    def create_widgets(self):
        #Server Controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        #Log Display
        self.log_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=20, state=tk.DISABLED)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        #Client List
        client_frame = tk.Frame(self.root)
        client_frame.pack(pady=10, fill=tk.X)

        tk.Label(client_frame, text="Connected Clients:").pack(side=tk.LEFT, padx=10)
        self.client_listbox = tk.Listbox(client_frame, width=50)
        self.client_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    def log_message(self, message):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)


    def update_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for client in active_clients:
            self.client_listbox.insert(tk.END, client[0])

    
    def start_server(self):     
        try:
            self.server_socket = socket.socket()
            self.server_socket.bind(ADDRESS)
            self.server_socket.listen(5)

            self.server_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            self.log_message("Server STARTED...")

            accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            accept_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")


    def stop_server(self):
            self.server_running = False
            try:
                 for client in active_clients:
                     client[1].close()
                 active_clients.clear()
                 if self.server_socket:
                        self.server_socket.close()
                 self.update_client_list()
                 self.log_message("Server STOPPED.")
                     
            except Exception as e:
                self.log_message(f"Error stopping server: {str(e)}")
            finally:
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                

    def accept_connections(self):
         while self.server_running:
             try:
                connection, address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.client_Handler, args=(connection,), daemon=True)
                client_thread.start()

             except Exception:
                break
               
    
    #Function to handle client
    def client_Handler(self, connection):
        username = ""
        user_added = False
        try:
            #Server will listen to the client until the client sends a username
           username = connection.recv(2050).decode("utf-8")
           if username:
                active_clients.append((username, connection))
                user_added = True
                self.log_message(f"{username} has joined the chat!")
                self.update_client_list()
                self.send_message_to_all(f"SERVER~{username} has joined the chat!")
                self.message_from_client(connection, username)

        except Exception as e:
            self.log_message(f"Error handling client {username}: {str(e)}")
        finally:
            if user_added:
                self.remove_client(connection, username)
            

#Function to remove client from active clients list
    def remove_client(self, connection, username):
     for i, client in enumerate(active_clients):
          if client[1] == connection:
               username = client[0]
               active_clients.pop(i)
               self.log_message(f"{username} has left the chat.")
               self.update_client_list()
               self.send_message_to_all(f"SERVER~{username} has left the chat.")
               break
               

#Function to receive message from client and send it to all other clients
    def message_from_client(self, connection, username):
        while self.server_running:
            try:
                message = connection.recv(2050).decode("utf-8")
                if not message:
                    break
                if message == "exit":
                    break       
                if message.startswith("/private"):
                  #Format: /private receipient_username message_content
                  parts = message.split(" ", 2)
                  if len(parts) == 3:
                     receipient, private_msg = parts[1], parts[2]
                     self.send_private_message(username, receipient, private_msg)
                  else:
                       self.send_message_to_client(connection, "SERVER~Invalid private message format. Use /private <username> <message>")
                elif message == "/list":
                    self.send_client_list(connection)
                else:
                    final_msg = f"{username}~{message}"
                    self.send_message_to_all(final_msg)
            except Exception:
                break          
                       
#Function to send message to a single client
    def send_private_message(self, sender, recipient, private_msg):
        found = False
        for client in active_clients:
            if client[0] == recipient:
                try:
                    msg = f"[PRIVATE] {sender} ~ {private_msg}"
                    client[1].send(msg.encode("utf-8"))
                    found = True
                except Exception:
                    pass
                break
        #Notify sender if recipient not found
        for client in active_clients:
            if client[0] == sender:
                try:
                    if found:
                        client[1].send(f"[PRIVATE] to {recipient}~{private_msg}".encode("utf-8"))
                    else:
                        client[1].send(f"SERVER~User '{recipient}' not found or offline.".encode("utf-8"))
                except Exception:
                    pass
                break
           

    def send_message_to_client(self, connection, message):
        try:
            connection.send(message.encode("utf-8"))
        except Exception:
            pass


    def send_message_to_all(self, message):
      for client in active_clients:
          try:
              client[1].send(message.encode("utf-8"))
          except Exception:
              pass
          
    def send_client_list(self, connection):
        user_list = "\n".join([client[0] for client in active_clients])
        try:
            connection.send(f"CLIENTLIST~{user_list}".encode("utf-8"))
        except Exception:
            pass
                 

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()

    
