import pgzrun
import random

# Game configuration
WIDTH = 640
HEIGHT = 480
HERO_X_START = 30
HERO_Y_START = 400
HERO_SPEED = 5
ENEMY_Y = 400
GROUND_Y = 400
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLATFORM_COLLISION_TOLERANCE = 15
FONTCOLOR = (255, 255, 255)
GAME_OVER_COLOR = (0,0,0)

MENU = 0
PLAYING = 1
GAME_OVER = 2

game_state = MENU
score = 0
music_on = True
m_key_cooldown = 0
M_KEY_DELAY = 18

IDLE_FRAMES = ['idle_1', 'idle_2', 'idle_3', 'idle_4', 'idle_5', 'idle_6',
               'idle_7', 'idle_8', 'idle_9', 'idle_10', 'idle_11', 'idle_12']
RUN_FRAMES_RIGHT = ['bunny_1', 'bunny_2', 'bunny_3', 'bunny_4', 'bunny_5', 
                    'bunny_6', 'bunny_7', 'bunny_8']
RUN_FRAMES_LEFT = ['bunny_left_1', 'bunny_left_2', 'bunny_left_3', 'bunny_left_4', 
                   'bunny_left_5', 'bunny_left_6', 'bunny_left_7', 'bunny_left_8']
ENEMY_FRAMES = ['burning_loop_1', 'burning_loop_2', 'burning_loop_3', 'burning_loop_4', 
                'burning_loop_5', 'burning_loop_6', 'burning_loop_7', 'burning_loop_8']


class Hero:
    
    def __init__(self, x, y):
        self.actor = Actor('idle_1')
        self.actor.pos = (x, y)
        self.velocity_y = 0
        self.velocity_x = 0
        self.is_jumping = False
        self.is_on_platform = False
        self.is_moving_right = False
        self.is_moving_left = False
        self.idle_counter = 0
        self.run_counter = 0
        
    def move_left(self):
        if self.actor.x > 0:
            self.actor.x -= HERO_SPEED
            self.velocity_x = -HERO_SPEED
            self.is_moving_left = True
            self.is_moving_right = False
            
    def move_right(self):
        if self.actor.x < WIDTH:
            self.actor.x += HERO_SPEED
            self.velocity_x = HERO_SPEED
            self.is_moving_right = True
            self.is_moving_left = False
            
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True
            self.is_on_platform = False
            
    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y
        
    def check_ground_collision(self):
        if self.actor.y >= HERO_Y_START:
            self.actor.y = HERO_Y_START
            self.velocity_y = 0
            self.is_jumping = False
            self.is_on_platform = False
            
    def check_platform_collision(self, platforms):
        self.is_on_platform = False
        for platform in platforms:
            if self.velocity_y > 0:
                if self.actor.colliderect(platform.actor):
                    if self.actor.bottom <= platform.actor.top + PLATFORM_COLLISION_TOLERANCE:
                        self.actor.bottom = platform.actor.top
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.is_on_platform = True
                        
                        if platform.platform_type == 'horizontal':
                            self.actor.x += platform.speed * platform.direction
                        elif platform.platform_type == 'vertical':
                            self.actor.y += platform.speed * platform.direction
                        break
                        
    def animate_idle(self):
        if not self.is_jumping and not self.is_moving_right and not self.is_moving_left:
            self.actor.image = IDLE_FRAMES[self.idle_counter % len(IDLE_FRAMES)]
            self.idle_counter += 1
            
    def animate_run(self):
        if not self.is_jumping:
            if self.is_moving_right:
                self.actor.image = RUN_FRAMES_RIGHT[self.run_counter % len(RUN_FRAMES_RIGHT)]
                self.run_counter += 1
            elif self.is_moving_left:
                self.actor.image = RUN_FRAMES_LEFT[self.run_counter % len(RUN_FRAMES_LEFT)]
                self.run_counter += 1
                
    def reset_movement(self):
        self.velocity_x = 0
        self.is_moving_right = False
        self.is_moving_left = False
        
    def draw(self):
        self.actor.draw()


class Enemy:
    
    def __init__(self, x, y, speed, min_x, max_x):
        self.actor = Actor('burning_loop_1')
        self.actor.pos = (x, y)
        self.speed = speed
        self.direction = 1
        self.min_x = min_x
        self.max_x = max_x
        self.counter = 0
        
    def move(self):
        self.actor.x += self.speed * self.direction
        
        if self.actor.x >= self.max_x:
            self.direction = -1
        elif self.actor.x <= self.min_x:
            self.direction = 1
            
    def animate(self):
        self.actor.image = ENEMY_FRAMES[self.counter % len(ENEMY_FRAMES)]
        self.counter += 1
        
    def check_collision_with_hero(self, hero):
        return self.actor.colliderect(hero.actor)
        
    def draw(self):
        self.actor.draw()


class Platform:
    
    def __init__(self, x, y, platform_type='static', speed=0, min_pos=0, max_pos=0):
        self.actor = Actor('base')
        self.actor.pos = (x, y)
        self.platform_type = platform_type
        self.speed = speed
        self.direction = 1
        
        if platform_type == 'horizontal':
            self.min_x = min_pos
            self.max_x = max_pos
        elif platform_type == 'vertical':
            self.min_y = min_pos
            self.max_y = max_pos
            
    def move(self):
        if self.platform_type == 'horizontal':
            self.actor.x += self.speed * self.direction
            if self.actor.x >= self.max_x:
                self.direction = -1
            elif self.actor.x <= self.min_x:
                self.direction = 1
                
        elif self.platform_type == 'vertical':
            self.actor.y += self.speed * self.direction
            if self.actor.y >= self.max_y:
                self.direction = -1
            elif self.actor.y <= self.min_y:
                self.direction = 1
                
    def draw(self):
        self.actor.draw()


