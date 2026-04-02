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

            # Логіка для різних станів гри
            if self.state == "placement":
                # Малюємо підказки для розстановки
                text = self.font.render(f"Розставте корабель на {self.ships_to_place[0]} палуби", True, (255, 255, 255))
                self.screen.blit(text, (player_x, 10))
                sub_text = self.font.render("ЛКМ - Поставити | ПКМ - Повернути", True, (200, 200, 200))
                self.screen.blit(sub_text, (player_x, player_y + 10 * self.config.cell_size + 10))

                self.draw_placement_preview(player_x, player_y)

            elif self.state == "playing" or self.state == "game_over":
                # Малюємо поле суперника
                self.draw_board(self.ai_board, ai_x, ai_y, hide_ships=(self.state != "game_over"))

                player_lbl = self.font.render("Ваше поле", True, (255, 255, 255))
                ai_lbl = self.font.render("Поле противника", True, (255, 255, 255))
                self.screen.blit(player_lbl, (player_x, 10))
                self.screen.blit(ai_lbl, (ai_x, 10))

            # Виведення екрана перемоги
            if self.state == "game_over":
                overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                win_color = (0, 255, 0) if "Ви" in self.winner_text else (255, 0, 0)
                text_surf = self.large_font.render(self.winner_text, True, win_color)
                text_rect = text_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(text_surf, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "placement":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 3:  # Правий клік - поворот
                            self.current_orientation = "V" if self.current_orientation == "H" else "H"
                        elif event.button == 1:  # Лівий клік - поставити
                            mx, my = pygame.mouse.get_pos()
                            if player_x <= mx < player_x + 10 * self.config.cell_size and \
                                    player_y <= my < player_y + 10 * self.config.cell_size:

                                grid_x = (mx - player_x) // self.config.cell_size
                                grid_y = (my - player_y) // self.config.cell_size
                                length = self.ships_to_place[0]

                                if self.player_board.place_ship(grid_x, grid_y, length, self.current_orientation):
                                    self.ships_to_place.pop(0)
                                    if not self.ships_to_place:
                                        self.state = "playing"

                elif self.state == "playing":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.turn == "player":
                        mx, my = pygame.mouse.get_pos()
                        if ai_x <= mx < ai_x + 10 * self.config.cell_size and \
                                ai_y <= my < ai_y + 10 * self.config.cell_size:

                            grid_x = (mx - ai_x) // self.config.cell_size
                            grid_y = (my - ai_y) // self.config.cell_size

                            if self.ai_board.grid[grid_y][grid_x] in [0, 1]:
                                self.ai_board.receive_shot(grid_x, grid_y)
                                self.turn = "ai"

            # Хід AI
            if self.turn == "ai" and self.state == "playing":
                pygame.time.delay(400)
                self.ai_move()

            # Перевірка перемоги
            if self.state == "playing":
                if self.player_board.ships_alive == 0:
                    self.winner_text = "AI Переміг!"
                    self.state = "game_over"
                elif self.ai_board.ships_alive == 0:
                    self.winner_text = "Ви Перемогли!"
                    self.state = "game_over"

            pygame.display.flip()
            self.clock.tick(self.config.fps)

        pygame.quit()
        sys.exit()

    def ai_move(self):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while self.player_board.grid[y][x] in [2, 3, 4]:
            x, y = random.randint(0, 9), random.randint(0, 9)
        self.player_board.receive_shot(x, y)
        self.turn = "player"