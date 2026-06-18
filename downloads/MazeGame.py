import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

#Game settings
TILE_SIZE = 35
FPS = 60
maze = [
    "1111110111111",
    "1000100000001",
    "1010110101101",
    "1010010101001",
    "1000110100011",
    "1110110111001",
    "1000110101101",
    "1011110100001",
    "1010000110111",
    "1000111110001",
    "1110100000101",
    "1000101111101",
    "1011100010001",
    "1000101010101",
    "1110101010101",
    "1000101110101",
    "1011100010001",
    "1111111011111"
]

ROWS, COLS = len(maze), len(maze[0])
WIDTH = max(800, COLS * TILE_SIZE + 250)
HEIGHT = ROWS * TILE_SIZE + 150

#Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze of Monsters")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
big_font = pygame.font.SysFont(None, 48)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,50,50)
GREEN = (50,200,50)
BLUE = (50,50,200)
GRAY = (100,100,100)
YELLOW = (200,200,50)

def load_sprite(path):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE))

Player_sprite = load_sprite("Game/sprites/Player.png")
Monster_sprites = {
    "weak": load_sprite("Game/sprites/Monster1.png"),
    "normal": load_sprite("Game/sprites/Monster2.png"),
    "strong": load_sprite("Game/sprites/Monster4.png"),
    "boss": load_sprite("Game/sprites/Monster3.png")
}
Key = load_sprite("Game/sprites/KEY.png")
Pot_sprite = load_sprite("Game/sprites/Potion.png")
Sword_sound = pygame.mixer.Sound("Game/sound effects/sword-hit.mp3")

class Player:
    def __init__(self):
        self.x, self.y = 6, 0
        self.hp = self.max_hp = 100
        self.base_attack = self.attack = 10
        self.keys = self.points = self.kills = self.potions_collected = 0
        self.strength_hits = self.weakness_hits = 0

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def apply_effect(self, effect_type):
        if effect_type == "strength":
            self.strength_hits = 5
        elif effect_type == "weakness":
            self.weakness_hits = 2
        self.update_attack()

    def update_attack(self):
        self.attack = self.base_attack
        if self.strength_hits > 0:
            self.attack += 5
        if self.weakness_hits > 0:
            self.attack = max(1, self.attack - 5)

    def use_attack(self):
        if self.strength_hits > 0:
            self.strength_hits -= 1
        if self.weakness_hits > 0:
            self.weakness_hits -= 1
        self.update_attack()

class Monster:
    stats = {
        "weak": (15, 25, 3, 6, 20),
        "normal": (25, 35, 5, 8, 40),
        "strong": (35, 50, 8, 12, 60),
        "boss": (50, 70, 10, 15, 100)
    }

    def __init__(self, x, y, monster_type):
        self.x, self.y = x, y
        self.monster_type = monster_type
        min_hp, max_hp, self.min_attack, self.max_attack, self.points = self.stats[monster_type]
        self.hp = self.max_hp = random.randint(min_hp, max_hp)

    def get_attack_damage(self):
        return random.randint(self.min_attack, self.max_attack)

class Potion:
    def __init__(self, x, y, potion_type):
        self.x = x
        self.y = y
        self.type = potion_type
        self.collected = False

    def apply_effect(self, player):
        """Apply the potion's effect to the player and return message info"""
        if self.type == 'health':
            player.heal(40)
            return "HEALTH RESTORED!", GREEN
        elif self.type == 'poison':
            player.take_damage(20)
            return "POISONED!", RED
        elif self.type == 'strength':
            player.apply_effect("strength")
            return "STRENGTH BOOST!", GREEN
        elif self.type == 'weakness':
            player.apply_effect("weakness")
            return "WEAKENED!", RED

    def collect(self, player):
        """Collect the potion and apply its effect"""
        if not self.collected:
            self.collected = True
            player.potions_collected += 1
            return self.apply_effect(player)
        return None, None

def random_path():
    while True:
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if maze[y][x] == "0":
            return x, y

def far_from_exit(pos, exit_pos, min_dist=6):
    return abs(pos[0] - exit_pos[0]) + abs(pos[1] - exit_pos[1]) >= min_dist

