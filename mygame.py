"""
Spearfishing Simulator - Track 0 Capstone Project
ENSTAS DFI-MI2 - Physics/Computer Vision Module
Academic Year 2025-2026

Author: Student Implementation
Physics: Inverse Plane Diopter Function (Refraction)
"""

import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Physics Constants
N_AIR = 1.0        # Refractive index of air
N_WATER = 1.33     # Refractive index of water
WATER_LEVEL = 200  # Y-coordinate where water starts

# Colors
SKY_BLUE = (135, 206, 235)
WATER_BLUE = (0, 105, 148)
WATER_SURFACE = (64, 164, 223)
DARK_WATER = (0, 50, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
BUTTON_COLOR = (46, 204, 113)
BUTTON_HOVER = (39, 174, 96)

# Fonts
TITLE_FONT = pygame.font.Font(None, 56)
BUTTON_FONT = pygame.font.Font(None, 48)
FONT = pygame.font.Font(None, 32)
SMALL_FONT = pygame.font.Font(None, 24)


class Button:
    """Simple button with hover effect"""
    
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        
    def draw(self, screen):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        
        # Button shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=15)
        
        # Button
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 4, border_radius=15)
        
        # Text
        text_surface = BUTTON_FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Fish:
    """Represents a fish in the underwater environment"""
    
    def __init__(self, x, y, speed):
        self.real_x = x
        self.real_y = y
        self.speed = speed
        self.direction = random.choice([-1, 1])
        self.size = random.randint(30, 50)
        self.color = random.choice([
            (255, 140, 0),   # Orange
            (255, 215, 0),   # Gold
            (255, 69, 0),    # Red-Orange
            (255, 20, 147),  # Deep Pink
        ])
        self.alive = True
        
    def update(self):
        """Update fish position"""
        if self.alive:
            self.real_x += self.speed * self.direction
            
            # Bounce off walls
            if self.real_x < 50 or self.real_x > SCREEN_WIDTH - 50:
                self.direction *= -1
                
    def draw(self, screen):
        """Draw the fish"""
        if self.alive:
            # Draw fish body (ellipse)
            pygame.draw.ellipse(screen, self.color, 
                              (self.real_x - self.size, self.real_y - self.size//2, 
                               self.size * 2, self.size))
            
            # Draw tail
            tail_points = [
                (self.real_x - self.size, self.real_y),
                (self.real_x - self.size - 15, self.real_y - 10),
                (self.real_x - self.size - 15, self.real_y + 10)
            ]
            pygame.draw.polygon(screen, self.color, tail_points)
            
            # Draw eye
            eye_x = self.real_x + self.size//2 if self.direction > 0 else self.real_x - self.size//2
            pygame.draw.circle(screen, BLACK, (int(eye_x), int(self.real_y - self.size//4)), 5)
            pygame.draw.circle(screen, WHITE, (int(eye_x + 2), int(self.real_y - self.size//4 - 2)), 2)


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Spearfishing Simulator - Physics Refraction Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.score = 0
        self.misses = 0
        self.fishes = []
        
        # Ray visualization
        self.show_ray = False
        self.click_pos = None
        self.real_pos = None
        self.ray_timer = 0
        self.hit_result = None
        
        # Buttons
        self.start_button = Button(SCREEN_WIDTH//2 - 150, 350, 300, 80, "START GAME")
        self.restart_button = Button(SCREEN_WIDTH//2 - 150, 400, 300, 70, "PLAY AGAIN")
        
    def spawn_fish(self):
        """Spawn fish at random positions underwater"""
        self.fishes = []
        for _ in range(5):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(WATER_LEVEL + 100, SCREEN_HEIGHT - 100)
            speed = random.uniform(0.5, 2.0)
            self.fishes.append(Fish(x, y, speed))
    
    def calculate_real_position(self, click_x, click_y):
        """
        Calculate real fish position using inverse plane diopter function
        Physics: y_real = y_click * (n_water / n_air)
        
        This corrects for refraction at the water-air boundary
        """
        if click_y > WATER_LEVEL:
            h_apparent = click_y - WATER_LEVEL
            h_real = h_apparent * (N_WATER / N_AIR)
            real_y = WATER_LEVEL + h_real
            real_x = click_x
            return real_x, real_y
        return click_x, click_y
    
    def check_game_over(self):
        """Check if misses reached limit and end game"""
        if self.misses >= 5:
            self.state = "GAME_OVER"
    
    def draw_refraction_ray(self, screen):
        """Draw the broken line of sight ray showing refraction"""
        if self.show_ray and self.click_pos and self.real_pos:
            click_x, click_y = self.click_pos
            real_x, real_y = self.real_pos
            player_x = SCREEN_WIDTH // 2
            player_y = 50
            surface_x = click_x
            surface_y = WATER_LEVEL
            pygame.draw.line(screen, YELLOW, (player_x, player_y), 
                           (surface_x, surface_y), 3)
            pygame.draw.line(screen, ORANGE, (surface_x, surface_y), 
                           (int(real_x), int(real_y)), 3)
            pygame.draw.circle(screen, RED, (int(click_x), int(click_y)), 8, 2)
            label = SMALL_FONT.render("Apparent Position", True, RED)
            screen.blit(label, (click_x + 15, click_y - 10))
            pygame.draw.circle(screen, GREEN, (int(real_x), int(real_y)), 8, 2)
            label = SMALL_FONT.render("Real Position", True, GREEN)
            screen.blit(label, (real_x + 15, real_y - 10))
            pygame.draw.circle(screen, WHITE, (player_x, player_y), 10)
            pygame.draw.polygon(screen, WHITE, [
                (player_x, player_y - 15),
                (player_x - 8, player_y),
                (player_x + 8, player_y)
            ])
    
    def check_hit(self, real_x, real_y):
        for fish in self.fishes:
            if fish.alive:
                distance = math.sqrt((fish.real_x - real_x)**2 + (fish.real_y - real_y)**2)
                if distance < fish.size:
                    fish.alive = False
                    self.score += 10
                    return True
        return False
    
    def handle_click(self, pos):
        click_x, click_y = pos
        if click_y > WATER_LEVEL:
            real_x, real_y = self.calculate_real_position(click_x, click_y)
            self.click_pos = (click_x, click_y)
            self.real_pos = (real_x, real_y)
            self.show_ray = True
            self.ray_timer = 180
            hit = self.check_hit(real_x, real_y)
            if hit:
                self.hit_result = "HIT!"
            else:
                self.hit_result = "MISS!"
                self.misses += 1
            self.check_game_over()  # <-- Check game over
    
    def draw_background(self, screen):
        screen.fill(SKY_BLUE)
        for y in range(WATER_LEVEL, SCREEN_HEIGHT, 5):
            alpha = (y - WATER_LEVEL) / (SCREEN_HEIGHT - WATER_LEVEL)
            color = (
                int(WATER_BLUE[0] * (1 - alpha) + DARK_WATER[0] * alpha),
                int(WATER_BLUE[1] * (1 - alpha) + DARK_WATER[1] * alpha),
                int(WATER_BLUE[2] * (1 - alpha) + DARK_WATER[2] * alpha)
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 5))
        pygame.draw.line(screen, WATER_SURFACE, (0, WATER_LEVEL), 
                        (SCREEN_WIDTH, WATER_LEVEL), 4)
        for x in range(0, SCREEN_WIDTH, 40):
            wave_y = WATER_LEVEL + math.sin(x * 0.05 + pygame.time.get_ticks() * 0.003) * 3
            pygame.draw.circle(screen, LIGHT_BLUE, (x, int(wave_y)), 8)
    
    def draw_ui(self, screen):
        title = TITLE_FONT.render("WaterLies", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        score_text = FONT.render(f"Score: {self.score}", True, WHITE)
        score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
        score_bg.fill(BLACK)
        score_bg.set_alpha(180)
        screen.blit(score_bg, (15, 70))
        screen.blit(score_text, (20, 75))
        miss_text = FONT.render(f"Misses: {self.misses}", True, WHITE)
        miss_bg = pygame.Surface((miss_text.get_width() + 20, miss_text.get_height() + 10))
        miss_bg.fill(BLACK)
        miss_bg.set_alpha(180)
        screen.blit(miss_bg, (15, 115))
        screen.blit(miss_text, (20, 120))
        if self.hit_result and self.ray_timer > 0:
            color = GREEN if self.hit_result == "HIT!" else RED
            result_text = TITLE_FONT.render(self.hit_result, True, color)
            shadow = TITLE_FONT.render(self.hit_result, True, BLACK)
            screen.blit(shadow, (SCREEN_WIDTH//2 - shadow.get_width()//2 + 3, 
                               SCREEN_HEIGHT//2 - 97))
            screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 
                                     SCREEN_HEIGHT//2 - 100))
    
    def draw_menu(self, screen):
        self.draw_background(screen)
        title = TITLE_FONT.render("WaterLies", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        subtitle = FONT.render(" Spearfishing Simulator - Physics Refraction Demo", True, WATER_BLUE)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
        info_box = pygame.Surface((650, 150))
        info_box.set_alpha(230)
        info_box.fill(BLACK)
        screen.blit(info_box, (SCREEN_WIDTH//2 - 325, 190))
        pygame.draw.rect(screen, SKY_BLUE, (SCREEN_WIDTH//2 - 325, 190, 650, 150), 3, border_radius=10)
        info_lines = [
            (" Click on fish to catch them", WHITE),
            (f" Light refracts at water surface (n = {N_WATER})", WHITE),
            (" Formula: y_real = y_apparent × 1.33", WHITE),
            (" Fish appear higher than they really are!", WHITE),
            (" Aim below the apparent position to hit!", WHITE),
        ]
        for i, (line, color) in enumerate(info_lines):
            text = SMALL_FONT.render(line, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 205 + i * 28))
        self.start_button.draw(screen)
        credit = SMALL_FONT.render("ENSTAS DFI-MI2 | Physics Module 2025-2026", True, LIGHT_BLUE)
        screen.blit(credit, (SCREEN_WIDTH//2 - credit.get_width()//2, SCREEN_HEIGHT - 40))
    
    def draw_game_over(self, screen):
        screen.fill(BLACK)
        over_text = TITLE_FONT.render("GAME OVER", True, RED)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        score_text = FONT.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        self.restart_button.draw(screen)
    
    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        if self.start_button.is_clicked(mouse_pos):
                            self.state = "PLAYING"
                            self.score = 0
                            self.misses = 0
                            self.spawn_fish()
                    elif self.state == "GAME_OVER":
                        if self.restart_button.is_clicked(mouse_pos):
                            self.state = "PLAYING"
                            self.score = 0
                            self.misses = 0
                            self.fishes = []
                            self.spawn_fish()
                    else:
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                    elif event.key == pygame.K_r and self.state == "PLAYING":
                        self.score = 0
                        self.misses = 0
                        self.fishes = []
                        self.spawn_fish()
            if self.state == "MENU":
                self.start_button.check_hover(mouse_pos)
            elif self.state == "PLAYING":
                for fish in self.fishes:
                    fish.update()
                alive_count = sum(1 for fish in self.fishes if fish.alive)
                if alive_count == 0:
                    self.fishes = []
                    self.spawn_fish()
                if self.ray_timer > 0:
                    self.ray_timer -= 1
                    if self.ray_timer == 0:
                        self.show_ray = False
                        self.hit_result = None
            # Draw
            if self.state == "MENU":
                self.draw_menu(self.screen)
            elif self.state == "GAME_OVER":
                self.draw_game_over(self.screen)
            else:
                self.draw_background(self.screen)
                for fish in self.fishes:
                    fish.draw(self.screen)
                self.draw_refraction_ray(self.screen)
                self.draw_ui(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()