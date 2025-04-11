import socket
import threading

SERVER_IP = "127.0.0.1"  # Change this if the server is on another machine
PORT = 8087

def receive_messages(client_socket):
    """Continuously receives messages from the server and prints them."""
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except:
            print("Disconnected from server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((SERVER_IP, PORT))
        print("Connected to chat server.")
    except:
        print("Failed to connect.")
        return

    # Starts a separate thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True  # Ends thread when main program exits
    receive_thread.start()

    # Loop for sending messages
    while True:
        message = input()
        if message.lower() == "exit":
            break  # Exit chat
        
        try:
            client_socket.send(message.encode("utf-8"))
        except:
            print("Failed to send message.")
            break

    client_socket.close()
    print("Disconnected from chat.")

if __name__ == "__main__":
    main()
