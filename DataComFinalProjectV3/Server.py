from threading import Thread, Lock
from socket import socket, SOCK_STREAM, AF_INET, timeout, SOL_SOCKET, SO_REUSEADDR

PORT = 8087
clients = []
client_names = {}
clients_lock = Lock()
running = True

def broadcast(message, current_client, broadcast_num=0): #broadcast_num handles handles the type of broadcast, 0 is a message, 1 is a connection
    with clients_lock:
        for client in clients[:]:
            try:
                if client != current_client:
                    if broadcast_num == 1:
                        client.send((f"{broadcast_num}{message}").encode("utf-8")) # Connection message
                    else:
                        client.send((f"{broadcast_num}{client_names[current_client]}: \n{message}").encode("utf-8")) # client message

                else:
                    if broadcast_num == 0:
                        client.send((f"9Me: \n{message}").encode("utf-8")) # Broadcast back to sending client to confirm message was sent, 9
                    if broadcast_num == 1:
                        client.send((f"OK").encode("utf-8")) # Tell client that it's username is good
            except: # If a client cannot be reached
                        clients.remove(client)
                
def handle_client(client_socket):
    try:
        name = set_client_name(client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8').strip()
            if not message:
                break
            broadcast(message, client_socket)
    except:
        pass
    finally:
        if name:
            broadcast(f"{name} has disconnected",client_socket, 1)
            client_names.pop(client_socket, None) # remove from dict, don't raise error if it cannot be found
            with clients_lock:
                if client_socket in clients:
                    clients.remove(client_socket)
            client_socket.close()
            print("Client disconnected.")
        else:
            if running: # Stops this from printing if server closed
                print("Client used invalid name, disconnecting")

def set_client_name(client_socket):
    try:
        name = client_socket.recv(1024).decode('utf-8').strip()
        if running and (name not in client_names.values()):
            client_names[client_socket] = str(name)
            print(f"{name} joined the chat.")
            broadcast(f"{name} has joined the chat.", client_socket, 1)
            return name
        else:
            client_socket.send((f"Invalid").encode("utf-8"))
            client_socket.close()
    except:
        client_socket.close()

def server_loop(server_socket):
    global running
    print("Server started. Press enter to stop.")
    while running:
        try:
            server_socket.settimeout(1)
            client_socket, client_address = server_socket.accept()
            print(f"New connection from {client_address}")
            with clients_lock:
                clients.append(client_socket)
            thread = Thread(target=handle_client, args=(client_socket,), daemon=True)
            thread.start()
        except timeout:
            continue
        except ConnectionResetError:
            continue
        except OSError:
            break

def main():
    global running
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', PORT))
    server_socket.listen(5)
    server_socket.settimeout(1)
    print("Server is starting...")

    server_thread = Thread(target=server_loop, args=(server_socket,))
    server_thread.start()

    try:
        input("")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt. Shutting down...")
    print("Server is closing...")
    running = False

    try:
        dummy = socket(AF_INET, SOCK_STREAM)
        dummy.connect(('127.0.0.1', PORT))
        dummy.close()
    except:
        pass
    server_socket.close()

    with clients_lock:
        for client in clients:
            client.close()
    server_thread.join()
    print("Server has closed.")

if __name__ == "__main__":
    main()