class Button:
    
    def __init__(self, x, y, width, height, text, color):
        self.rect = Rect((x, y), (width, height))
        self.text = text
        self.color = color
        self.hover_color = (200, 200, 200)
        self.is_hovered = False
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
        
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color=(0, 0, 0))


bg = Actor('background')
menu_bg = Actor('green')
target = Actor('target')
hero = Hero(HERO_X_START, HERO_Y_START)
enemies = []
platforms = []

start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50, 'START GAME', (100, 200, 100))
music_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, 'MUSIC: ON', (100, 100, 200))
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50, 'EXIT', (200, 100, 100))


def initialize_game_objects():
    global enemies, platforms, target
    
    enemies.clear()
    enemies.append(Enemy(200, 310, 0.5, 150, 250))
    enemies.append(Enemy(350, ENEMY_Y, 2, 100, 420))
    enemies.append(Enemy(550, ENEMY_Y, 1.5, 480, 600))
    
    platforms.clear()
    platforms.append(Platform(200, 350, 'static'))
    platforms.append(Platform(50, 250, 'horizontal', 2, 50, 350))
    platforms.append(Platform(500, 200, 'vertical', 1.5, 33, 350))
    
    target.pos = (random.randint(HERO_X_START, WIDTH - 30), random.randint(150, 300))


def reset_game():
    global score, hero
    score = 0
    hero = Hero(HERO_X_START, HERO_Y_START)
    initialize_game_objects()


def animate_characters():
    if game_state == PLAYING:
        hero.animate_idle()
        hero.animate_run()
        for enemy in enemies:
            enemy.animate()


def update():
    global score, game_state, music_on, m_key_cooldown
    
    if m_key_cooldown > 0:
        m_key_cooldown -= 1    
    if music_on and not music.is_playing('fantasygoodnight'):
        music.play('fantasygoodnight')
    elif not music_on:
        music.stop()    
    if game_state == MENU:
        return    
    if game_state == GAME_OVER:
        if keyboard.space:
            reset_game()
            game_state = PLAYING
        if keyboard.escape:
            game_state = MENU
        return    
    if game_state == PLAYING:
        hero.reset_movement()        
        if keyboard.left:
            hero.move_left()
        if keyboard.right:
            hero.move_right()
        if keyboard.up:
            hero.jump()        
        hero.apply_gravity()
        hero.check_platform_collision(platforms)
        hero.check_ground_collision()
        
        for platform in platforms:
            platform.move()        
        for enemy in enemies:
            enemy.move()
            if enemy.check_collision_with_hero(hero):
                game_state = GAME_OVER        
        if target.colliderect(hero.actor):
            sounds.coin.play()
            target.pos = (random.randint(HERO_X_START, WIDTH - 30), 
                         random.randint(150, 300))
            score += 1

def on_mouse_move(pos):
    if game_state == MENU:
        start_button.check_hover(pos)
        music_button.check_hover(pos)
        exit_button.check_hover(pos)

def on_mouse_down(pos):
    global game_state, music_on, m_key_cooldown
    
    if game_state == MENU:
        if start_button.is_clicked(pos):
            reset_game()
            game_state = PLAYING            
        elif music_button.is_clicked(pos) and m_key_cooldown == 0:
            music_on = not music_on
            m_key_cooldown = M_KEY_DELAY
            music_button.text = f'MUSIC: {"ON" if music_on else "OFF"}'            
        elif exit_button.is_clicked(pos):
            exit()


def draw():
    bg.draw()
    
    if game_state == MENU:
        menu_bg.draw()
        screen.draw.text('PYGAMEZERO GAME', center=(WIDTH*0.5, HEIGHT*0.2), 
                        fontsize=60, color='red', shadow=(0, 1))
        start_button.draw()
        music_button.draw()
        exit_button.draw()
        screen.draw.text('Use ARROW KEYS to move in game', center=(WIDTH//2, HEIGHT - 50), 
                        fontsize=20, color=FONTCOLOR)
        return
    if game_state == PLAYING:
        for platform in platforms:
            platform.draw()
        for enemy in enemies:
            enemy.draw()
        hero.draw()
        target.draw()
        screen.draw.text(f'Score: {score}', (15, 10), color=FONTCOLOR, fontsize=22) 
    if game_state == GAME_OVER:
        screen.draw.text('GAME OVER', center=(WIDTH//2, HEIGHT//3), 
                        fontsize=60, color='red', shadow=(0, 1))
        screen.draw.text(f'Final Score: {score}', center=(WIDTH//2, HEIGHT//2), 
                        fontsize=30, color=GAME_OVER_COLOR)
        screen.draw.text('SPACE - Play Again', center=(WIDTH//2, HEIGHT//2 + 60), 
                        fontsize=20, color=GAME_OVER_COLOR)
        screen.draw.text('ESC - Main Menu', center=(WIDTH//2, HEIGHT//2 + 90), 
                        fontsize=20, color=GAME_OVER_COLOR)

initialize_game_objects()
clock.schedule_interval(animate_characters, 0.1)
pgzrun.go()