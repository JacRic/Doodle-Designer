# Jacob Richard COMP 4911 - Final Project
# Doodle Designer is a drawing game where players are given a word to draw and other players vote on the best drawing.
# The game is split into three phases: drawing, voting, and winner announcement.
# The game is played over a TCP connection with a server hosting the game.

# Imports
import pygame
import os
import time
from DD_TCPClient import TCPClient

# Initialize player TCP client
client = TCPClient("192.168.2.104", 12345)

# Pygame window setup
pygame.init()
pygame_screen = pygame.display.set_mode((1280, 720))
pygame_screen.fill('white')
pygame.display.set_caption("Doodle Detective")

# Prepare the loading screen
bg = pygame.image.load(os.path.join("./", "DD_LoadingScreen.jpg"))
pygame_screen.blit(bg, (0, 0))
pygame.display.update()
pygame.font.init()
textFont = pygame.font.SysFont('Comic Sans MS', 30)
buttonText = textFont.render('Join a lobby', False, (0,0,0))

# Main loop for the loading screen
# This loop will wait for the player to click the button to join the lobby and the connection is established
loading = True
while loading:
    x, y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loading = False
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clicking the button
            if (x >= 540 and x <= 740) and (y >= 400 and y <= 500):
                # Try and connect player to the server
                try:
                    client.connect()
                    loading = False
                except TimeoutError:
                    buttonText = textFont.render('Server Down', False, (0,0,0))

    # Logic for highlighting button when the pla logic
    if (x >= 540 and x <= 740) and (y >= 400 and y <= 500): 
        pygame.draw.rect(pygame_screen,(164,212,146),[540, 400, 200, 100])
    else: 
        pygame.draw.rect(pygame_screen,(147,222,120),[540, 400, 200, 100]) 
    pygame_screen.blit(buttonText, (555,420))

    pygame.display.flip()

# Prepare the Drawing phase screen
bg = pygame.image.load(os.path.join("./", "DD_Canvas+Background.jpg"))
pygame_screen.blit(bg, (0, 0))

# Display waiting message
buttonText = textFont.render('Waiting for players', False, (0,0,0))
pygame_screen.blit(buttonText, (500,420))

pygame.display.update() 

# Loops until lobby is full and game is ready to start
# The server will send a message when the lobby is full 
# This message will contain the word that must be drawn
creating_lobby = True
while creating_lobby:
    word = client.receive_data()
    if word != "Waiting on more players":
        creating_lobby = False


# Prepare the canvas for drawing
display_word = textFont.render("Word to draw: " + str(word), False, (0,0,0))
pygame_screen.blit(display_word, (400,100))
pygame.draw.rect(pygame_screen, 'white', pygame.Rect(160, 172, 960, 492))

# Main loop for the running stage of the game.
draw = False
drawing_phase = True
stopwatch = time.time()
while drawing_phase:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            drawing_phase = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            draw = True
        if event.type == pygame.MOUSEBUTTONUP:
            draw = False
        if event.type == pygame.KEYDOWN:
            # Resets the canvas
            if event.key == pygame.K_e:
                pygame.draw.rect(pygame_screen, 'white', pygame.Rect(160, 172, 960, 492))
    
    # Logic for drawing on the canvas
    if draw:
        x, y = pygame.mouse.get_pos()
        if (x > 165 and x < 1115) and (y > 176 and y < 659):
            pygame.draw.circle(pygame_screen, 'black', (pygame.mouse.get_pos()), 5)

    # Ends the drawing phase after 30 seconds
    if time.time() - stopwatch > 30:
        drawing_phase = False
    
    pygame.display.flip()

# Capture the drawing area to send to the server
drawing = pygame_screen.subsurface(pygame.Rect(160, 172, 960, 492)) 

# Convert the drawing to a bytes object
drawing_bytes = pygame.image.tobytes(drawing, 'RGB')

# Send the drawing data to the TCP server
size = len(drawing_bytes)
client.send_image(drawing_bytes)

# Receive bytes corresponding to all of the other player's drawings from the server
drawings = client.receive_drawings(size)

# Converts the drawings back to image
voting_screen = pygame.image.frombytes(drawings, (960, 492),'RGB')

# Prepare the voting screen
pygame_screen.blit(bg, (0, 0))
voting_directions = textFont.render("Vote on the best drawing", False, (0,0,0))
pygame_screen.blit(voting_directions, (500,100))


# Main loop for the voting phase
# Player will vote on the best drawing by clicking on the best image
vote = 0
voting_phase = True
while voting_phase:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            voting_phase = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if (x > 165 and x < 640) and (y > 176 and y < 422):
                vote = "1"
                voting_phase = False
            if (x > 640 and x < 1115) and (y > 176 and y < 422):
                vote = "2"
                voting_phase = False
            if (x > 165 and x < 640) and (y > 422 and y < 659):
                vote = "3"
                voting_phase = False
            if (x > 640 and x < 1115) and (y > 422 and y < 659):
                vote = "4"
                voting_phase = False

    pygame_screen.blit(voting_screen, (160, 172))
    pygame.display.flip()

# Send the vote to the server and wait for all other players to vote
client.send_data(vote)
tally_votes = True
while tally_votes:
    winners = client.receive_data()
    if winners != "Waiting on votes":
        tally_votes = False

# Prepare the winner screen and display the winner(s)
winner_text = textFont.render("Winner!", False, (0,255,0))
for winner in winners:
    if winner == "1":
        pygame_screen.blit(winner_text, (165, 176))
    if winner == "2":
        pygame_screen.blit(winner_text, (640, 176))
    if winner == "3":
        pygame_screen.blit(winner_text, (165, 422))
    if winner == "4":
        pygame_screen.blit(winner_text, (640, 422))
pygame.display.update()

# Wait for 5 seconds before closing the game
time.sleep(5)
pygame.quit()