import arcade
import random
import math
from croco_game import resource_path

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "SNAKE BATTLE"
CELL_SIZE = 20
BASE_SPEED = 0.15
MIN_SPEED = 0.04

STATE_COUNTDOWN = 0
STATE_GAME = 1


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.alpha = 255
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 5

    def draw(self, off_x, off_y):
        if self.alpha > 0:
            color = (self.color[0], self.color[1], self.color[2], self.alpha)
            arcade.draw_rect_filled(arcade.rect.XYWH(self.x + off_x, self.y + off_y, 4, 4), color)


class Snake:
    def __init__(self, x, y, color):
        self.color = color
        self.segments = [[x, y], [x - CELL_SIZE, y]]
        self.change_x = CELL_SIZE
        self.change_y = 0

    def draw(self, off_x, off_y):
        for seg in self.segments:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(seg[0] + CELL_SIZE / 2 + off_x, seg[1] + CELL_SIZE / 2 + off_y,
                                 CELL_SIZE - 2, CELL_SIZE - 2),
                self.color
            )


class SnakeBattle(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title=SCREEN_TITLE)
        #self.state = STATE_MENU
        self.player1 = None
        self.player2 = None
        self.apple = None
        self.timer = 0
        self.flash_timer = 0
        self.game_over = False
        self.menu_bg = self.is_music = self.over_sound = None
        self.current_speed = BASE_SPEED
        self.score1 = 0
        self.score2 = 0
        self.particles = []

        self.state = STATE_COUNTDOWN
        self.countdown_value = 3.0
        self.last_tick_sec = 3

        self.title_text = arcade.Text("SNAKE BATTLE", 0, 0, arcade.color.NEON_GREEN, 50, anchor_x="center", bold=True)
        self.hint_text = arcade.Text("P1: Arrows | P2: WASD\n\nPRESS ENTER TO START\n\nESC TO EXIT",
                                     0, 0, arcade.color.WHITE, 16, anchor_x="center", multiline=True, width=500)
        self.over_text = arcade.Text("", self.width / 2 , self.height / 2, arcade.color.GOLD, 35, anchor_x="center", bold=True)
        self.countdown_text = arcade.Text("", self.width / 2 , self.height / 2, arcade.color.NEON_GREEN, 50, anchor_x="center", bold=True)

        self.setup()

    def setup(self):

        #self.ctx.projection_2d = 0, SCREEN_WIDTH, 0, SCREEN_HEIGHT

        try:
            self.eat_sound = arcade.load_sound(resource_path("Assets/sound/snake_sounds/eat.wav"))
            self.music_bg = arcade.load_sound(resource_path("Assets/sound/snake_sounds/snake_music.mp3"))
            self.menu_bg = arcade.load_texture(resource_path("Assets/images/snakes_menu_bg.png"))
            if not self.over_sound:
                self.over_sound = arcade.load_sound(resource_path("Assets/sound/snake_sounds/over_sound.mp3"))
        except:
            pass
        self.player1 = Snake(100, 300, arcade.color.ELECTRIC_CRIMSON)
        self.player2 = Snake(500, 300, arcade.color.CYAN)
        self.player2.change_x = -CELL_SIZE
        self.current_speed = BASE_SPEED
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.particles = []
        self.state = STATE_COUNTDOWN
        self.countdown_value = 3.0
        self.last_tick_sec = 3
        self.start_background_music()
        self.apples = []
        for _ in range(2):
            self.spawn_apple()


    def create_explosion(self, x, y, color):
        for _ in range(25):
            self.particles.append(Particle(x + CELL_SIZE / 2, y + CELL_SIZE / 2, color))

    def spawn_apple(self):
        new_apple = [random.randrange(0, SCREEN_WIDTH, CELL_SIZE),
                     random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)]
        self.apples.append(new_apple)

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH + 1, CELL_SIZE):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_BLUE_GRAY, 1)
        for y in range(0, SCREEN_HEIGHT + 1, CELL_SIZE):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.DARK_BLUE_GRAY, 1)

    def on_draw(self):
        self.clear()

        off_x = (self.width - SCREEN_WIDTH) // 2
        off_y = (self.height - SCREEN_HEIGHT) // 2

        arcade.draw_rect_outline(arcade.rect.XYWH(self.width / 2, self.height / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
                                 arcade.color.DARK_BLUE_GRAY, 2)

        #if self.state == STATE_MENU:
        #    if self.menu_bg:
        #        arcade.draw_texture_rect(self.menu_bg, arcade.rect.XYWH(off_x * 2, off_y * 2, 600, 600))
        #        arcade.draw_rect_filled(arcade.rect.XYWH(off_x * 2, off_y * 2, 600, 600), (0, 0, 0, 150))

        #    self.title_text.draw()
        #    self.hint_text.draw()

        #elif self.state == STATE_GAME:
        for x in range(0, SCREEN_WIDTH + 1, CELL_SIZE):
            arcade.draw_line(x + off_x, off_y, x + off_x, SCREEN_HEIGHT + off_y, arcade.color.DARK_BLUE_GRAY, 1)
        for y in range(0, SCREEN_HEIGHT + 1, CELL_SIZE):
            arcade.draw_line(off_x, y + off_y, SCREEN_WIDTH + off_x, y + off_y, arcade.color.DARK_BLUE_GRAY, 1)

        speed_val = int((BASE_SPEED / self.current_speed) * 100)
        arcade.draw_text(f"SPEED: {speed_val}%", 10, self.height + 60 - off_y, arcade.color.LIGHT_GRAY,
                         22, bold=True)
        arcade.draw_text(f"RED PLAYER: {self.score1}", 10, self.height + 30 - off_y, arcade.color.ELECTRIC_CRIMSON, 22,
                         bold=True)
        arcade.draw_text(f"BLUE PLAYER: {self.score2}", 10, self.height - off_y, arcade.color.CYAN, 22,
                         bold=True)

        for p in self.particles:
            p.draw(off_x, off_y)

        if self.state == STATE_COUNTDOWN:
            self.countdown_text.text = str(int(self.countdown_value) + 1)
            self.countdown_text.draw()
        elif self.game_over:
            self.over_text.x, self.over_text.y = self.width / 2, self.height / 2
            self.over_text.draw()
        else:
            alpha = int(160 + 95 * math.sin(self.flash_timer * 12))
            c = arcade.color.NEON_GREEN
            apple_color = (c[0], c[1], c[2], alpha)
            for apple in self.apples:
                arcade.draw_rect_filled(arcade.rect.XYWH(apple[0] + CELL_SIZE / 2 + off_x, apple[1] + CELL_SIZE / 2 + off_y,
                                                        CELL_SIZE - 2, CELL_SIZE - 2), apple_color)
            self.player1.draw(off_x, off_y)
            self.player2.draw(off_x, off_y)


    def on_resize(self, width, height):
        super().on_resize(width, height)
        #self.ctx.projection_2d = 0, width, 0, height

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()

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
        if (key == arcade.key.W or key == 119) and self.player2.change_y == 0:
            self.player2.change_x, self.player2.change_y = 0, CELL_SIZE
        elif (key == arcade.key.S or char in 'sы') and self.player2.change_y == 0:
            self.player2.change_x, self.player2.change_y = 0, -CELL_SIZE
        elif (key == arcade.key.A or char in 'aф') and self.player2.change_x == 0:
            self.player2.change_x, self.player2.change_y = -CELL_SIZE, 0
        elif (key == arcade.key.D or char in 'dв') and self.player2.change_x == 0:
            self.player2.change_x, self.player2.change_y = CELL_SIZE, 0


    def start_background_music(self):
        if self.is_music:
            arcade.stop_sound(self.is_music)
        self.background_music = arcade.load_sound(resource_path("Assets/sound/snake_sounds/snake_music.mp3"))
        self.is_music = arcade.play_sound(self.background_music, loop=True)

    def on_update(self, delta_time):
        self.flash_timer += delta_time
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0: self.particles.remove(p)

        if self.state == STATE_COUNTDOWN:
            self.countdown_value -= delta_time

            if self.countdown_value <= 0:
                self.state = STATE_GAME
            return

        if self.game_over: return

        self.timer += delta_time
        if self.timer < self.current_speed: return
        self.timer = 0

        self.current_speed = max(MIN_SPEED, BASE_SPEED - ((self.score1 + self.score2) * 0.005))
        for i, p in enumerate([self.player1, self.player2]):
            head = p.segments[-1]
            new_head = [int(head[0] + p.change_x), int(head[1] + p.change_y)]
            p.segments.append(new_head)
            ate = False
            for apple in self.apples[:]:
                if new_head == apple:
                    if i == 0:
                        self.score1 += 1
                    else:
                        self.score2 += 1
                    if self.eat_sound: arcade.play_sound(self.eat_sound)
                    self.apples.remove(apple)
                    self.spawn_apple()
                    ate = True
                    break
            if not ate: p.segments.pop(0)

        h1, h2 = self.player1.segments[-1], self.player2.segments[-1]
        b1, b2 = self.player1.segments[:-1], self.player2.segments[:-1]

        if h1[0] < 0 or h1[0] >= SCREEN_WIDTH or h1[1] < 0 or h1[1] >= SCREEN_HEIGHT or \
                h2[0] < 0 or h2[0] >= SCREEN_WIDTH or h2[1] < 0 or h2[1] >= SCREEN_HEIGHT or \
                h1 == h2 or h1 in b1 or h1 in b2 or h2 in b1 or h2 in b2:
            self.game_over = True
            if self.over_sound: arcade.play_sound(self.over_sound)
            for h, c in [(h1, self.player1.color), (h2, self.player2.color)]:
                for _ in range(25): self.particles.append(Particle(h[0] + CELL_SIZE / 2, h[1] + CELL_SIZE / 2, c))
            if self.score1 > self.score2:
                self.over_text.text = "COLLISION! RED PLAYER WINS!"
            elif self.score2 > self.score1:
                self.over_text.text = "COLLISION! BLUE PLAYER WINS!"
            else:
                self.over_text.text = "COLLISION! IT'S A DRAW!"



if __name__ == "__main__":
    game = SnakeBattle()
    game.setup()
    arcade.run()
