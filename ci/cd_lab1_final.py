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

class Board:
    def __init__(self, size=10):
        self.size = size
        # 0 - пусто, 1 - корабель, 2 - промах, 3 - влучання, 4 - знищено
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.ships_alive = 0

    def _can_place(self, x, y, length, orientation):
        if orientation == "H" and x + length > self.size: return False
        if orientation == "V" and y + length > self.size: return False

        for i in range(length):
            cx = x + i if orientation == "H" else x
            cy = y if orientation == "H" else y + i

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < self.size and 0 <= nx < self.size:
                        if self.grid[ny][nx] != 0:
                            return False

    def place_random_ships(self):
        ship_lengths = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for length in ship_lengths:
            placed = False
            while not placed:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                orientation = random.choice(["H", "V"])
                if self.place_ship(x, y, length, orientation):
                    placed = True

    def place_ship(self, x, y, length, orientation):
        if self._can_place(x, y, length, orientation):
            for i in range(length):
                if orientation == "H":
                    self.grid[y][x + i] = 1
                else:
                    self.grid[y + i][x] = 1
            self.ships_alive += length
            return True
        return False