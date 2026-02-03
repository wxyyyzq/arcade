import os
import sys
import random
import arcade
import math
from arcade.gui import UIManager, UITextureButton, UIAnchorLayout, UIBoxLayout


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(os.path.dirname(base_path), "Assets")
        if os.path.exists(assets_path):
            test_path = os.path.join(os.path.dirname(base_path), relative_path)
            if os.path.exists(test_path):
                return test_path
            test_path = os.path.join(base_path, relative_path)
            if os.path.exists(test_path):
                return test_path

    full_path = os.path.join(base_path, relative_path)
    return full_path


CROCO_SCALE = 0.9
TEETH_SCALE = 0.9
NUM_TEETH = 9


class SimpleConfettiParticle:
    def __init__(self, x, y, color, player_index):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 12)
        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(4, 12)
        self.gravity = 0.3
        self.life = 1.0
        self.decay = random.uniform(0.005, 0.015)
        self.player_index = player_index

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y -= self.gravity
        self.life -= self.decay
        self.speed_x *= 0.995
        return self.life > 0

    def draw(self):
        alpha = int(self.life * 255)
        arcade.draw_circle_filled(self.x, self.y, self.size,
                                  (self.color[0], self.color[1], self.color[2], alpha))


class CrocodileClosed(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.scale = CROCO_SCALE
        self.texture = arcade.load_texture(resource_path("Assets/images/croco_close.png"))
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2


class CrocodileOpen(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.scale = CROCO_SCALE
        self.texture = arcade.load_texture(resource_path("Assets/images/croco_open.png"))
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2


class Tooth(arcade.Sprite):
    def __init__(self, x, y, is_bad=False):
        super().__init__()
        self.scale = TEETH_SCALE
        self.texture = arcade.load_texture(resource_path("Assets/images/teeth.png"))
        self.center_x = x
        self.center_y = y
        self.is_pressed = False
        self.is_bad = is_bad
        self.pressed_by = None


class ToothPressed(arcade.Sprite):
    def __init__(self, x, y, player_index):
        super().__init__()
        self.scale = TEETH_SCALE
        self.texture = arcade.load_texture(resource_path("Assets/images/teeth_pressed.png"))
        self.center_x = x
        self.center_y = y
        self.is_pressed = True
        self.pressed_by = player_index


class BlueAngle(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.scale = 1
        self.texture = arcade.load_texture(resource_path("Assets/images/blue_angle.png"))
        self.center_x = screen_width - 70
        self.center_y = screen_height - 70


class RedAngle(arcade.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.scale = 1
        self.texture = arcade.load_texture(resource_path("Assets/images/red_angle.png"))
        self.center_x = 70
        self.center_y = 70


class CrocoGame(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title="Крокодил: Два игрока")
        arcade.set_background_color(arcade.color.LIGHT_PINK)

        self.manager = None
        self.anchor_layout = None
        self.box_layout = None
        self.again_button = None
        self.background_music = None
        self.background_music_player = None

        self.setup_ui()

        self.click_sound = arcade.load_sound(resource_path("Assets/sound/button-dry-clear-close-bright.wav"))
        self.game_over_sound = arcade.load_sound(":resources:sounds/gameover2.wav")
        self.confetti_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")

        self.highlight_pulse = 0
        self.pulse_speed = 0.05
        self.pulse_direction = 1

        self.setup()

    def setup_ui(self):
        self.manager = UIManager()
        self.manager.enable()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=False, space_between=30)
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        menu_button = UITextureButton(
            texture=arcade.load_texture(resource_path("Assets/images/menu_icon.png")),
            scale=0.2
        )

        def on_menu_click(event):
            if self.background_music_player:
                arcade.stop_sound(self.background_music_player)
            self.manager.disable()
            self.close()
            import interface
            menu_window = interface.MyGame()
            arcade.run()

        menu_button.on_click = on_menu_click
        self.box_layout.add(menu_button)

        self.again_button = UITextureButton(
            texture=arcade.load_texture(resource_path("Assets/images/vor.png")),
            scale=0.8
        )
        self.again_button.on_click = self.restart_game
        self.box_layout.add(self.again_button)

    def setup(self):
        screen_width, screen_height = self.get_size()

        self.croco_closed = CrocodileClosed(screen_width, screen_height)
        self.croco_open = CrocodileOpen(screen_width, screen_height)
        self.blue_angle = BlueAngle(screen_width, screen_height)
        self.red_angle = RedAngle(screen_width, screen_height)

        self.crocodile_list = arcade.SpriteList()
        self.teeth_list = arcade.SpriteList()
        self.angles = arcade.SpriteList()

        self.crocodile_list.append(self.croco_open)
        self.angles.append(self.blue_angle)
        self.angles.append(self.red_angle)

        self.confetti_particles = []
        self.confetti_active = False
        self.confetti_spawn_timer = 0
        self.game_over = False

        self.current_player = random.randint(0, 1)

        self.scores = [0, 0]
        self.pressed_teeth_count = 0
        self.winner_index = None

        self.bad_tooth_index = random.randint(0, NUM_TEETH - 1)
        self.add_teeth(screen_width, screen_height)

        self.start_background_music()

    def start_background_music(self):
        if self.background_music_player:
            arcade.stop_sound(self.background_music_player)

        self.background_music = arcade.load_sound(resource_path("Assets/sound/background_crocodile.mp3"))
        self.background_music_player = arcade.play_sound(self.background_music, loop=True)

    def restart_game(self, event=None):
        self.setup()

    def add_teeth(self, screen_width, screen_height):
        teeth_coordinates = [
            (screen_width // 2 - 160, screen_height - 330),
            (screen_width // 2 - 175, screen_height - 400),
            (screen_width // 2 - 165, screen_height - 465),
            (screen_width // 2 - 80, screen_height - 490),
            (screen_width // 2, screen_height - 500),
            (screen_width // 2 + 80, screen_height - 490),
            (screen_width // 2 + 165, screen_height - 465),
            (screen_width // 2 + 175, screen_height - 400),
            (screen_width // 2 + 160, screen_height - 330)
        ]

        for i, (x, y) in enumerate(teeth_coordinates):
            is_bad_tooth = (i == self.bad_tooth_index)
            self.teeth_list.append(Tooth(x, y, is_bad=is_bad_tooth))

    def draw_current_player_highlight(self):
        if self.game_over:
            return

        self.highlight_pulse += self.pulse_speed * self.pulse_direction
        if self.highlight_pulse >= 1.0:
            self.highlight_pulse = 1.0
            self.pulse_direction = -1
        elif self.highlight_pulse <= 0.3:
            self.highlight_pulse = 0.3
            self.pulse_direction = 1

        if self.current_player == 0:
            center_x, center_y = self.red_angle.center_x, self.red_angle.center_y
            base_color = (255, 50, 50)
            glow_color = (255, 100, 100, int(150 * self.highlight_pulse))
        else:
            center_x, center_y = self.blue_angle.center_x, self.blue_angle.center_y
            base_color = (50, 50, 255)
            glow_color = (100, 100, 255, int(150 * self.highlight_pulse))

        glow_radius = 60 + 15 * self.highlight_pulse

        for i in range(3):
            radius = glow_radius + i * 10
            alpha = int(80 * (1 - i / 3) * self.highlight_pulse)
            arcade.draw_circle_filled(center_x, center_y, radius, (*glow_color[:3], alpha))

        arcade.draw_circle_filled(center_x, center_y, glow_radius - 20, (*base_color, int(100 * self.highlight_pulse)))

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.LIGHT_PINK)

        self.crocodile_list.draw()

        if not self.game_over:
            self.draw_current_player_highlight()

        self.angles.draw()
        self.teeth_list.draw()

        for particle in self.confetti_particles:
            particle.draw()

        if self.game_over:
            self.manager.draw()

    def create_confetti_explosion(self, player_index):
        self.confetti_active = True
        arcade.play_sound(self.confetti_sound, volume=1.0)

        colors = [
            [(255, 0, 0), (178, 34, 34), (220, 20, 60), (255, 69, 0),
             (255, 140, 0), (255, 99, 71), (255, 20, 147), (255, 215, 0)],
            [(0, 0, 255), (0, 0, 139), (65, 105, 225), (70, 130, 180),
             (100, 149, 237), (30, 144, 255), (138, 43, 226), (0, 255, 255)]
        ][player_index]

        for _ in range(5):
            spawn_x = random.randint(100, self.width - 100)
            spawn_y = random.randint(100, self.height - 100)
            for _ in range(80):
                self.confetti_particles.append(SimpleConfettiParticle(
                    spawn_x, spawn_y, random.choice(colors), player_index
                ))

    def update_confetti(self, delta_time):
        if not self.confetti_active:
            return

        self.confetti_particles = [p for p in self.confetti_particles if p.update()]
        self.confetti_spawn_timer += delta_time

        if self.confetti_spawn_timer > 0.3 and self.winner_index is not None:
            self.confetti_spawn_timer = 0
            colors = [
                [(255, 0, 0), (255, 69, 0), (255, 140, 0), (255, 215, 0)],
                [(0, 0, 255), (65, 105, 225), (30, 144, 255), (0, 255, 255)]
            ][self.winner_index]

            for _ in range(3):
                spawn_x = random.randint(0, self.width)
                spawn_y = self.height
                for _ in range(2):
                    self.confetti_particles.append(SimpleConfettiParticle(
                        spawn_x, spawn_y, random.choice(colors), self.winner_index
                    ))

    def on_update(self, delta_time):
        if self.game_over and self.confetti_active:
            self.update_confetti(delta_time)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.game_over:
            self.manager.on_mouse_press(x, y, button, modifiers)
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            clicked_sprites = arcade.get_sprites_at_point((x, y), self.teeth_list)

            for tooth in clicked_sprites:
                if hasattr(tooth, 'is_pressed') and tooth.is_pressed:
                    continue

                tooth_x, tooth_y = tooth.center_x, tooth.center_y
                is_bad = tooth.is_bad

                tooth.remove_from_sprite_lists()

                if is_bad:
                    self.game_over = True
                    arcade.play_sound(self.game_over_sound)
                    self.winner_index = 1 - self.current_player
                    self.scores[self.winner_index] += 1
                    self.create_confetti_explosion(self.winner_index)

                    self.teeth_list.append(ToothPressed(tooth_x, tooth_y, self.current_player))
                    self.pressed_teeth_count += 1

                    self.croco_open.remove_from_sprite_lists()
                    self.teeth_list.clear()
                    self.crocodile_list.append(self.croco_closed)
                else:
                    self.scores[self.current_player] += 1
                    arcade.play_sound(self.click_sound)

                    self.teeth_list.append(ToothPressed(tooth_x, tooth_y, self.current_player))
                    self.pressed_teeth_count += 1
                    self.current_player = 1 - self.current_player

                    if self.pressed_teeth_count >= NUM_TEETH:
                        self.game_over = True
                        arcade.play_sound(self.game_over_sound)
                        self.winner_index = 0 if self.scores[0] >= self.scores[1] else 1
                        self.create_confetti_explosion(self.winner_index)


def main():
    game = CrocoGame()
    arcade.run()


if __name__ == "__main__":
    main()
