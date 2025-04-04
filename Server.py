from threading import Thread, Lock
from socket import socket, SOCK_STREAM, AF_INET, timeout, SOL_SOCKET, SO_REUSEADDR

PORT = 8087
clients = []
clients_lock = Lock()
running = True

def broadcast(message, current_client):
    with clients_lock:
        for client in clients[:]:
            if client != current_client:
                try:
                    client.send(message)
                except:
                    clients.remove(client)

def handle_client(client_socket):
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, client_socket)
    except:
        pass
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print("Client disconnected.")

def server_loop(server_socket):
    global running
    print("Server started. Type 'exit' to stop.")
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