
import socket

IP_SERVER = "localhost"
PORT = 12000
ADDRESS = (IP_SERVER, PORT)

clientSocket = socket.socket()


clientSocket.connect(ADDRESS)
print("Client CONNECTED...")

msg = clientSocket.recv(2000).decode("utf-8")
print(msg)


while True:
    try:
        UserInput = int(input("Choose one of the questions 1/2:"))
        clientSocket.send(str(UserInput).encode("utf-8"))
        break
        
    except:
        print("Invalid input, Input 1 or 2:")


print(f"Server RESPONSE -> {clientSocket.recv(2000).decode("utf-8")}")






#import required modues
import socket
import threading
import tkinter as tk

IP_SERVER = "localhost"
PORT = 10000
ADDRESS = (IP_SERVER, PORT)

def message_from_server(clientSocket):
    while True:
        message = clientSocket.recv(2050).decode("utf-8")
        if message != '':
            username = message.split("~")[0]
            content = message.split("~")[1]

            print(f"[{username}]  {content}")

        else:
            print("The message sent from server is empty")
            exit(0)

def send_message_to_server(clientSocket):
    while True:
        message = input("Message: ")
        if message != '':
            clientSocket.sendall(message.encode("utf-8"))
        else:
            print("Message is empty")
            exit(0)
        

def communicate_with_server(clientSocket):
    username = input("Please enter your username: ")

    if username != '':
        clientSocket.sendall(username.encode("utf-8"))

    else:
        print("Username cannot be empty")
        exit(0)

    threading.Thread(target=message_from_server, args=(clientSocket, )).start()

    send_message_to_server(clientSocket)
    


#Main Function
def main():
    clientSocket = socket.socket()
     
    #Connecting client to server
    clientSocket.connect(ADDRESS)
    print("Client STARTED...")

    communicate_with_server(clientSocket)



if __name__ == "__main__":
    main()