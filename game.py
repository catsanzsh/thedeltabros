import pygame
import random
import math
from abc import ABC, abstractmethod

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class GameObject(ABC):
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.math.Vector2(0, 0)

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

class Character(GameObject):
    def __init__(self, x, y, width, height, health, attack, defense):
        super().__init__(x, y, width, height)
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.is_attacking = False
        self.attack_cooldown = 0
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def take_damage(self, amount):
        actual_damage = max(1, amount - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

class Mario(Character):  # Kris equivalent
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, 100, 15, 10)
        self.color = BLUE

    def update(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.move(dx, dy)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw health bar
        health_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 10,
                                    self.rect.width * (self.health / self.max_health), 5)
        pygame.draw.rect(screen, RED, health_bar_rect)

class Peach(Character):  # Susie equivalent
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, 120, 20, 8)
        self.color = (255, 192, 203)  # Pink

    def update(self):
        if not self.is_attacking:
            # Basic AI movement
            pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        health_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 10,
                                    self.rect.width * (self.health / self.max_health), 5)
        pygame.draw.rect(screen, RED, health_bar_rect)

class Bowser(Character):  # Lancer equivalent
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, 150, 25, 15)
        self.color = (139, 69, 19)  # Brown
        self.movement_pattern = 0
        self.pattern_timer = 0

    def update(self):
        self.pattern_timer += 1
        if self.pattern_timer >= 60:  # Change pattern every second
            self.movement_pattern = (self.movement_pattern + 1) % 4
            self.pattern_timer = 0

        # Simple movement patterns
        if self.movement_pattern == 0:
            self.rect.x += self.speed
        elif self.movement_pattern == 1:
            self.rect.x -= self.speed
        elif self.movement_pattern == 2:
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed

        # Keep within screen bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        health_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 10,
                                    self.rect.width * (self.health / self.max_health), 5)
        pygame.draw.rect(screen, RED, health_bar_rect)

class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0  # 0 for player, 1 for enemy
        self.actions = ["FIGHT", "ACT", "ITEM", "MERCY"]
        self.selected_action = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if self.turn == 0:  # Player's turn
            if keys[pygame.K_SPACE] and not self.player.is_attacking:
                if self.actions[self.selected_action] == "FIGHT":
                    damage = self.player.attack
                    self.enemy.take_damage(damage)
                    self.turn = 1
                    self.player.is_attacking = True
                    self.player.attack_cooldown = 30
        else:  # Enemy's turn
            if not self.enemy.is_attacking:
                damage = self.enemy.attack
                self.player.take_damage(damage)
                self.turn = 0
                self.enemy.is_attacking = True
                self.enemy.attack_cooldown = 30

    def draw(self, screen):
        # Draw battle menu
        menu_height = 100
        menu_rect = pygame.Rect(0, SCREEN_HEIGHT - menu_height, SCREEN_WIDTH, menu_height)
        pygame.draw.rect(screen, WHITE, menu_rect)

        # Draw action options
        font = pygame.font.Font(None, 36)
        for i, action in enumerate(self.actions):
            color = RED if i == self.selected_action else BLACK
            text = font.render(action, True, color)
            screen.blit(text, (50 + i * 200, SCREEN_HEIGHT - 60))

