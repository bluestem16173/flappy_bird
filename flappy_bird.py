import pygame
import json
import random
import os
import sys
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

class GameState(Enum):
    START_SCREEN = 1
    PLAYING = 2
    GAME_OVER = 3

class Player:
    def __init__(self, x, y, size, config):
        self.x = x
        self.y = y
        self.size = size
        self.velocity = 0  # Start with no velocity - bird doesn't fall initially
        self.gravity = config['player_settings']['gravity']
        self.jump_strength = config['player_settings']['jump_strength']
        self.max_fall_speed = config['player_settings']['max_fall_speed']
        
        # Load player image
        try:
            self.image = pygame.image.load('assets/images/hero.png')
            self.image = pygame.transform.scale(self.image, (size, size))
        except:
            # Fallback to colored rectangle if image not found
            self.image = pygame.Surface((size, size))
            self.image.fill((255, 255, 0))  # Yellow bird
        
        self.rect = pygame.Rect(x, y, size, size)
    
    def jump(self):
        self.velocity = self.jump_strength
    
    def update(self):
        # Apply gravity
        self.velocity += self.gravity
        if self.velocity > self.max_fall_speed:
            self.velocity = self.max_fall_speed
        
        # Update position
        self.y += self.velocity
        self.rect.y = self.y
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.rect.x = x
        self.rect.y = y

class Wall:
    def __init__(self, x, window_height, config):
        self.x = x
        self.width = config['wall_settings']['width']
        self.gap_size = config['wall_settings']['gap_size']
        self.speed = config['wall_settings']['speed']
        
        # Random gap position - ensure valid range
        min_gap_y = config['wall_settings']['min_height']
        max_gap_y = window_height - config['wall_settings']['min_height'] - self.gap_size
        gap_y = random.randint(min_gap_y, max_gap_y)
        
        # Create top and bottom walls
        self.top_height = gap_y
        self.bottom_y = gap_y + self.gap_size
        self.bottom_height = window_height - self.bottom_y
        
        self.top_rect = pygame.Rect(x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(x, self.bottom_y, self.width, self.bottom_height)
        
        # Create a simple wall image
        self.wall_color = tuple(config['colors']['wall'])
        self.top_surface = pygame.Surface((self.width, self.top_height))
        self.top_surface.fill(self.wall_color)
        self.bottom_surface = pygame.Surface((self.width, self.bottom_height))
        self.bottom_surface.fill(self.wall_color)
        
        self.passed = False
    
    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen):
        screen.blit(self.top_surface, (self.x, 0))
        screen.blit(self.bottom_surface, (self.x, self.bottom_y))
    
    def is_off_screen(self, window_width):
        return self.x + self.width < 0
    
    def check_collision(self, player_rect):
        return (self.top_rect.colliderect(player_rect) or 
                self.bottom_rect.colliderect(player_rect))

class Enemy:
    def __init__(self, x, y, size, speed, config):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        
        # Load enemy image
        try:
            self.image = pygame.image.load('assets/images/enemy.png')
            self.image = pygame.transform.scale(self.image, (size, size))
        except:
            # Fallback to colored rectangle if image not found
            self.image = pygame.Surface((size, size))
            self.image.fill(tuple(config['colors']['enemy']))  # Red enemy
        
        self.rect = pygame.Rect(x, y, size, size)
        self.animation_timer = 0
    
    def update(self, player_x):
        # Move towards player
        if self.x > player_x:
            self.x -= self.speed
        else:
            self.x -= self.speed * 0.5  # Slower when past player
        
        self.rect.x = self.x
        
        # Simple flying animation
        self.animation_timer += 1
        if self.animation_timer % 20 == 0:  # Every 20 frames
            self.y += random.randint(-2, 2)
            self.rect.y = self.y
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def is_off_screen(self, window_width):
        return self.x + self.size < 0
    
    def check_collision(self, player_rect):
        return self.rect.colliderect(player_rect)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        sound_files = {
            'flap': 'assets/mp4/flap (1).mp3',
            'bg': 'assets/mp4/bg.mp3',
            'enemy': 'assets/mp4/enemy.mp3',
            'gameover': 'assets/mp4/gameover.mp3'
        }
        
        for name, file_path in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(file_path)
            except:
                print(f"Could not load sound: {file_path}")
                self.sounds[name] = None
    
    def play_sound(self, sound_name):
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()
    
    def play_background_music(self):
        if self.sounds.get('bg'):
            pygame.mixer.music.load('assets/mp4/bg.mp3')
            pygame.mixer.music.play(-1)  # Loop indefinitely