def draw_bar(x, y, w, h, current, maximum):
    ratio = max(0, current/maximum) if maximum > 0 else 0
    pygame.draw.rect(screen, RED, (x, y, w, h))
    pygame.draw.rect(screen, GREEN, (x, y, w*ratio, h))
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    text = font.render(f"{current}/{maximum}", True, WHITE)
    screen.blit(text, (x + w + 5, y))

def draw_text(text, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))
    return y + 22

#Game objects
player = Player()
exit_pos = (7, 17)

#Monsters
exit_guard_pos = (exit_pos[0] - 1, exit_pos[1])
if maze[exit_guard_pos[1]][exit_guard_pos[0]] != "0":
    exit_guard_pos = (exit_pos[0], exit_pos[1] - 1)

monsters = [
    Monster(*random_path(), "weak"),
    Monster(*random_path(), "normal"),
    Monster(*exit_guard_pos, "strong"),
    Monster(*random_path(), "boss")
]

#Randomly puts key and potions around maze
potions = []
potion_types = ['health', 'poison', 'strength', 'weakness']
for _ in range(6):
    x, y = random_path()
    while (x, y) in [(6, 0), exit_pos]:
        x, y = random_path()
    potions.append(Potion(x, y, random.choice(potion_types)))

key_pos = random_path()
while not far_from_exit(key_pos, exit_pos):
    key_pos = random_path()

#Game status
in_combat = current_monster = None
key_msg_timer = potion_msg_timer = 0
potion_msg_text = ""
game_win = game_over = False

