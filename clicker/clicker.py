import pygame #this library is awesome  
import time #this library is used to track time for idle messages and the lose condition
import random #this library is just for the random idle messages
import sys #this library is used to exit the game - do we need it?

#I reckon this is what we use to hook it up to shanalytics

#import safehouse


#project = safehouse.activate_project(
    #name='tic-tac-toe',   obviously we need to change this
    #org_name='safehouse',
    #runtime_mode='local', # change to live when we have live
#)
#user_id = safehouse.user.id_for("local")


#events = project.events
#events.origin = 'game'
#game_id = randint(0, 1000000)



pygame.init()

#The window size, width and height won't change.You can do higher numbers if you have a bigger screen

WIDTH, HEIGHT = 1000, 800 #size of game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #creates the game window with the width and height we specified 
pygame.display.set_caption("WORLD OF CAKE 🍰") #This Is the title of the game window

clock = pygame.time.Clock() #this is the clock object that will be used to control the frame rate
FONT = pygame.font.SysFont(None, 35) #this is the font object that will be used to draw text on the screen
BIG_FONT = pygame.font.SysFont(None, 45)#this  using the default system font with a size of 88, 

# the images have to be in the same folder as the python game code file, or else you have to specify the path and idk how to do that.
BG = pygame.image.load("bg.jpeg") #random image we are using as a background
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT)) #this makes the background fit the window size 

cake_img = pygame.image.load("cake1.png") #here we are loading the cake image
BASE_CAKE_SIZE = 140 #this is the base size of the cake image -- will be scaled up when the player clicks on it

#Here are the variables, we are going to start with one cake per click and no cakes per second, to be incremented
cakes = 0 #MAIN VARIABLE, keeps track of how many cakes the player has, incremented by clicks and auto cakes per second
cakes_per_click = 1#how many cakes the player gets per click, starts at 1 and isincreased by upgrades
cakes_per_second = 0 #how many cakes the player gets automatically per second, starts at 0 and increased by upgrades

message = "Cha-ching!" #is this the upgrade message or the main cake click message (But cakes don't make cha-ching noises?

last_click_time = time.time() #this is the time of the last click, determines when to trigger idle messages and trigger the lose condition
idle_message = "" #this is the message that will be displayed when the player is idle, it will be randomly chosen from the idle_prompts list
idle_message_time = 0 #this is the time of the last idle message, determines when to trigger a new idle message

WIN_CAKES = 1_000_000_000 #how many cakes needed to trigger the win condition

# ---------------- CAKE BUTTONS ----------------
cakes_data = [#this is a list of dictionaries, each dictionary represents a cake button or upgrade
    
    #the (#, #) fields control the position of the buttons on screen.  (0, 0) is the
    #top left corner, and (WIDTH, HEIGHT) is the bottom right corner.
    
    {"label": "CLICK ME", "pos": (430, 300), "cost": 0}, #main cake button, it doesn't cost anything and gives 1 cake per click
    {"label": "Cake / second (500)", "pos": (100, 150), "cost": 500},#second upgrade, costs 500 cakes and gives 1 cake per second
    {"label": "Click power +1 (100)", "pos": (100, 350), "cost": 100}, #first upgrade costs 100 cakes and gives +1 cake per click
    {"label": "Cakes / sec +5 (2200)", "pos": (100, 550), "cost": 2200}, #fourth upgrade costs 2200 cakes and gives +5 cakes per second
    {"label": "+50 click power (5000)", "pos": (700, 150), "cost": 5000},#third upgrade costs 5000 cakes and gives +50 cakes per click
    {"label": "Cakes / sec +50 (25000)", "pos": (700, 350), "cost": 25000},#fifth upgrade costs 25000 cakes and gives +50 cakes per second
    {"label": "+500 click power (50000)", "pos": (700, 550), "cost": 50000},#sixth upgrade costs 50000 cakes and gives +500 cakes per click
]

