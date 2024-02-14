import pygame
import sys
import random
import pygame.freetype

pygame.init()

#music
pygame.mixer.music.load("snakegame_bg.wav")

#sound
eat_sound = pygame.mixer.Sound("food.wav")
game_over_sound = pygame.mixer.Sound("gameover.wav")
toggle_sound = pygame.mixer.Sound("toggle1.wav")

#constants
WIDTH, HEIGHT = 700, 400 
CELL_SIZE = 20
FPS = 4  

# Colors
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 255, 0)
GRAY = (0, 96, 100)
PINK = (248, 152, 128) 

# Directions
UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)
LEFT = (-CELL_SIZE, 0)
RIGHT = (CELL_SIZE, 0)

FRUIT_COLORS = [(WHITE), (PINK), (130, 202, 250), (255, 0, 0)] #red white pink blue

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

#bg grass image
background_image = pygame.image.load("BG1.jpg").convert()

#snake logo image
snake_image = pygame.image.load("Snake.jpg")

#snake starting position
snake = [(100, 100), (90, 100), (80, 100)]
snake_direction = None  

foods = []
score = 0
game_over = False
phasing_mode = True

# Sidebar 
initial_width = 150
max_sidebar_width = 300  
fullscreen = False  
sidebar_width = max_sidebar_width if fullscreen else initial_width  # Initial width
sidebar_rect = pygame.Rect(WIDTH - sidebar_width, 0, sidebar_width, HEIGHT)

initial_snake_width = initial_width   # Adjust the snake phto width
initial_snake_height = initial_snake_width - 10 #  aspect rtio
snake_image = pygame.transform.scale(snake_image, (initial_snake_width, initial_snake_height))

# Speed levels
speed_levels = [ 4, 5, 11]  
current_speed = speed_levels[0]  

show_score = True

# initial screen and full screen toggling
def toggle_fullscreen():
    global fullscreen, WIDTH, HEIGHT, sidebar_rect, sidebar_width, background_image, snake_image
    toggle_sound.play()
    if fullscreen:
        # Exit fullscreen mode
        fullscreen = False
        sidebar_width = 150  
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        sidebar_rect = pygame.Rect(WIDTH - sidebar_width, 0, sidebar_width, HEIGHT)
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        snake_image = pygame.transform.scale(snake_image, (sidebar_width, sidebar_width))
    else:
        # Enter fullscreen mode
        fullscreen = True
        sidebar_width = max_sidebar_width
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
        sidebar_rect = pygame.Rect(WIDTH - sidebar_width, 0, sidebar_width, HEIGHT)
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        snake_image = pygame.transform.scale(snake_image, (sidebar_width, sidebar_width))

    if not fullscreen:
        WIDTH, HEIGHT = 700, 400  # Initial width and height
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        sidebar_rect = pygame.Rect(WIDTH - sidebar_width, 0, sidebar_width, HEIGHT)
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        snake_image = pygame.transform.scale(snake_image, (sidebar_width, sidebar_width))
   
