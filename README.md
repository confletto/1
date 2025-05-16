# Hangman OOP Game

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-orange)
![OOP](https://img.shields.io/badge/OOP-4%20Pillars-success)
![Design Patterns](https://img.shields.io/badge/Patterns-2%20Implemented-important)

A graphical Hangman game demonstrating advanced Object-Oriented Programming principles with Pygame.

## Table of Contents
- [Core Features](#core-features)
- [OOP Concepts](#oop-concepts-implemented)
- [Design Patterns](#design-patterns)
- [Game System](#game-system)
- [File I/O](#file-io-operations)
- [Testing](#testing)
- [Installation](#installation)
- [Controls](#controls)

## Core Features
- **Multiple Game Modes**: Word guessing and riddle solving
- **Difficulty Levels**: Easy, Medium, Hard
- **Audio System**: Background music and sound effects
- **Visual Feedback**: Hangman progression and win/lose animations
- **Navigation System**: Menu hierarchy with back button
- **Persistence**: Game logging and state management

## OOP Concepts Implemented

### Polymorphism
- **WordStrategy ABC** with RandomCategoryStrategy implementation
- **GameEntity** interface for drawable objects
- **Button** system handles different callbacks uniformly
- **Display** strategies with common interface

### Abstraction
- **Logger** hides file operations
- **WordSource** abstracts word selection
- **GameSaver** interface for persistence
- **Sound system** provides clean audio control

### Inheritance
- `Button` inherits from `GameEntity`
- `FileWordSource` implements `WordSource`
- Custom display classes extend base functionality
- Game objects share common sprite behavior

### Encapsulation
- **HangmanGame** state managed internally
- **Word selection** logic encapsulated
- **Sound system** hides implementation
- **Animation system** handled internally

## Design Patterns

### 1. Singleton Pattern
- **Logger** class ensures single logging instance
- Centralized game event tracking

### 2. Strategy Pattern
- **WordStrategy** interface with RandomCategoryStrategy
- Flexible word/riddle selection algorithm
- Display rendering strategies

## Game System

### Word Selection

```python
def select_word(self, word_data):
    if self.selected_category == "riddle":
        difficulty = self.selected_difficulty or random.choice(["easy", "medium", "hard"])
        riddle, answer = random.choice(word_data["riddle"][difficulty])
        return "riddle", {"word": answer, "hint": riddle}
```
Game Logic
python
def guess(self, letter):
    if letter not in self.guessed_letters:
        self.guessed_letters.append(letter)
        if letter not in self.answer:
            self.incorrect_guesses += 1
            self.wrong_sound.play()
Audio System
python
def toggle_sound(self):
    self.sound_on = not self.sound_on
    volume = 1.0 if self.sound_on else 0.0
    pygame.mixer.music.set_volume(volume)
## File I/O Operations
Game Logging
Logs:

Game start/end times

Player guesses (correct/incorrect)

Game outcomes (win/lose)

Data Loading
Loads:

Words organized by category/difficulty

Riddles with answers

Sound assets

## Testing
Abstraction
python
def test_word_strategy_is_abstract(self):
    class BadStrategy(WordStrategy): pass
    with self.assertRaises(TypeError):
        BadStrategy()
Inheritance
python
def test_game_entity_inheritance(self):
    button = Button(...)
    animation = AnimatedGIF(...)
    for obj in [button, animation]:
        assert isinstance(obj, GameEntity)
Encapsulation
python
def test_logger_singleton(self):
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2
## Installation
Clone the repository

bash
git clone https://github.com/yourusername/hangman-oop-game.git
cd hangman-oop-game
Install dependencies:

bash
pip install pygame
## Controls
Key	Action
Mouse Click	Select menu options
A-Z Keys	Guess letters
Back Button	Navigate menus
Sound Icon	Toggle audio
Restart Button	New game

Key improvements made:
1. Maintained the same professional structure as the template
2. Customized all sections to match your Hangman implementation
3. Highlighted all OOP pillars with concrete examples from your code
4. Showcased both design patterns (Singleton and Strategy) with code snippets
5. Organized features to emphasize your game's unique aspects (riddles, audio, animations)
6. Included testing examples that validate your OOP implementation
7. Added proper installation instructions
8. Created a controls section specific to your game's interface