idle_prompts = [ 
    "Don't you want cake?",
    "Click the cake.",
    "No clicks? No cake.",
    "😢",
]

# ---------------- HELPERS ----------------
#this is a helper function to draw text on the screen, it takes the text, x and y coordinates, font and color as parameters
#it renders the text and blits it to the window at the specified coordinates
#the default font is FONT and the default color is black, but you can specify different fonts and colors when calling the function
#this function is used throughout the game to display the number of cakes, the upgrade messages, the idle messages and the win/lose messages
#it makes the code cleaner and more organized by centralizing the text drawing logic in one place, so you don't have to repeat 
# the same code every time you want to display text on the screen
def draw_text(text, x, y, font=FONT, color=(255, 255, 127)):#this line defines the function draw_text, which takes the text to be displayed, the x and y coordinates for the position of the text, the font to be used (default is FONT), and the color of the text (default is a light yellow color)
    img = font.render(text, True, color)#this line renders the text into an image using the specified font and color. The second parameter (True) is for anti-aliasing, which makes the text smoother.
    WIN.blit(img, (x, y))#this line blits the rendered text image onto the game window (WIN) at the specified x and y coordinates. This is what actually draws the text on the screen.
#blit is basically like "splat" or "stamp" --- blit that on there. 

message = "" #this sets the global variable message to the text that was passed to the function, which will be displayed in the main loop
message_time:float = time.time() #this sets the global variable message_time to the current time, which will be used in the main loop to determine how long to display the message on the screen. The message will be displayed for 1 second after this time is set.

def show_message(text):#this shows a message on the screen for a short period of time, it takes the text as a parameter and sets the global variables message and message_time to display the message in the main loop
    global message, message_time #these global variables are used to keep track of the current message being displayed and the time it was set, so we need to declare them as global to modify them inside the function
    message = text #this sets the global variable message to the text that was passed to the function, which will be displayed in the main loop
    message_time = time.time() #this sets the global variable message_time to the current time, which will be used in the main loop to determine how long to display the message on the screen. The message will be displayed for 1 second after this time is set.

