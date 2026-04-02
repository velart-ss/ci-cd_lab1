import pygame
import argparse
import random
import sys

class Config:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Battleship Game")
        parser.add_argument("--bg", type=str, default="blue", choices=["blue", "black", "gray"],
                            help="Background color (blue, black, gray)")
        parser.add_argument("--diff", type=str, default="easy", choices=["easy", "hard"],
                            help="AI Difficulty (easy, hard)")
        args = parser.parse_args()

        colors = {"blue": (0, 50, 100), "black": (20, 20, 20), "gray": (50, 50, 50)}
        self.bg_color = colors[args.bg]
        self.difficulty = args.diff
        self.cell_size = 40
        self.grid_size = 10
        self.fps = 30

class BattleshipGame:
    def __init__(self, config):
        pygame.init()
        pygame.font.init()
        self.config = config

        width = self.config.cell_size * 23
        height = self.config.cell_size * 13
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"Battleship - Diff: {self.config.difficulty}")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)

        self.player_board = Board(self.config.grid_size)
        self.ai_board = Board(self.config.grid_size)
        self.ai_board.place_random_ships()

        # Стан гри: "placement" (розстановка), "playing" (гра), "game_over" (кінець)
        self.state = "placement"
        self.ships_to_place = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.current_orientation = "H"

        self.running = True
        self.turn = "player"
        self.winner_text = ""