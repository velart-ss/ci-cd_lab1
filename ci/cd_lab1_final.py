import pygame
import argparse
import random
import sys


# --- НАЛАШТУВАННЯ (Config) ---
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


# --- ЛОГІКА (Logic) ---
class Board:
    def __init__(self, size=10):
        self.size = size
        # 0 - пусто, 1 - корабель, 2 - промах, 3 - влучання, 4 - знищено
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.ships_alive = 0

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
        return True

    def receive_shot(self, x, y):
        if self.grid[y][x] == 1:
            self.grid[y][x] = 3  # Влучання
            self.ships_alive -= 1
            self.mark_if_sunk(x, y)  # Перевіряємо, чи корабель знищено
            return True
        elif self.grid[y][x] == 0:
            self.grid[y][x] = 2  # Промах
        return False

    def mark_if_sunk(self, x, y):
        cells = []
        visited = set()

        def dfs(cx, cy):
            if (cx, cy) in visited: return
            if not (0 <= cx < self.size and 0 <= cy < self.size): return
            if self.grid[cy][cx] not in [1, 3]: return
            visited.add((cx, cy))
            cells.append((cx, cy))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(cx + dx, cy + dy)

        dfs(x, y)

        if all(self.grid[cy][cx] == 3 for cx, cy in cells):
            for cx, cy in cells:
                self.grid[cy][cx] = 4  # 4 - статус "Знищено"


# --- ІНТЕРФЕЙС (UI) ---
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
                    color = (100, 100, 100)  # Корабель
                elif val == 2:
                    color = (255, 255, 255)  # Промах
                elif val == 3:
                    color = (220, 20, 60)  # Поранення
                elif val == 4:
                    color = (255, 140, 0)  # Знищений

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
            color = (150, 255, 150) if is_valid else (255, 150, 150)

            for i in range(length):
                px = grid_x + i if self.current_orientation == "H" else grid_x
                py = grid_y if self.current_orientation == "H" else grid_y + i
                if 0 <= px < 10 and 0 <= py < 10:
                    rect = pygame.Rect(start_x + px * self.config.cell_size,
                                       start_y + py * self.config.cell_size,
                                       self.config.cell_size, self.config.cell_size)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def ai_move(self):
        x, y = random.randint(0, 9), random.randint(0, 9)
        while self.player_board.grid[y][x] in [2, 3, 4]:
            x, y = random.randint(0, 9), random.randint(0, 9)
        self.player_board.receive_shot(x, y)
        self.turn = "player"

    def run(self):
        while self.running:
            self.screen.fill(self.config.bg_color)

            player_x, player_y = self.config.cell_size, self.config.cell_size * 2
            ai_x, ai_y = self.config.cell_size * 12, self.config.cell_size * 2

            self.draw_board(self.player_board, player_x, player_y)

            if self.state == "placement":
                text = self.font.render(f"Розставте корабель на {self.ships_to_place[0]} палуби", True, (255, 255, 255))
                self.screen.blit(text, (player_x, 10))
                sub_text = self.font.render("ЛКМ - Поставити | ПКМ - Повернути", True, (200, 200, 200))
                self.screen.blit(sub_text, (player_x, player_y + 10 * self.config.cell_size + 10))
                self.draw_placement_preview(player_x, player_y)

            elif self.state == "playing" or self.state == "game_over":
                self.draw_board(self.ai_board, ai_x, ai_y, hide_ships=(self.state != "game_over"))

                player_lbl = self.font.render("Ваше поле", True, (255, 255, 255))
                ai_lbl = self.font.render("Поле противника", True, (255, 255, 255))
                self.screen.blit(player_lbl, (player_x, 10))
                self.screen.blit(ai_lbl, (ai_x, 10))

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
                        if event.button == 3:
                            self.current_orientation = "V" if self.current_orientation == "H" else "H"
                        elif event.button == 1:
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

            if self.turn == "ai" and self.state == "playing":
                pygame.time.delay(400)
                self.ai_move()

            if self.state == "playing":
                if self.player_board.ships_alive == 0:
                    self.winner_text = "Комп'ютер переміг!"
                    self.state = "game_over"
                elif self.ai_board.ships_alive == 0:
                    self.winner_text = "Ви Перемогли!"
                    self.state = "game_over"

            pygame.display.flip()
            self.clock.tick(self.config.fps)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    config = Config()
    game = BattleshipGame(config)
    game.run()