# ---------------- MAIN LOOP ----------------
def main():
    global cakes, cakes_per_click, cakes_per_second# these global variables are used to keep track of the game state and are modified in the main loop. I hereby declare them, that they may be modified inside the function
    global last_click_time, idle_message, idle_message_time# these global variables are used to keep track of the game state and are modified in the main loop, so we need to declare them as global to modify them inside the function

    running = True
    last_auto_time = time.time()
    clicking = False

    while running:
        #WIN.blit(BG, (0, 0))
        WIN.fill((100, 180, 255)) #this fills the window with a solid color (light blue) instead of using the background image
        now = time.time()

        # These are the game events, which are checked every frame. Mouse clicks/release, quit game etc
        for event in pygame.event.get(): #Every time something happens, like a click or a key press, it creates an event.
            if event.type == pygame.QUIT:#if the event is a quit event (like clicking the X on the window), it sets running to False, which will exit the main loop and end the game
                pygame.quit()#And this will happen
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:#
                clicking = True
                last_click_time = now
                mouse = event.pos#We are getting the position of the mouse click to see which button (ifany) the player clicked on

                for i, cake in enumerate(cakes_data):#we are looping through the cakes_data list to check if the mouse click was on any of the cake buttons, based on their position
                    rect = pygame.Rect(cake["pos"][0], cake["pos"][1],# we are creating a rectangle for each cake button based on its position and the base cake size, to check for collisions with the mouse click
                                       BASE_CAKE_SIZE, BASE_CAKE_SIZE)# the rectangle is created using the x and y position of the cake button, and the width and height are both set to BASE_CAKE_SIZE, which is 140 pixels. This means that each cake button will have a clickable area of 140x140 pixels around its position. We will use this rectangle to check if the mouse click was within this area, which would indicate that the player clicked on that cake button.
                    if rect.collidepoint(mouse): #if the mouse click was within the rectangle of the cake button, it means the player clicked on that button, and we will execute the corresponding action based on which button it was (main cake button or an upgrade)

                        if i == 0:#if the player clicked on the main cake button (index 0), it adds cakes_per_click to the total cakes and shows a message, then breaks out of the loop so it doesn't check the other buttons
                            cakes += cakes_per_click
                            show_message("You received cake!")
                            break #Then it breaks out of the loop so it doesn't check the other buttons

                        if cakes < cake["cost"]:#if the player doesn't have enough cakes to buy the upgrade, it shows a message and breaks out of the loop, so they can't buy the upgrade
                            show_message("You don't have enough cake! How sad!")# and it shows this message
                            break

                        cakes -= cake["cost"]
                        show_message("You receive cake!")

                        if i == 1:#if player clicked on the 1st upgrade button (index 1), it increases cakes_per_second by 1, see cakes_data list
                            cakes_per_second += 1# if the player clicked on the second upgrade button (index 1), it increases cakes_per_second by 1, and so on for the other upgrade buttons based on their index, which corresponds to the upgrades we defined in the cakes_data list
                        elif i == 2:#if the player clicked on the second upgrade button (index 2), it increases cakes_per_click by 1, and so on for the other upgrade buttons based on their index, which corresponds to the upgrades we defined in the cakes_data list
                            cakes_per_click += 1 #   if the player clicked on the third upgrade button (index 2), it increases cakes_per_click by 1, and so on for the other upgrade buttons based on their index, which corresponds to the upgrades we defined in the cakes_data list   
                        elif i == 3:
                            cakes_per_second += 5
                        elif i == 4:
                            cakes_per_click += 50
                        elif i == 5:
                            cakes_per_second += 50
                        elif i == 6:
                            cakes_per_click += 500

            if event.type == pygame.MOUSEBUTTONUP:
                clicking = False

        # -------- AUTO CAKES --------
        if now - last_auto_time >= 1:
            cakes += cakes_per_second
            last_auto_time = now

        # Idle prompt / lose condition
        if now - last_click_time > 30 and now - idle_message_time > 5:
            idle_message = random.choice(idle_prompts)
            idle_message_time = now

        if now - last_click_time > 200:
            WIN.fill((0, 0, 0))
            draw_text("You lost. The cake got stale.", 250, 350, BIG_FONT, (255, 255, 255))
            pygame.display.update()
            pygame.time.wait(4000)
            return

        # -------- DRAW CAKES --------
        for i, cake in enumerate(cakes_data):
            size = BASE_CAKE_SIZE + 20 if clicking and i == 0 else BASE_CAKE_SIZE
            img = pygame.transform.smoothscale(cake_img, (size, size))
            WIN.blit(img, cake["pos"])
            draw_text(cake["label"], cake["pos"][0] - 10, cake["pos"][1] - 30)

        # -------- UI --------
        draw_text(f"Cakes: {cakes}", 20, 20)
        draw_text(f"Cakes / Click: {cakes_per_click}", 20, 50, FONT, (255, 127, 255))
        draw_text(f"Cakes / Second: {cakes_per_second}", 20, 80)

        if (now - message_time) < 2:
            draw_text(message, 350, 700, BIG_FONT)

        if idle_message and now - idle_message_time < 5:
            draw_text(idle_message, 300, 120, BIG_FONT)

        # -------- WIN --------
        if cakes >= WIN_CAKES:
            for i in range(30):
                WIN.fill((255, 255, 255))
                big = pygame.transform.smoothscale(cake_img, (300 + i * 10, 300 + i * 10))
                WIN.blit(big, (350 - i * 5, 250 - i * 5))
                draw_text("THE CAKE EXPLODES 🎉", 300, 100, BIG_FONT)
                pygame.display.update()
                pygame.time.delay(50)
            pygame.time.wait(3000)
            return

        pygame.display.update()
        clock.tick(60)

main()