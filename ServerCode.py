
import socket
import time
import datetime

IP_Server = 'localhost'
PORT = 12000
ADDRESS = (IP_Server, PORT)

def userRecv():
    msg = int(connection.recv(2000).decode("utf-8"))
    if msg == 1:
        print(f"User requested for time, SUCCESSFULLY SEND TIME TO USER!")
        connection.send(f"TIME -> {time.ctime()}".encode("utf-8"))
    
    elif msg == 2:
        print(f"User requested for today's date, SUCCESSFULLY SEND TODAY'S DATE TO USER!")
        connection.send(f"Date -> {datetime.datetime.now()}".encode("utf-8"))

    else:
        print("User entered an invalid input, FAIL!")
        connection.send("Sorry your input is not included in our service.".encode("utf-8"))

serverSocket = socket.socket()

serverSocket.bind(ADDRESS)
print("Server Started...")

serverSocket.listen(5)

lstOfQuestions = ["What time is it", "What is today's date"]

while True:
    connection, address = serverSocket.accept()

    print(f"User CONNECTED -> {address}")

    connection.send(f"Hello Client, Ask the following questions\n{lstOfQuestions}".encode("utf-8"))

    userRecv()







#import required modules
import socket
import threading
import tkinter as tk

IP_SERVER = "localhost"
PORT = 10000
ADDRESS = (IP_SERVER, PORT)
active_clients = [] # List of curently connected users

#Function to receive message from client and send it to all other clients
def message_from_client(connection, username):
     while True:
          message = connection.recv(2050).decode("utf-8")
          if message != '':
               
               final_msg = username + '~' + message
               send_messages_to_all(final_msg)
          
          else:
               print(f"The message sent from {username} is empty")
               exit(0)


#Function to send message to a single client
def send_message_to_client(connection, message):
     
     connection.sendall(message.encode("utf-8"))
    

#Function to send new message to all clients currently connected to the server
def send_messages_to_all(message):
    for user in active_clients:

        send_message_to_client(user[1], message)
        
        
#Function to handle client
def client_Handler(connection):
        #Server will listen to the client until the client sends a username
        while True:
            #Receiving username from client
            username = connection.recv(2050).decode("utf-8")
            if username != '':
                 active_clients.append((username, connection))
                 prompt_message = "SERVER~" + f"{username}  has joined the chat!"
                 send_messages_to_all(prompt_message)
                 break
            
            else:
                    print("Client's username is empty")


        threading.Thread(target=message_from_client, args=(connection, username, )).start()

#Main Function
def main():
    #Creating socket
    serverSocket = socket.socket()

    #Binding ip_server and port
    serverSocket.bind(ADDRESS)
    print("Server STARTED...")

    #server limit
    serverSocket.listen(5)

    #This while loop will keep listening to client connections
    while True:
        connection, address = serverSocket.accept()
        print(f"Client CONNECTED -> {address}")

        threading.Thread(target=client_Handler, args=(connection, )).start()

    
           

if __name__ == "__main__":
    main()
    
