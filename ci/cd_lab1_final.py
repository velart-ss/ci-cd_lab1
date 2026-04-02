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

    def draw_board(self, board, offset_x, offset_y, hide_ships=False):
        for y in range(board.size):
            for x in range(board.size):
                rect = pygame.Rect(offset_x + x * self.config.cell_size,
                                   offset_y + y * self.config.cell_size,
                                   self.config.cell_size, self.config.cell_size)

                color = (200, 200, 200)  # Вода
                val = board.grid[y][x]

                if val == 1 and not hide_ships:
                    color = (100, 100, 100)  # Корабель (Сірий)
                elif val == 2:
                    color = (255, 255, 255)  # Промах (Білий)
                elif val == 3:
                    color = (220, 20, 60)  # Поранення (Червоний)
                elif val == 4:
                    color = (255, 140, 0)  # Знищений (Помаранчевий)

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_placement_preview(self, start_x, start_y):
        mx, my = pygame.mouse.get_pos()
        if start_x <= mx < start_x + 10 * self.config.cell_size and \
                start_y <= my < start_y + 10 * self.config.cell_size:

            grid_x = (mx - start_x) // self.config.cell_size
            grid_y = (my - start_y) // self.config.cell_size
            length = self.ships_to_place[0]

            is_valid = self.player_board._can_place(grid_x, grid_y, length, self.current_orientation)
            color = (150, 255, 150) if is_valid else (255, 150, 150)  # Зелений або рожевий

            for i in range(length):
                px = grid_x + i if self.current_orientation == "H" else grid_x
                py = grid_y if self.current_orientation == "H" else grid_y + i
                if 0 <= px < 10 and 0 <= py < 10:
                    rect = pygame.Rect(start_x + px * self.config.cell_size,
                                       start_y + py * self.config.cell_size,
                                       self.config.cell_size, self.config.cell_size)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def run(self):
        while self.running:
            self.screen.fill(self.config.bg_color)

            # Відмальовка полів та підписів
            player_x, player_y = self.config.cell_size, self.config.cell_size * 2
            ai_x, ai_y = self.config.cell_size * 12, self.config.cell_size * 2

            self.draw_board(self.player_board, player_x, player_y)