#Game looping
while True:
    clock.tick(FPS)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and (game_win or game_over):
                pygame.quit()
                sys.exit()

            if not (game_win or game_over):
                #Player movement
                dx = dy = 0
                if event.key in [pygame.K_w, pygame.K_UP]: dy = -1
                elif event.key in [pygame.K_s, pygame.K_DOWN]: dy = 1
                elif event.key in [pygame.K_a, pygame.K_LEFT]: dx = -1
                elif event.key in [pygame.K_d, pygame.K_RIGHT]: dx = 1

                if dx or dy:
                    nx, ny = player.x + dx, player.y + dy

                    #Monster collision check
                    for m in monsters:
                        if (m.x, m.y) == (nx, ny):
                            in_combat, current_monster = True, m
                            break
                    else:
                        #cHECKS IF PATH IS VALID
                        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == "0":
                            player.x, player.y = nx, ny

                            #Verifies if player has key to exit the maze
                            if (nx, ny) == exit_pos:
                                if player.keys:
                                    game_win = True
                                else:
                                    key_msg_timer = 120

                #Fighting
                elif event.key == pygame.K_SPACE and in_combat:
                    current_monster.hp -= player.attack
                    player.use_attack()
                    Sword_sound.play()

                    if current_monster.hp > 0:
                        player.take_damage(current_monster.get_attack_damage())
                    else:
                        player.points += current_monster.points
                        player.kills += 1
                        monsters.remove(current_monster)
                        in_combat = current_monster = None

                #Item collection when gone over it
                if (player.x, player.y) == key_pos:
                    player.keys = 1
                    key_pos = (-1, -1)

                for potion in potions:
                    if not potion.collected and (player.x, player.y) == (potion.x, potion.y):
                        msg, color = potion.collect(player)
                        if msg:
                            potion_msg_text, potion_msg_timer = msg, 60

    if player.hp <= 0:
        game_over = True

    #Maze creation
    maze_offset = (10, 30)
    for y in range(ROWS):
        for x in range(COLS):
            if maze[y][x] == "1":
                pygame.draw.rect(screen, GRAY,
                    (x*TILE_SIZE + maze_offset[0], y*TILE_SIZE + maze_offset[1], TILE_SIZE, TILE_SIZE))

    #Sprite creations
    screen.blit(Player_sprite, (player.x*TILE_SIZE + maze_offset[0], player.y*TILE_SIZE + maze_offset[1]))

    for m in monsters:
        screen.blit(Monster_sprites[m.monster_type],
            (m.x*TILE_SIZE + maze_offset[0], m.y*TILE_SIZE + maze_offset[1]))

    if key_pos != (-1, -1):
        screen.blit(Key, (key_pos[0]*TILE_SIZE + maze_offset[0], key_pos[1]*TILE_SIZE + maze_offset[1]))

    for potion in potions:
        if not potion.collected:
            screen.blit(Pot_sprite,
                (potion.x*TILE_SIZE + maze_offset[0], potion.y*TILE_SIZE + maze_offset[1]))

    pygame.draw.rect(screen, YELLOW,
        (exit_pos[0]*TILE_SIZE + maze_offset[0], exit_pos[1]*TILE_SIZE + maze_offset[1], TILE_SIZE, TILE_SIZE))

    #UI
    ui_x, ui_y = COLS * TILE_SIZE + 20, 30
    pygame.draw.rect(screen, (30, 30, 30), (ui_x - 10, 10, 230, HEIGHT - 20))
    pygame.draw.rect(screen, WHITE, (ui_x - 10, 10, 230, HEIGHT - 20), 2)

    ui_y = draw_text("=== PLAYER STATS ===", YELLOW, ui_x, ui_y) + 8
    ui_y = draw_text("Health:", WHITE, ui_x, ui_y) - 2
    draw_bar(ui_x, ui_y, 150, 15, player.hp, player.max_hp)
    ui_y += 35

    for stat in [f"Attack: {player.attack}", f"Keys: {player.keys}", f"Potions: {player.potions_collected}",
                 f"Points: {player.points}", f"Kills: {player.kills}"]:
        ui_y = draw_text(stat, WHITE, ui_x, ui_y)

    #Fighting UI
    if in_combat and current_monster:
        ui_y = draw_text("=== ENEMY ===", RED, ui_x, ui_y + 10)
        ui_y = draw_text(f"Type: {current_monster.monster_type.title()}", WHITE, ui_x, ui_y)
        ui_y = draw_text("Enemy Health:", WHITE, ui_x, ui_y) - 2
        draw_bar(ui_x, ui_y, 150, 15, current_monster.hp, current_monster.max_hp)
        ui_y = draw_text(f"Damage: {current_monster.min_attack}-{current_monster.max_attack}", WHITE, ui_x, ui_y + 25)
        draw_text("Press SPACE to attack!", YELLOW, ui_x, ui_y)

    #Potion effect status
    if player.strength_hits or player.weakness_hits:
        ui_y = draw_text("=== STATUS ===", YELLOW, ui_x, ui_y + 10)
        if player.strength_hits:
            ui_y = draw_text(f"STRENGTH: {player.strength_hits}", GREEN, ui_x, ui_y)
        if player.weakness_hits:
            ui_y = draw_text(f"WEAKNESS: {player.weakness_hits}", RED, ui_x, ui_y)

    #Text creation when needed
    if key_msg_timer > 0:
        draw_text("KEY REQUIRED FOR EXIT!", YELLOW, 50, HEIGHT-40)
        key_msg_timer -= 1
    if potion_msg_timer > 0:
        color = GREEN if "HEALTH" in potion_msg_text or "STRENGTH" in potion_msg_text else RED
        draw_text(potion_msg_text, color, 50, HEIGHT-60)
        potion_msg_timer -= 1

    draw_text("Use WASD/Arrow keys to move", WHITE, 10, 10)

    #Game stats
    if game_over or game_win:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        if game_over:
            screen.blit(big_font.render("YOU DIED", True, RED), (WIDTH//2-120, HEIGHT//2-50))
            screen.blit(font.render("Press ESC to exit", True, WHITE), (WIDTH//2-80, HEIGHT//2))
        else:
            screen.blit(big_font.render("YOU ESCAPED!", True, GREEN), (WIDTH//2-140, HEIGHT//2-100))
            stats = [f"Points: {player.points}", f"Monsters Killed: {player.kills}", f"Final HP: {player.hp}",
                    f"Potions Collected: {player.potions_collected}", f"Final Attack: {player.attack}"]
            for i, s in enumerate(stats):
                screen.blit(font.render(s, True, WHITE), (WIDTH//2-100, HEIGHT//2-50+i*25))
            screen.blit(font.render("Press ESC to exit", True, WHITE), (WIDTH//2-80, HEIGHT//2+75))

    pygame.display.flip()
