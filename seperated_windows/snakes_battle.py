import arcade
import random
import math
from croco_game import resource_path

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "SNAKE BATTLE"
CELL_SIZE = 20
UPDATE_SPEED = 0.12

STATE_MENU = 0
STATE_GAME = 1


class Snake:
    def __init__(self, x, y, color):
        self.color = color
        self.segments = [[x, y], [x - CELL_SIZE, y]]
        self.change_x = CELL_SIZE
        self.change_y = 0

    def draw(self):
        for seg in self.segments:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(seg[0] + CELL_SIZE / 2, seg[1] + CELL_SIZE / 2,
                                 CELL_SIZE - 2, CELL_SIZE - 2),
                self.color
            )


class SnakeBattle(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.state = STATE_MENU
        self.player1 = None
        self.player2 = None
        self.apple = None
        self.timer = 0
        self.flash_timer = 0
        self.game_over = False
        self.menu_bg = None

        self.title_text = arcade.Text("SNAKE BATTLE", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
                                      arcade.color.NEON_GREEN, 50, anchor_x="center", bold=True)
        self.hint_text = arcade.Text("P1: Arrows | P2: WASD\n\nPRESS ENTER TO START\n\nPRESS ESC TO EXIT",
                                     SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                                     arcade.color.WHITE, 16, anchor_x="center", multiline=True, width=500)
        self.over_text = arcade.Text("COLLISION!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                     arcade.color.GOLD, 35, anchor_x="center", bold=True)

    def setup(self):
        try:
            self.menu_bg = arcade.load_texture(resource_path("Assets/images/snakes_menu_bg.png"))
        except:
            pass
        self.player1 = Snake(100, 300, arcade.color.ELECTRIC_CRIMSON)
        self.player2 = Snake(500, 300, arcade.color.CYAN)
        self.player2.change_x = -CELL_SIZE
        self.spawn_apple()
        self.game_over = False

    def spawn_apple(self):
        self.apple = [random.randrange(0, SCREEN_WIDTH, CELL_SIZE),
                      random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)]

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH + 1, CELL_SIZE):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_BLUE_GRAY, 1)
        for y in range(0, SCREEN_HEIGHT + 1, CELL_SIZE):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.DARK_BLUE_GRAY, 1)

    def on_draw(self):
        self.clear()

        if self.state == STATE_MENU:
            if self.menu_bg:
                arcade.draw_texture_rect(self.menu_bg, arcade.rect.XYWH(300, 300, 600, 600))
                arcade.draw_rect_filled(arcade.rect.XYWH(300, 300, 600, 600), (0, 0, 0, 150))

            self.title_text.draw()
            self.hint_text.draw()

        elif self.state == STATE_GAME:
            self.draw_grid()

            if self.game_over:
                self.over_text.draw()
                arcade.draw_text("PRESS SPACE TO RESTART", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
                                 arcade.color.WHITE, 14, anchor_x="center")
                return

            alpha = int(160 + 95 * math.sin(self.flash_timer * 12))
            apple_color = (arcade.color.NEON_GREEN[0], arcade.color.NEON_GREEN[1],
                           arcade.color.NEON_GREEN[2], alpha)

            arcade.draw_rect_filled(
                arcade.rect.XYWH(self.apple[0] + CELL_SIZE / 2, self.apple[1] + CELL_SIZE / 2,
                                 CELL_SIZE - 2, CELL_SIZE - 2), apple_color
            )

            self.player1.draw()
            self.player2.draw()

    def on_key_press(self, key, modifiers):
        if self.state == STATE_MENU and key == arcade.key.ENTER:
            self.setup()
            self.state = STATE_GAME
            return

        if self.game_over and key == arcade.key.SPACE:
            self.setup()
            return

        if key == arcade.key.UP and self.player1.change_y == 0:
            self.player1.change_x, self.player1.change_y = 0, CELL_SIZE
        elif key == arcade.key.DOWN and self.player1.change_y == 0:
            self.player1.change_x, self.player1.change_y = 0, -CELL_SIZE
        elif key == arcade.key.LEFT and self.player1.change_x == 0:
            self.player1.change_x, self.player1.change_y = -CELL_SIZE, 0
        elif key == arcade.key.RIGHT and self.player1.change_x == 0:
            self.player1.change_x, self.player1.change_y = CELL_SIZE, 0

        try:
            char = chr(key).lower()
        except:
            char = ''
        if (key == arcade.key.W or char in 'wц') and self.player2.change_y == 0:
            self.player2.change_x, self.player2.change_y = 0, CELL_SIZE
        elif (key == arcade.key.S or char in 'sы') and self.player2.change_y == 0:
            self.player2.change_x, self.player2.change_y = 0, -CELL_SIZE
        elif (key == arcade.key.A or char in 'aф') and self.player2.change_x == 0:
            self.player2.change_x, self.player2.change_y = -CELL_SIZE, 0
        elif (key == arcade.key.D or char in 'dв') and self.player2.change_x == 0:
            self.player2.change_x, self.player2.change_y = CELL_SIZE, 0

    def on_update(self, delta_time):
        self.flash_timer += delta_time
        if self.state != STATE_GAME or self.game_over: return

        self.timer += delta_time
        if self.timer < UPDATE_SPEED: return
        self.timer = 0

        for p in [self.player1, self.player2]:
            new_head = [int(p.segments[-1][0] + p.change_x), int(p.segments[-1][1] + p.change_y)]
            p.segments.append(new_head)
            if new_head == self.apple:
                self.spawn_apple()
            else:
                p.segments.pop(0)

        h1, h2 = self.player1.segments[-1], self.player2.segments[-1]
        bodies = self.player1.segments[:-1] + self.player2.segments[:-1]

        if (h1[0] < 0 or h1[0] >= SCREEN_WIDTH or h1[1] < 0 or h1[1] >= SCREEN_HEIGHT or
                h2[0] < 0 or h2[0] >= SCREEN_WIDTH or h2[1] < 0 or h2[1] >= SCREEN_HEIGHT or
                h1 == h2 or h1 in bodies or h2 in bodies):
            self.game_over = True


if __name__ == "__main__":
    game = SnakeBattle()
    game.setup()
    arcade.run()
