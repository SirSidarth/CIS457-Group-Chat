from threading import Thread
from socket import socket, SOCK_STREAM, AF_INET, timeout

PORT = 8087
clients = []
running = True # used to update server when the server is closing

def broadcast(message, current_client):
    for client in clients[:]:
        if client != current_client:
            try:
                client.send(message)
            except: # Incase a client leaves during the loop
                clients.remove(client)

def handle_client(client_socket):
    try:
        while True:
            # Receive the message from the client
            message = client_socket.recv(1024)
            if not message:
                break  # Client disconnected
            broadcast(message, client_socket)  # Broadcast the message to other clients
    except:
        pass # Stops error messages when client disconnects

    finally: # Ensures these two lines run even if connection is terminated improperly
        clients.remove(client_socket)  # Remove client from list
        client_socket.close()

def server_loop(server_thread):
    global running
    print("Server started. Type 'exit' to stop.")
    while running:
        try:
            server_thread.settimeout(1)  # Timeout to check running flag periodically
            client_socket, client_address = server_thread.accept()
            print(f"New connection from {client_address}")
            clients.append(client_socket)
            thread = Thread(target=handle_client, args=(client_socket,))
            thread.start()
        except timeout:
            continue  # Continue loop if no connection is made within the timeout
        except OSError:
            break  # Break loop if server_socket is closed

def main():
    global running
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('127.0.0.1', PORT))
    server_socket.listen(5) # allows 5 connections, we can expand this if we want but these seemed fine for now

    print("Server is starting...")

    server_thread = Thread(target=server_loop, args=(server_socket,))
    server_thread.start()

    input("") # Wait for any input to close server
    print("Server is closing...")
    running = False
    server_socket.close()
    for client in clients:
        client.close()
    server_thread.join() # Waits for other threads to close
    print("Server has closed")

if __name__ == "__main__":
    main()