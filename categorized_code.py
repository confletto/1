# hangman_oop_game.py
import pygame
import random
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime

# Constants
WIDTH, HEIGHT = 800, 600
LILAC = (168, 136, 181)
BLACK = (0, 0, 0)
PURPLE = (79, 28, 81)
BLUE = (22, 64, 214)
RED = (200, 0, 0)
GREEN = (52, 121, 40)
WHITE = (255, 255, 255)
BUTTON_HOVER = (133, 88, 133)  # New color for button hover
BUTTON_ACTIVE = (150, 120, 170)  # New color for button click
FONT_NAME = os.path.join("fonts", "Jersey10-Regular.ttf")
FONT_SIZE = 30
TITLE_FONT_SIZE = 50
MENU_TITLE_FONT_SIZE = 100
MAX_TRIES = 6
# Add with other constants
SOUND_ON_ICON = "assets1/sound_on.jpg"
SOUND_OFF_ICON = "assets1/sound_off.jpg"
# Add with other constants
BACK_ARROW_ICON = "assets1/back_arrow.png"  # Create a dark purple arrow image (30x30px)


# --- Logger Singleton ---
class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.log_file = open("game_log.txt", "a")
        return cls._instance

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(f"[{timestamp}] {message}\n")

    def __del__(self):
        self.log_file.close()


# --- Strategy Pattern ---
class WordStrategy(ABC):
    @abstractmethod
    def select_word(self, word_data):
        pass


class RandomCategoryStrategy(WordStrategy):
    def __init__(self, selected_category=None, selected_difficulty=None):
        self.selected_category = selected_category
        self.selected_difficulty = selected_difficulty

    def select_word(self, word_data):
        if self.selected_category == "riddle":
            difficulty = self.selected_difficulty or random.choice(["easy", "medium", "hard"])
            riddle, answer = random.choice(word_data["riddle"][difficulty])
            return "riddle", {"word": answer, "hint": riddle}
        else:
            # For "words" option, pick random category (animal/color/country/fruit)
            word_categories = [cat for cat in word_data.keys() if cat != "riddle"]
            category = random.choice(word_categories)
            difficulty = self.selected_difficulty or random.choice(["easy", "medium", "hard"])
            word = random.choice(word_data[category][difficulty])
            return category, word.lower()  # category becomes the hint


# --- GameEntity Base Class ---
class GameEntity(ABC):
    @abstractmethod
    def draw(self, surface):
        pass


# --- Button ---
class Button(GameEntity):
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.hover_color = BUTTON_HOVER
        self.active_color = BUTTON_ACTIVE
        self.callback = callback
        self.is_hovered = False
        self.is_active = False
        self.click_sound = pygame.mixer.Sound("assets1/sounds/click.wav")


    def draw(self, surface):
        current_color = self.active_color if self.is_active else (
            self.hover_color if self.is_hovered else self.color)
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, PURPLE, self.rect, 2)  # Add border
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        text_surf = font.render(self.text, True, PURPLE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


    # Inside Button class
    def handle_event(self, event, sound_enabled=True):  # Add sound_enabled parameter
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_active and self.rect.collidepoint(event.pos):
                if sound_enabled:  # Only play if sound is on
                    self.click_sound.play()
                self.callback()
            self.is_active = False

class AnimatedGIF:
    def __init__(self, frame_paths, position, frame_duration=300):
        self.frames = []
        for path in frame_paths:
            img = pygame.image.load(path).convert_alpha()
            # Uncomment below if you need to resize your GIF frames
            # img = pygame.transform.scale(img, (400, 400))  # Adjust size as needed
            self.frames.append(img)
        self.position = position
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.rect = self.frames[0].get_rect(center=(position[0], position[1]))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface):
        current_frame = self.frames[self.current_frame]
        surface.blit(current_frame, self.rect)