class MenuItem:
    def __init__(self, text, action, position, size=36):
        self.text = text
        self.action = action
        self.position = position
        self.size = size
        self.font = pygame.font.Font(None, size)
        self.is_selected = False
        self.color = WHITE
        self.hover_color = (255, 215, 0)  # Gold color for hover

    def draw(self, screen):
        color = self.hover_color if self.is_selected else self.color
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.position)
        screen.blit(text_surface, text_rect)

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_index = 0
        center_x = SCREEN_WIDTH // 2

        # Create menu items
        self.menu_items = [
            MenuItem("Start Game", "start", (center_x, 250)),
            MenuItem("Settings", "settings", (center_x, 350)),
            MenuItem("Credits", "credits", (center_x, 450)),
            MenuItem("Quit", "quit", (center_x, 550))
        ]

        # Title properties
        self.title_font = pygame.font.Font(None, 72)
        self.title_text = "Mario's Dark World"
        self.title_pos = (center_x, 120)

        # Create pulsing effect for title
        self.pulse_value = 0
        self.pulse_speed = 0.05

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                return self.menu_items[self.selected_index].action
        return None

    def update(self):
        # Update pulse effect
        self.pulse_value = (self.pulse_value + self.pulse_speed) % (2 * math.pi)

        # Update selected state for menu items
        for i, item in enumerate(self.menu_items):
            item.is_selected = (i == self.selected_index)

    def draw(self):
        # Draw background
        self.screen.fill((40, 40, 40))  # Dark gray background

        # Draw title with pulse effect
        pulse_factor = (math.sin(self.pulse_value) + 1) / 2  # Value between 0 and 1
        title_color = (255,
                      int(215 + 40 * pulse_factor),
                      int(0 + 40 * pulse_factor))
        title_surface = self.title_font.render(self.title_text, True, title_color)
        title_rect = title_surface.get_rect(center=self.title_pos)
        self.screen.blit(title_surface, title_rect)

        # Draw menu items
        for item in self.menu_items:
            item.draw(self.screen)

        # Draw version number
        version_font = pygame.font.Font(None, 24)
        version_text = version_font.render("v1.0.0", True, (128, 128, 128))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        self.screen.blit(version_text, version_rect)

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_index = 0
        center_x = SCREEN_WIDTH // 2

        self.settings = {
            "Music Volume": 70,
            "Sound Effects": 80,
            "Screen Shake": True,
            "Difficulty": "Normal"
        }

        # Create menu items
        self.menu_items = [
            MenuItem("Music Volume", "music", (center_x, 200)),
            MenuItem("Sound Effects", "sound", (center_x, 300)),
            MenuItem("Screen Shake", "shake", (center_x, 400)),
            MenuItem("Difficulty", "difficulty", (center_x, 500)),
            MenuItem("Back", "back", (center_x, 550))
        ]

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                return self.menu_items[self.selected_index].action
            elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                self.adjust_setting(event.key == pygame.K_RIGHT)
        return None

    def adjust_setting(self, increase):
        setting = self.menu_items[self.selected_index].action
        if setting in ["music", "sound"]:
            current = self.settings["Music Volume" if setting == "music" else "Sound Effects"]
            delta = 10 if increase else -10
            self.settings["Music Volume" if setting == "music" else "Sound Effects"] = max(0, min(100, current + delta))
        elif setting == "shake":
            self.settings["Screen Shake"] = not self.settings["Screen Shake"]
        elif setting == "difficulty":
            difficulties = ["Easy", "Normal", "Hard"]
            current_index = difficulties.index(self.settings["Difficulty"])
            new_index = (current_index + (1 if increase else -1)) % len(difficulties)
            self.settings["Difficulty"] = difficulties[new_index]

    def draw(self):
        self.screen.fill((40, 40, 40))

        # Draw title
        title_font = pygame.font.Font(None, 72)
        title_surface = title_font.render("Settings", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)

        # Draw menu items and their values
        for i, item in enumerate(self.menu_items):
            item.is_selected = (i == self.selected_index)
            item.draw(self.screen)

            # Draw setting values
            if item.action in ["music", "sound"]:
                value = self.settings["Music Volume" if item.action == "music" else "Sound Effects"]
                value_text = f"{value}%"
            elif item.action == "shake":
                value_text = "On" if self.settings["Screen Shake"] else "Off"
            elif item.action == "difficulty":
                value_text = self.settings["Difficulty"]
            elif item.action == "back":
                continue

            value_surface = pygame.font.Font(None, 36).render(value_text, True, WHITE)
            value_rect = value_surface.get_rect(midleft=(item.position[0] + 150, item.position[1]))
            self.screen.blit(value_surface, value_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario's Dark World")
        self.clock = pygame.time.Clock()
        self.is_running = True

        # Initialize game states
        self.state = "menu"  # Can be "menu", "settings", "game", "credits"
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen)

        # Initialize characters (will be created when game starts)
        self.mario = None
        self.peach = None
        self.bowser = None
        self.battle = None
        self.in_battle = False

    def init_game(self):
        # Initialize characters when starting a new game
        self.mario = Mario(100, 300)  # Kris
        self.peach = Peach(300, 300)  # Susie
        self.bowser = Bowser(500, 300)  # Lancer

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.state = "menu"
                    elif self.state == "settings":
                        self.state = "menu"
                    elif self.state == "menu":
                        self.is_running = False
                elif self.state == "menu":
                    action = self.main_menu.handle_input(event)
                    if action == "start":
                        self.state = "game"
                        self.init_game()
                    elif action == "settings":
                        self.state = "settings"
                    elif action == "quit":
                        self.is_running = False
                elif self.state == "settings":
                    action = self.settings_menu.handle_input(event)
                    if action == "back":
                        self.state = "menu"
                elif self.state == "game":
                    if event.key == pygame.K_b:
                        self.in_battle = not self.in_battle
                        if self.in_battle:
                            self.battle = Battle(self.mario, self.bowser)

    def update(self):
        if self.state == "menu":
            self.main_menu.update()
        elif self.state == "game":
            if self.in_battle:
                self.battle.update()
            else:
                self.mario.update()
                self.peach.update()
                self.bowser.update()

                # Check for collision with enemy to trigger battle
                if self.mario.rect.colliderect(self.bowser.rect):
                    self.in_battle = True
                    self.battle = Battle(self.mario, self.bowser)

    def draw(self):
        if self.state == "menu":
            self.main_menu.draw()
        elif self.state == "settings":
            self.settings_menu.draw()
        elif self.state == "game":
            self.screen.fill(BLACK)
            if self.in_battle:
                self.battle.draw(self.screen)
                self.mario.draw(self.screen)
                self.bowser.draw(self.screen)
            else:
                self.mario.draw(self.screen)
                self.peach.draw(self.screen)
                self.bowser.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
