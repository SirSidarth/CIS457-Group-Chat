import socket
import threading
import tkinter as tk
import queue

SERVER_IP = "127.0.0.1"
PORT = 8087


class ChatClientApp:
    def __init__(self, master):
        self.master = master
        master.title("Tkinter Chat Client")

        self.username = None
        self.client_socket = None
        self.running = False

        self.data_queue = queue.Queue()

        # GUI components
        self.chat_log = tk.Text(master, state='disabled', width=50, height=20)

        self.chat_log.tag_configure("me", background="#d0f0c0") # Light green
        self.chat_log.tag_configure("other", background="white")
        self.chat_log.tag_configure("connection", background="#e6f7ff") # Light blue
        self.chat_log.tag_configure("error", background="#ffb3b3") # Light red

        self.message_entry = tk.Text(master, height=10, width=40)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)

        self.message_entry.config(state='disabled')
        self.send_button.config(state='disabled')

        self.prompt_username()# Ask for username before connecting
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        self.update_gui()

    def prompt_username(self): # Asks user to put in a name before connecting
        popup = tk.Toplevel()
        popup.title("Enter Username")
        popup.grab_set()

        popup.protocol("WM_DELETE_WINDOW", self.close)

        tk.Label(popup, text="Username:").pack(padx=10, pady=(10, 0))
        entry = tk.Entry(popup)
        entry.pack(padx=10, pady=5)
        entry.focus()

        error_label = tk.Label(popup, text="", fg="red")  # Red text for error
        error_label.pack(padx=10, pady=5)

        def set_username():
            name = entry.get().strip()
            if name and (name != "Me"):
                if self.connect_to_server(name):
                    self.username = name
                    popup.destroy()
                    
                    # After the username is set, show the message system
                    self.chat_log.pack(padx=10, pady=5)
                    self.message_entry.pack(side=tk.LEFT, padx=(10, 0), pady=5)
                    self.send_button.pack(side=tk.LEFT, padx=(5, 10), pady=5)

                    # Enable the message entry and send button
                    self.message_entry.config(state='normal')
                    self.send_button.config(state='normal')

                    self.master.deiconify() # Make window visable
                else:
                    error_label.config(text="Username is already taken")
            else:
                error_label.config(text="Invalid Username! Please try again.")

        tk.Button(popup, text="Connect", command=set_username).pack(pady=(0, 10))
        popup.bind("<Return>", lambda event: set_username())

    def connect_to_server(self, name):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((SERVER_IP, PORT))
            self.client_socket.send(name.encode("utf-8"))
            if self.client_socket.recv(1024).decode("utf-8") == "OK":
                self.running = True

                self.append_message("1Connected to chat server.") # 1 is used to display text color properly in append_message()
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                return True
            else:
                self.client_socket.close()
                return False

        except Exception as e:
            self.append_message(f"Failed to connect: {e}")

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if not message:
                    break
                self.data_queue.put(message)
            except:
                self.data_queue.put("Disconnected from server.")
                self.send_button.config(state='disabled')
                break

    def send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            try:
                self.client_socket.send(message.encode("utf-8"))
                self.message_entry.delete("1.0", tk.END)
            except:
                self.append_message("Failed to send message.")

    def append_message(self, message):
        self.chat_log.config(state='normal')
        if message[:1] == "0":
            tag = "other"
            message = message[1:]

        elif message[:1] == "1":
            tag = "connection"
            message = message[1:]

        elif message[:1] == "9":
            tag = "me"
            message = message[1:]

        else: # Messages without a code number will be interperated as errors
            tag = "error"
        self.chat_log.insert(tk.END, message + "\n", tag)
        self.chat_log.config(state='disabled')
        self.chat_log.see(tk.END)

    def update_gui(self):
        try:
            message = self.data_queue.get_nowait()
            self.append_message(message)
        except queue.Empty:
            pass
        self.master.after(100, self.update_gui) # Check every 100 ms

    def close(self):
        self.running = False
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    root.withdraw() # Hide main window until user sets username

    app = ChatClientApp(root)
    root.mainloop()