def spawn_fruits(num_fruits):
    return [(random.randrange(0, (WIDTH - sidebar_width) // CELL_SIZE) * CELL_SIZE,
             random.randrange(0, HEIGHT // CELL_SIZE) * CELL_SIZE,
             random.choice(FRUIT_COLORS)) for _ in range(num_fruits)]

foods.extend(spawn_fruits(1)) 
foods.extend(spawn_fruits(1))  
foods.extend(spawn_fruits(2))  

#restarting
def restart_game():
    global snake, snake_direction, foods, score, game_over
    snake = [(100, 100), (90, 100), (80, 100)]
    snake_direction = None
    # Reset 
    foods = []
    score = 0
    game_over = False
    # Respawn food
    foods.extend(spawn_fruits(1))  
    foods.extend(spawn_fruits(1))  
    foods.extend(spawn_fruits(2))  

    pygame.mixer.music.play(-1)

pygame.mixer.music.play(-1)

# Main game loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    restart_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            elif snake_direction is None:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    snake_direction = RIGHT  
            else:
                if event.key == pygame.K_UP and snake_direction != DOWN:
                    snake_direction = UP
                elif event.key == pygame.K_DOWN and snake_direction != UP:
                    snake_direction = DOWN
                elif event.key == pygame.K_LEFT and snake_direction != RIGHT:
                    snake_direction = LEFT
                elif event.key == pygame.K_RIGHT and snake_direction != LEFT:
                    snake_direction = RIGHT
                elif event.key == pygame.K_p:
                    phasing_mode = not phasing_mode
                    toggle_sound.play()
                elif event.key == pygame.K_f:
                    toggle_fullscreen()
                elif event.key == pygame.K_s:
                    show_score = not show_score
                    toggle_sound.play()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    # speed 123
                    speed_index = int(event.unicode) - 1
                    toggle_sound.play()
                    if 0 <= speed_index < len(speed_levels):
                        current_speed = speed_levels[speed_index]

    if not game_over and snake_direction is not None:
        new_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])

        if not phasing_mode and (new_head[0] >= WIDTH - sidebar_width or new_head[0] < 0 or new_head[1] < 0 or new_head[1] >= HEIGHT):
            game_over = True
            pygame.mixer.music.stop() 
            game_over_sound.play()  
        else:
            # phase on
            if phasing_mode:
                if new_head[0] >= WIDTH - sidebar_width:
                    # Phase left
                    new_head = (0, new_head[1] % HEIGHT)
                elif new_head[0] < 0:
                    # phase right
                    new_head = ((WIDTH - sidebar_width) // CELL_SIZE * CELL_SIZE, new_head[1] % HEIGHT)
                elif new_head[1] < 0:
                    # phase down
                    new_head = (new_head[0] % WIDTH, (HEIGHT // CELL_SIZE - 1) * CELL_SIZE)
                elif new_head[1] >= HEIGHT:
                    #phase up
                    new_head = (new_head[0] % WIDTH, 0)

            for food in foods:
                if new_head[:2] == food[:2]:
                    score += 1
                    foods.remove(food)
                    foods.extend(spawn_fruits(1)) 
                    eat_sound.play() 
                    break
            else:
                snake.pop()

        
            if not phasing_mode and new_head in snake[1:]:
                game_over = True
                pygame.mixer.music.stop()  
                game_over_sound.play()  
            else:
                snake.insert(0, new_head)

    screen.blit(background_image, (0, 0))
    pygame.draw.rect(screen, GRAY, sidebar_rect)

    # sidebar adjustment
    font_sidebar_size = 10 if not fullscreen else 18  
    font_sidebar = pygame.font.SysFont("Segoe UI", font_sidebar_size)

    instructions = [
        "Instructions:",
        "Use Arrow Keys to Move",
        "Press P to Toggle Phasing",
        "Press F to Toggle Fullscreen",
        "Press S to Toggle Score Display",
        "Press 1, 2, 3 to Change Speed"
    ]


    text_y = 120 if not fullscreen else 350

    for text in instructions:
        text_render = font_sidebar.render(text, True, WHITE)
        text_rect = text_render.get_rect(topleft=(WIDTH - sidebar_width + 10, text_y))
        screen.blit(text_render, text_rect)
        text_y += 30  # Increase y-coordinate for each text

    #phasing on off
        phasing_mode_text = font_sidebar.render(f"Phasing: {'On' if phasing_mode else 'Off'}", True, WHITE)
        screen.blit(phasing_mode_text, (WIDTH - sidebar_width + 10, HEIGHT - 90))

    #score
    if show_score:
        score_text = font_sidebar.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - sidebar_width + 10, HEIGHT - 60))

    #snakecolour
    for i, segment in enumerate(snake):
        color = DARK_GREEN if i % 2 == 0 else GREEN  # Alternate colors for stripes
        pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    #randomcolour food
    for food in foods:
        pygame.draw.rect(screen, food[2], pygame.Rect(food[0], food[1], CELL_SIZE, CELL_SIZE))

    if game_over:
        # game over
        game_over_font = pygame.font.SysFont("Comic Sans Ms", 72) 
        game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(game_over_text, game_over_rect)

        #Press R to restart
        restart_font = pygame.font.SysFont("Arial Black", 15)  
        restart_text = restart_font.render("Press R to restart", True, (128, 128, 128))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(restart_text, restart_rect)

    snake_position = (WIDTH - sidebar_width, 0) 
    screen.blit(snake_image, snake_position)

    pygame.display.flip()
    pygame.time.Clock().tick(current_speed)