# --- Hangman Game ---
class HangmanGame:
    def __init__(self, app, word_selector, selected_category=None, selected_difficulty=None):
        self.app= app
        self.word_data = self.load_words()
        self.word_selector = word_selector
        self.selected_category = selected_category
        self.selected_difficulty = selected_difficulty
        self.logger = Logger()
        self.images = [pygame.image.load(f"assets1/hangman{i}.png") for i in range(7)]
        # Add these lines for sound effects
        self.correct_sound = pygame.mixer.Sound("assets1/sounds/correct.wav")
        self.correct_sound.set_volume(0.4)
        self.wrong_sound = pygame.mixer.Sound("assets1/sounds/wrong.wav")
        self.wrong_sound.set_volume(0.3)  # 50% volume
        self.win_sound = pygame.mixer.Sound("assets1/sounds/win.wav")
        self.win_sound.set_volume(0.4)
        self.lose_sound = pygame.mixer.Sound("assets1/sounds/lose.wav")
        self.lose_sound.set_volume(0.4)
        self.reset_game()
        self.sound_enabled = True  # Add this flag



    def reset_game(self):
        self.guessed_letters = []
        self.incorrect_guesses = 0
        # Get word/riddle from selector
        self.category, self.word = self.word_selector.select_word(self.word_data)
        # Set answer and hint
        if self.category == "riddle":
            self.answer = self.word["word"].lower()
            self.hint = self.word["hint"]
        else:
            self.answer = self.word.lower()
            self.hint = self.category

        self.logger.log(f"New game: Category={self.category}, Word={self.answer}")

    def load_words(self):
        with open("words.json") as f:
            words_data = json.load(f)
        with open("riddles.json") as f:
            words_data["riddle"] = json.load(f)  # Add riddles as a category
        return words_data

    def guess(self, letter):
        if letter not in self.guessed_letters:
            self.guessed_letters.append(letter)
            if letter not in self.answer:
                self.incorrect_guesses += 1
                self.app.play_sound(self.wrong_sound)
                self.logger.log(f"Wrong guess: {letter}")
            else:
                self.app.play_sound(self.correct_sound)
                self.logger.log(f"Correct guess: {letter}")

    def get_display_word(self):
        return ' '.join([l if l in self.guessed_letters else '_' for l in self.answer])

    def has_won(self):
        return '_' not in self.get_display_word()

    def has_lost(self):
        return self.incorrect_guesses >= MAX_TRIES

    def draw_hangman(self, surface):
        image = self.images[self.incorrect_guesses]
        x = WIDTH // 2 - image.get_width() // 2
        y = -100
        surface.blit(image, (x, y))