class ScoreManager:
    def __init__(self, config):
        self.score = 0
        self.high_score = 0
        self.high_score_file = config['scoring']['high_score_file']
        self.points_per_wall = config['scoring']['points_per_wall']
        self.points_per_enemy = config['scoring']['points_per_enemy_avoided']
        self.load_high_score()
    
    def load_high_score(self):
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, 'r') as f:
                    self.high_score = int(f.read().strip())
        except:
            self.high_score = 0
    
    def save_high_score(self):
        try:
            with open(self.high_score_file, 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
    
    def reset_score(self):
        self.score = 0

class FlappyBirdGame:
    def __init__(self):
        # Load configuration
        with open('game_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize game
        self.window_width = self.config['game_settings']['window_width']
        self.window_height = self.config['game_settings']['window_height']
        self.fps = self.config['game_settings']['fps']
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config['game_settings']['title'])
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.START_SCREEN
        self.current_level = 0
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.score_manager = ScoreManager(self.config)
        
        # Initialize game objects
        self.player = None
        self.walls = []
        self.enemies = []
        
        # Game variables
        self.wall_timer = 0
        self.enemy_timer = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load background
        try:
            self.background = pygame.image.load('assets/images/background.png')
            self.background = pygame.transform.scale(self.background, (self.window_width, self.window_height))
        except:
            self.background = None
        
        # Start background music
        self.sound_manager.play_background_music()
    
    def start_game(self):
        self.state = GameState.PLAYING
        self.score_manager.reset_score()
        
        # Initialize player
        player_config = self.config['player_settings']
        self.player = Player(
            player_config['start_x'],
            player_config['start_y'],
            player_config['size'],
            self.config
        )
        
        # Clear obstacles
        self.walls.clear()
        self.enemies.clear()
        
        # Reset timers
        self.wall_timer = 0
        self.enemy_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.START_SCREEN:
                        self.start_game()
                    elif self.state == GameState.PLAYING:
                        self.player.jump()
                        self.sound_manager.play_sound('flap')
                    elif self.state == GameState.GAME_OVER:
                        self.start_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.state == GameState.START_SCREEN:
                        self.start_game()
                    elif self.state == GameState.PLAYING:
                        self.player.jump()
                        self.sound_manager.play_sound('flap')
                    elif self.state == GameState.GAME_OVER:
                        self.start_game()
        
        return True
    
    def update_game(self):
        if self.state != GameState.PLAYING:
            return
        
        # Update player
        self.player.update()
        
        # Check if player hit ground or ceiling
        if self.player.y + self.player.size >= self.window_height or self.player.y <= 0:
            self.game_over()
            return
        
        # Update walls
        for wall in self.walls[:]:
            wall.update()
            
            # Check collision
            if wall.check_collision(self.player.rect):
                self.game_over()
                return
            
            # Check scoring
            if not wall.passed and wall.x + wall.width < self.player.x:
                wall.passed = True
                self.score_manager.add_score(self.score_manager.points_per_wall)
            
            # Remove off-screen walls
            if wall.is_off_screen(self.window_width):
                self.walls.remove(wall)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x)
            
            # Check collision
            if enemy.check_collision(self.player.rect):
                self.sound_manager.play_sound('enemy')
                self.game_over()
                return
            
            # Remove off-screen enemies
            if enemy.is_off_screen(self.window_width):
                self.enemies.remove(enemy)
                self.score_manager.add_score(self.score_manager.points_per_enemy)
        
        # Spawn new walls
        level_config = self.config['levels'][self.current_level]
        self.wall_timer += 1
        if self.wall_timer >= 60:  # Spawn every second at 60 FPS
            new_wall = Wall(self.window_width, self.window_height, self.config)
            self.walls.append(new_wall)
            self.wall_timer = 0
        
        # Spawn new enemies
        self.enemy_timer += 1
        if (self.enemy_timer >= self.config['enemy_settings']['spawn_distance'] and 
            len(self.enemies) < self.config['enemy_settings']['max_enemies'] and
            random.random() < level_config['enemy_spawn_rate']):
            
            enemy_y = random.randint(
                self.window_height // 4,
                self.window_height - self.window_height // 4
            )
            self.enemies.append(Enemy(
                self.window_width,
                enemy_y,
                self.config['enemy_settings']['size'],
                level_config['enemy_speed'],
                self.config
            ))
            self.enemy_timer = 0
    
    def game_over(self):
        self.state = GameState.GAME_OVER
        self.sound_manager.play_sound('gameover')
    
    def draw_start_screen(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(tuple(self.config['colors']['background']))
        
        # Draw title
        title_text = self.font.render("Flappy Bird Game", True, tuple(self.config['colors']['text']))
        title_rect = title_text.get_rect(center=(self.window_width // 2, self.window_height // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw instructions
        instruction_text = self.small_font.render("Press SPACE or Click to Start", True, tuple(self.config['colors']['text']))
        instruction_rect = instruction_text.get_rect(center=(self.window_width // 2, self.window_height // 2 - 50))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw high score
        high_score_text = self.small_font.render(f"High Score: {self.score_manager.high_score}", True, tuple(self.config['colors']['text']))
        high_score_rect = high_score_text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(high_score_text, high_score_rect)
    
    def draw_game(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(tuple(self.config['colors']['background']))
        
        # Draw game objects
        for wall in self.walls:
            wall.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        if self.player:
            self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score_manager.score}", True, tuple(self.config['colors']['text']))
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.small_font.render(f"Level: {self.config['levels'][self.current_level]['name']}", True, tuple(self.config['colors']['text']))
        self.screen.blit(level_text, (10, 50))
    
    def draw_game_over(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(tuple(self.config['colors']['background']))
        
        # Draw game over text
        game_over_text = self.font.render("Game Over!", True, tuple(self.config['colors']['text']))
        game_over_rect = game_over_text.get_rect(center=(self.window_width // 2, self.window_height // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        final_score_text = self.font.render(f"Final Score: {self.score_manager.score}", True, tuple(self.config['colors']['text']))
        final_score_rect = final_score_text.get_rect(center=(self.window_width // 2, self.window_height // 2 - 50))
        self.screen.blit(final_score_text, final_score_rect)
        
        # Draw high score
        high_score_text = self.small_font.render(f"High Score: {self.score_manager.high_score}", True, tuple(self.config['colors']['text']))
        high_score_rect = high_score_text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Draw restart instruction
        restart_text = self.small_font.render("Press SPACE or Click to Restart", True, tuple(self.config['colors']['text']))
        restart_rect = restart_text.get_rect(center=(self.window_width // 2, self.window_height // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        if self.state == GameState.START_SCREEN:
            self.draw_start_screen()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
