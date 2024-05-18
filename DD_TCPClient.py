# Jacob Richard COMP 4911 - Final Project
# This class is the TCP client that will connect to the server and send and receive messages.

# Imports
from socket import socket, AF_INET, SOCK_STREAM


class TCPClient:
    # Constructor for the TCP Client
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    # Function to connect to the server
    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
        except TimeoutError:
            raise TimeoutError("Connection timed out. Server is not available.")

    # Function to send a message to the server
    def send_data(self, message):
        try:
            print("message waiting to be sent")
            self.client_socket.send(message.encode())
            print("Message sent successfully.")
        except TimeoutError:
            print("Failed to send message.")

    # Function to send an image to the server
    # The image is sent in bytes so it can be reconstructed on the server side
    def send_image(self, image_bytes):
        try:
            self.client_socket.sendall(image_bytes)
            print("Image sent successfully.")
        except TimeoutError:
            print("Failed to send image.")
    
    # Function to receive a message from the server
    def receive_data(self):
        try:
            data = self.client_socket.recv(1024)
            return data.decode()
        except TimeoutError:
            print("Failed to receive message.")

    # Function to receive an image from the server
    # The image is large so it is received in chunks and reconstructed
    def receive_drawings(self, image_size):
        print("received image size")
        image_data = b""
        while len(image_data) < image_size:
            temp_data = self.client_socket.recv(4096)
            print(len(temp_data))
            image_data = image_data + temp_data 

        return image_data[0:image_size]

    # Function to close the connection
    def close(self):
        self.client_socket.close()
        print("Connection closed.")