# --- App Interface ---
class HangmanApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.menu_title_font = pygame.font.Font(FONT_NAME, MENU_TITLE_FONT_SIZE)
        #background sound
        self.background_music = pygame.mixer.Sound("assets1/sounds/background.wav")
        self.background_music.play(loops=-1)  # -1 = infinite loop
        self.background_music.set_volume(1)  # 30% volume

        self.selected_category = None
        self.selected_difficulty = None
        self.game = None  # We'll initialize this later

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("OOP Hangman Game")
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.title_font = pygame.font.Font(FONT_NAME, TITLE_FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.running = True
        self.game_over = False
        self.current_screen = "menu"  # Can be "menu", "categories", "difficulty", or "game"
        self.initialize_buttons()
        # Add this with other initialization code
        self.win_animation = None
        self.win_frames = [f"assets1/win_{i}.png" for i in range(2)]  # Adjust based on your frames

        # ====== BUTTON POSITIONS UPDATE ======
        # Back button (top-left) - will be just an arrow icon
        self.back_arrow_img = pygame.image.load("assets1/back_arrow.jpg").convert_alpha()
        self.back_arrow_img = pygame.transform.scale(self.back_arrow_img, (30, 30))
        self.back_button_rect = pygame.Rect(10, 10, 30, 30)  # Positioned at top-left (10px from edges)

        # Sound button (top-right) - moved from left to right
        self.sound_on = True
        self.sound_on_img = pygame.image.load(SOUND_ON_ICON).convert_alpha()
        self.sound_off_img = pygame.image.load(SOUND_OFF_ICON).convert_alpha()
        self.sound_button_rect = pygame.Rect(WIDTH - 40, 10, 30, 30)  # Top-right (10px from right edge)


        # Scale down your 370x260 images to 30x30
        self.sound_on_img = pygame.transform.scale(self.sound_on_img, (30, 30))
        self.sound_off_img = pygame.transform.scale(self.sound_off_img, (30, 30))

    def play_sound(self, sound):
        """Plays a sound only if sound is enabled"""
        if self.sound_on and sound is not None:
            sound.play()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        # Set volume for all components
        volume = 1.0 if self.sound_on else 0.0
        self.background_music.set_volume(volume)
        # Update button sounds
        for button in self.buttons:
            if hasattr(button, 'click_sound'):
                button.click_sound.set_volume(volume)



    def initialize_buttons(self):
        self.buttons = []

        if self.current_screen == "menu":
            self.buttons.append(Button("Start Game", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, self.show_categories))
        elif self.current_screen == "categories":
            self.buttons.append(Button("Riddles", WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 60,
                                       lambda: self.select_category("riddle")))
            self.buttons.append(Button("Words", WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60,
                                       lambda: self.select_category("words")))
        elif self.current_screen == "difficulty":
            self.buttons.append(Button("Easy", WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60,
                                       lambda: self.select_difficulty("easy")))
            self.buttons.append(Button("Medium", WIDTH // 2 - 150, HEIGHT // 2, 300, 60,
                                       lambda: self.select_difficulty("medium")))
            self.buttons.append(Button("Hard", WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60,
                                       lambda: self.select_difficulty("hard")))
        elif self.current_screen == "game":
            self.buttons.append(Button("Restart", 650, 500, 110, 60, self.restart_game))

    def show_categories(self):
        self.current_screen = "categories"
        self.initialize_buttons()

    def select_category(self, category):
        self.selected_category = category
        self.current_screen = "difficulty"
        self.initialize_buttons()

    def select_difficulty(self, difficulty):
        self.selected_difficulty = difficulty
        self.current_screen = "game"
        self.initialize_buttons()

        # Create the strategy FIRST
        strategy = RandomCategoryStrategy(self.selected_category, self.selected_difficulty)

        # Pass parameters in CORRECT ORDER:
        self.game = HangmanGame(
            self,  # app reference
            strategy,  # word selector strategy
            self.selected_category,
            self.selected_difficulty
        )
        self.game_over = False

    def restart_game(self):
        self.game.reset_game()
        self.game.sound_enabled = self.sound_on  # Maintain sound state
        self.game_over = False
        if hasattr(self, 'win_animation'):
            self.win_animation = None

    def draw_text(self, text, pos, color=BLUE, font=None):
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, pos)

    def go_back(self):
        if self.current_screen == "game":
            self.current_screen = "difficulty"
        elif self.current_screen == "difficulty":
            self.current_screen = "categories"
        elif self.current_screen == "categories":
            self.current_screen = "menu"
        self.initialize_buttons()

    def draw_back_button(self, surface):
        if self.current_screen != "menu":  # No back button on main menu
            surface.blit(self.back_arrow_img, self.back_button_rect)


    def draw_sound_button(self, surface):
        current_icon = self.sound_on_img if self.sound_on else self.sound_off_img
        # Optional: Add white background
        pygame.draw.rect(surface, WHITE, self.sound_button_rect)
        # Draw icon
        surface.blit(current_icon, self.sound_button_rect)
        # Add purple border
        pygame.draw.rect(surface, PURPLE, self.sound_button_rect, 2)

    def draw_menu(self):
        self.draw_text("Hangman Game", (WIDTH // 2 - 250, HEIGHT // 4), PURPLE, self.menu_title_font)
        for button in self.buttons:
            button.draw(self.screen)
        self.draw_sound_button(self.screen)


    def draw_categories(self):
        self.draw_text("Categories", (WIDTH // 2 - 100, HEIGHT // 4), PURPLE, self.title_font)
        for button in self.buttons:
            button.draw(self.screen)
        self.draw_sound_button(self.screen)
        self.draw_back_button(self.screen)

    def draw_difficulty(self):
        self.draw_text("Difficulty Level", (WIDTH // 2 - 125, HEIGHT // 6), PURPLE, self.title_font)
        for button in self.buttons:
            button.draw(self.screen)
        self.draw_sound_button(self.screen)
        self.draw_back_button(self.screen)

    def draw_game(self):
            # Only draw hangman progression if game isn't won yet
        if not self.game.has_won():
            hangman_img = self.game.images[self.game.incorrect_guesses]
            hangman_x = -5
            hangman_y = -100  # 50 pixels from top
            self.screen.blit(hangman_img, (hangman_x, hangman_y))
        self.draw_sound_button(self.screen)
        self.draw_back_button(self.screen)

        # Win animation (if won)
        if self.game.has_won():
            if self.win_animation is None:
                    self.play_sound(self.game.win_sound)
                    # Center the animation with these coordinates
                    win_x = WIDTH // 2 - 8  # Adjust based on your GIF size
                    win_y = 200  # Below hangman area
                    self.win_animation = AnimatedGIF(self.win_frames, (win_x, win_y))
            self.win_animation.update()
            self.win_animation.draw(self.screen)
            self.draw_text("You Won!", (WIDTH // 2 - 52, 350), GREEN)  # Position below GIF
            self.game_over = True
        elif self.game.has_lost():
            if not self.game_over:  # Only play sound once
                self.play_sound(self.game.lose_sound)
                self.game_over = True
            self.draw_text(f"You Lost! Word: {self.game.answer}", (WIDTH // 2 - 145, 350), RED)

        # Bottom-left texts
        self.draw_text(f"Hint: {self.game.hint}", (50, 400), BLUE)
        self.draw_text(f"Word: {self.game.get_display_word()}", (50, 440), BLACK)
        correct_letters = ' '.join([l for l in self.game.guessed_letters if l in self.game.answer])
        incorrect_letters = ' '.join([l for l in self.game.guessed_letters if l not in self.game.answer])
        self.draw_text(f"Correct guesses: {correct_letters}", (50, 480), GREEN)
        self.draw_text(f"Incorrect guesses: {incorrect_letters}", (50, 520), RED)

        for button in self.buttons:
            button.draw(self.screen)

    def run(self):
        while self.running:
            self.screen.fill(LILAC)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Back button (top-left)
                    if self.back_button_rect.collidepoint(event.pos) and self.current_screen != "menu":
                        self.go_back()
                    # Sound button (top-right)
                    elif self.sound_button_rect.collidepoint(event.pos):
                        self.toggle_sound()

                if self.current_screen == "game" and not self.game_over:
                    if event.type == pygame.KEYDOWN and event.unicode.isalpha():
                        self.game.guess(event.unicode.lower())

                for button in self.buttons:
                    button.handle_event(event, self.sound_on)

            if self.current_screen == "menu":
                self.draw_menu()
            elif self.current_screen == "categories":
                self.draw_categories()
            elif self.current_screen == "difficulty":
                self.draw_difficulty()
            elif self.current_screen == "game":
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


# --- Run App ---
if __name__ == "__main__":
    HangmanApp().run()
