# Jacob Richard COMP 4911 - Final Project
# This is the server side of the Doodle Designer game. 
# The server will host the game and handle the connections with the players.
# Socket programming is used to communicate with the players over a TCP connection.
# The server will handle the drawing phase, voting phase, and winner announcement.

# Imports
import socket
import threading
import time
from DD_WordPool import WordPool
import pygame

# Constant
MAX_PLAYERS = 4

# Create a WordPool object to get a random word to draw
wordPool = WordPool()
word = wordPool.pick_random_word()

# Lock to prevent multiple threads from appending to the list at the same time
lock = threading.Lock()

# List to store player threads
player_threads = []
# List to store player connections
player_connections = []
# List to store drawings
drawings = []
# List to store votes
votes = []

# Function to compile the images from all players into one image in a grid like fashion
def compile_images():
    # Convert the drawing back to bytes
    screen = pygame.display.set_mode((960, 492))

    x = 0
    y = 0
    # Draws the images in a grid like fashion
    for drawing in drawings:
        if x >= 960:
            x = 0
            y += 246
        image = pygame.image.frombytes(drawing, (960, 492),'RGB')
        small_image = pygame.transform.rotozoom(image, 0, 0.5)
        screen.blit(small_image, (x, y))

    # Return the compiled image as bytes to send to the players for voting
    return pygame.image.tobytes(screen, 'RGB')


# Function to handle each player and guide them through the drawing phase
# This function will receive the drawing from the player and add it to the list of drawings
def handle_drawing(connection, word, lock):

    # send the word to draw to the player
    connection.send(word.encode())

    # Wait for the player to finish drawing
    time.sleep(30)
    
    # Size of the image in bytes
    image_size = 1416960

    # Get the image in chunks from the player
    image_data = b""
    while len(image_data) < image_size:
        image_data = image_data + connection.recv(4096)

    
    # Add the drawing to the list of drawings
    # Lock is used to prevent multiple threads from appending the list at the same time
    lock.acquire()
    drawings.append(image_data)
    lock.release()


# Function to handle each player connection and guide them through the voting phase
def handle_voting(connection, final_image, lock):
    
    # Send the compiled image to the player for voting
    connection.sendall(final_image) 

    # Receive the vote from the player
    vote = connection.recv(1024).decode()

    # Add the vote to the list of votes
    # Lock is used to prevent multiple threads from appending the list at the same time
    lock.acquire()
    votes.append(vote)
    lock.release()

    # Wait for all players to vote
    while len(votes) < MAX_PLAYERS:
        connection.send("Waiting on votes".encode())
        time.sleep(1)
    
    # Tally the votes and determine winner
    vote_counts = {}

    for vote in votes:
        if vote in vote_counts:
            vote_counts[vote] += 1
        else:
            vote_counts[vote] = 1

    max_votes = max(vote_counts.values())
    winners = [player for player, votes in vote_counts.items() if votes == max_votes]
    
    if len(winners) == 1:
        winner = winners[0]
        winning_message = winner
    else:
        winning_message = "".join(winners)
    
    # Send the winner(s) to the player(s)
    connection.send(winning_message.encode())

    # Close the connection
    connection.close()


# Create a socket for server to listen for incoming connections 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(('', 12345))

# Listen for incoming connections
server_socket.listen(MAX_PLAYERS)
print("Server started. Waiting for players...")

# Accept player connections
while len(player_connections) < MAX_PLAYERS:
    connection, address = server_socket.accept()
    player_connections.append(connection)
    print("Player connected:", address)

# Start the drawing phase by creating a thread for each player that will handle the drawing
for connection in player_connections:
    thread = threading.Thread(target=handle_drawing, args=(connection,word, lock,))
    thread.start()
    player_threads.append(thread)

# Wait for all player threads to finish drawing and join them
for thread in player_threads:
    thread.join()

# Compile the images from all players into one image
final_image = compile_images()  

# Start the voting phase by creating a thread for each player that will handle the voting
for connection in player_connections:
    threading.Thread(target=handle_voting, args=(connection, final_image, lock,)).start()

