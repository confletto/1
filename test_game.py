def draw_game(self):
    # Clear screen with background color
    self.screen.fill(LILAC)

    # Draw hangman image (only if game isn't won yet)
    if not self.game.has_won():
        hangman_img = self.game.images[self.game.incorrect_guesses]
        self.screen.blit(hangman_img, (20, 50))  # Position adjusted

    # Game title
    title = self.title_font.render("Hangman Game", True, PURPLE)
    self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # Display current word with blanks/letters
    display_word = " ".join([letter if letter in self.game.guessed_letters else "_"
                             for letter in self.game.answer])
    word_text = self.font.render(display_word, True, BLUE)
    self.screen.blit(word_text, (WIDTH // 2 - word_text.get_width() // 2, 200))

    # Display hint
    hint_text = self.font.render(f"Hint: {self.game.hint}", True, PURPLE)
    self.screen.blit(hint_text, (50, 300))

    # Display guessed letters
    correct = [l for l in self.game.guessed_letters if l in self.game.answer]
    incorrect = [l for l in self.game.guessed_letters if l not in self.game.answer]

    correct_text = self.font.render(f"Correct: {', '.join(correct)}", True, GREEN)
    incorrect_text = self.font.render(f"Wrong: {', '.join(incorrect)}", True, RED)

    self.screen.blit(correct_text, (50, 350))
    self.screen.blit(incorrect_text, (50, 400))

    # Display remaining attempts
    attempts = self.font.render(f"Attempts left: {MAX_TRIES - self.game.incorrect_guesses}", True, BLACK)
    self.screen.blit(attempts, (WIDTH - 200, 50))

    # Win/Lose messages
    if self.game.has_won():
        win_text = self.title_font.render("You Won!", True, GREEN)
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 450))
        self.play_sound(self.game.win_sound)
    elif self.game.has_lost():
        lose_text = self.title_font.render(f"Game Over! Word: {self.game.answer}", True, RED)
        self.screen.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, 450))
        self.play_sound(self.game.lose_sound)

    # Draw buttons and other UI elements
    self.draw_sound_button(self.screen)
    self.draw_back_button(self.screen)
    for button in self.buttons:
        button.draw(self.screen)

    pygame.display.flip()