import os
import sys
import arcade
import math
import random
from arcade.gui import UIManager, UITextureButton, UIAnchorLayout, UIBoxLayout
from croco_game import resource_path


CARS_SCALE = 0.3
CAR_SPEED = 4
CAR_REVERSE_SPEED = 2
ROTATION_SPEED = 3
WINNING_LAPS = 3

MAP1_CUSTOM_CHECKPOINTS = [(744, 350, 356, 8), (168, 362, 366, 8)]
MAP2_CUSTOM_CHECKPOINTS = [(836, 76, 8, 157), (588, 297, 208, 8), (74, 362, 251, 8)]

MAP_CONFIGS = {
    "map1": {"red_car_x": 290, "blue_car_x": 410, "both_car_y": 342, "custom_checkpoints": MAP1_CUSTOM_CHECKPOINTS},
    "map2": {"red_car_x": 150, "blue_car_x": 240, "both_car_y": 342, "custom_checkpoints": MAP2_CUSTOM_CHECKPOINTS}
}


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


class Checkpoint:
    def __init__(self, x, y, width, height, checkpoint_id, is_finish_line=False):
        self.center_x = x + width / 2
        self.center_y = y + height / 2
        self.width = width
        self.height = height
        self.checkpoint_id = checkpoint_id
        self.is_finish_line = is_finish_line
        self.color = arcade.color.RED if is_finish_line else arcade.color.YELLOW

    def contains_point(self, point_x, point_y):
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        return left <= point_x <= right and bottom <= point_y <= top


class RedCar(arcade.Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__()
        self.texture = arcade.load_texture(resource_path("Assets/images/car_red_tires.png"))
        self.speed = CAR_SPEED
        self.reverse_speed = CAR_REVERSE_SPEED
        self.scale = CARS_SCALE
        self.center_x = spawn_x
        self.center_y = spawn_y
        self.steering_angle = 0
        self.can_move = False
        self.has_started = False
        self.laps = 0
        self.is_winner = False
        self.winner_timer = 3.0
        self.is_reversing = False
        self.current_checkpoint = 0
        self.checkpoints_passed = 0


class BlueCar(arcade.Sprite):
    def __init__(self, spawn_x, spawn_y):
        super().__init__()
        self.texture = arcade.load_texture(resource_path("Assets/images/car_cyan_tires.png"))
        self.speed = CAR_SPEED
        self.reverse_speed = CAR_REVERSE_SPEED
        self.scale = CARS_SCALE
        self.center_x = spawn_x
        self.center_y = spawn_y
        self.steering_angle = 0
        self.can_move = False
        self.has_started = False
        self.laps = 0
        self.is_winner = False
        self.winner_timer = 3.0
        self.is_reversing = False
        self.current_checkpoint = 0
        self.checkpoints_passed = 0


class Races(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True, title="Гонки")
        self.current_map = None
        self.countdown_timer = 3.0
        self.is_countdown_active = True
        self.countdown_text = "3"
        self.go_text_timer = 0.0
        self.show_go_text = False
        self.game_over = False
        self.winner = None

        self.start_sound = None
        self.drive_sound = None
        self.finish_sound = None
        self.win_sound = None
        self.confetti_sound = None
        self.drive_sound_player = None
        self.background_music_player = None
        self.load_sounds()

        self.checkpoints = []
        self.finish_line = None
        self.confetti_particles = []
        self.confetti_active = False
        self.confetti_spawn_timer = 0
        self.winner_index = None

        self.manager = None
        self.restart_button = None
        self.menu_button = None
        self.setup_ui()
        self.setup()

    def setup_ui(self):
        self.manager = UIManager()
        self.manager.enable()
        anchor_layout = UIAnchorLayout()
        box_layout = UIBoxLayout(vertical=False, space_between=30)
        anchor_layout.add(box_layout)
        self.manager.add(anchor_layout)

        self.menu_button = UITextureButton(
            texture=arcade.load_texture(resource_path("Assets/images/menu_icon.png")),
            scale=0.2
        )

        def on_menu_click(event):
            self.stop_drive_sound()
            self.manager.disable()
            self.close()
            import interface
            menu_window = interface.MyGame()
            arcade.run()

        self.menu_button.on_click = on_menu_click
        box_layout.add(self.menu_button)

        self.restart_button = UITextureButton(
            texture=arcade.load_texture(resource_path("Assets/images/vor.png")),
            scale=0.8
        )
        self.restart_button.on_click = self.restart_game
        box_layout.add(self.restart_button)

        self.menu_button.visible = False
        self.restart_button.visible = False

    def restart_game(self, event=None):
        self.setup()

    def load_sounds(self):
        try:
            self.start_sound = arcade.load_sound(resource_path("Assets/sound/start_car.wav"))
        except:
            pass

        try:
            self.drive_sound = arcade.load_sound(resource_path("Assets/sound/drive_car.wav"))
        except:
            pass

        try:
            self.finish_sound = arcade.load_sound(resource_path("Assets/sound/finish.wav"))
        except:
            pass

        try:
            self.win_sound = arcade.load_sound(resource_path("Assets/sound/win.wav"))
        except:
            pass

        try:
            self.confetti_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")
        except:
            pass

    def play_win_sound(self):
        if self.win_sound:
            arcade.play_sound(self.win_sound)

    def play_finish_sound(self):
        if self.finish_sound:
            arcade.play_sound(self.finish_sound)

    def play_start_sound(self):
        if self.start_sound:
            arcade.play_sound(self.start_sound)

    def play_drive_sound(self):
        if self.drive_sound and not self.drive_sound_player:
            self.drive_sound_player = arcade.play_sound(self.drive_sound, loop=True)

    def stop_drive_sound(self):
        if self.drive_sound_player:
            self.drive_sound_player.pause()
            self.drive_sound_player = None

    def play_confetti_sound(self):
        if self.confetti_sound:
            arcade.play_sound(self.confetti_sound, volume=1.0)

    def create_checkpoints(self, offset_x, offset_y):
        self.checkpoints = []
        self.finish_line = None

        checkpoints_data = MAP1_CUSTOM_CHECKPOINTS if self.current_map == "map1" else MAP2_CUSTOM_CHECKPOINTS

        for i, (x, y, width, height) in enumerate(checkpoints_data):
            is_finish_line = (i == len(checkpoints_data) - 1)
            checkpoint = Checkpoint(x + offset_x, y + offset_y, width, height, i, is_finish_line)
            self.checkpoints.append(checkpoint)
            if is_finish_line:
                self.finish_line = checkpoint

    def check_checkpoints(self, car):
        if not car.can_move or self.game_over:
            return

        for checkpoint in self.checkpoints:
            if checkpoint.contains_point(car.center_x, car.center_y):
                if checkpoint.is_finish_line:
                    if car.checkpoints_passed >= len(self.checkpoints) - 1:
                        car.checkpoints_passed = 0
                        car.current_checkpoint = 0
                        car.laps += 1
                        self.play_finish_sound()

                        if car.laps >= WINNING_LAPS:
                            car.is_winner = True
                            self.game_over = True
                            self.winner_index = 0 if car == self.red_player else 1
                            self.play_win_sound()

                            self.create_confetti_explosion(self.winner_index)

                            self.menu_button.visible = True
                            self.restart_button.visible = True

                            self.red_player.can_move = False
                            self.blue_player.can_move = False
                            self.stop_drive_sound()

                elif checkpoint.checkpoint_id == car.current_checkpoint:
                    car.current_checkpoint += 1
                    car.checkpoints_passed += 1

                    if car.current_checkpoint >= len(self.checkpoints) - 1:
                        car.current_checkpoint = 0

    def create_confetti_explosion(self, player_index):
        self.confetti_active = True
        self.play_confetti_sound()

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

    def draw_lap_indicators(self):
        red_start_x, red_start_y = 120, 120
        blue_start_x, blue_start_y = self.width - 120, self.height - 120
        circle_radius, circle_spacing = 10, 25

        for i in range(WINNING_LAPS):
            red_x = red_start_x + i * circle_spacing
            blue_x = blue_start_x - i * circle_spacing

            if i < self.red_player.laps:
                arcade.draw_circle_filled(red_x, red_start_y, circle_radius, arcade.color.RED)
                arcade.draw_circle_outline(red_x, red_start_y, circle_radius, arcade.color.WHITE, 2)
            else:
                arcade.draw_circle_outline(red_x, red_start_y, circle_radius, arcade.color.WHITE, 2)

            if i < self.blue_player.laps:
                arcade.draw_circle_filled(blue_x, blue_start_y, circle_radius, arcade.color.CYAN)
                arcade.draw_circle_outline(blue_x, blue_start_y, circle_radius, arcade.color.WHITE, 2)
            else:
                arcade.draw_circle_outline(blue_x, blue_start_y, circle_radius, arcade.color.WHITE, 2)

    def setup(self):
        self.current_map = random.choice(["map1", "map2"])
        self.countdown_timer = 3.0
        self.is_countdown_active = True
        self.countdown_text = "3"
        self.go_text_timer = 0.0
        self.show_go_text = False
        self.game_over = False
        self.winner = None

        self.confetti_particles = []
        self.confetti_active = False
        self.confetti_spawn_timer = 0
        self.winner_index = None

        if hasattr(self, 'restart_button') and self.restart_button:
            self.restart_button.visible = False
        if hasattr(self, 'menu_button') and self.menu_button:
            self.menu_button.visible = False

        map_config = MAP_CONFIGS[self.current_map]
        map_path = resource_path(f"Assets/maps/{self.current_map}.tmx")

        tile_map = arcade.load_tilemap(map_path, scaling=1.0)
        map_width_pixels = tile_map.width * tile_map.tile_width
        map_height_pixels = tile_map.height * tile_map.tile_height

        scale_x = self.width / map_width_pixels
        scale_y = self.height / map_height_pixels
        final_scale = min(scale_x, scale_y)

        tile_map = arcade.load_tilemap(map_path, scaling=final_scale)

        self.ground_list = tile_map.sprite_lists["ground"]
        self.road_list = tile_map.sprite_lists["road"]
        self.fance_list = tile_map.sprite_lists["fance"]
        self.on_finish_list = tile_map.sprite_lists["on_finish"]
        self.finish_list = tile_map.sprite_lists["finish"]
        self.collision_list = tile_map.sprite_lists["collusion"]

        scaled_map_width = map_width_pixels * final_scale
        scaled_map_height = map_height_pixels * final_scale
        offset_x = (self.width - scaled_map_width) / 2
        offset_y = (self.height - scaled_map_height) / 2

        self.all_collision_list = arcade.SpriteList()
        for layer in [self.fance_list, self.collision_list]:
            for sprite in layer:
                self.all_collision_list.append(sprite)

        self.red_player = RedCar(map_config["red_car_x"] + offset_x, map_config["both_car_y"] + offset_y)
        self.blue_player = BlueCar(map_config["blue_car_x"] + offset_x, map_config["both_car_y"] + offset_y)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.red_player)
        self.player_list.append(self.blue_player)

        self.physics_engine_red = arcade.PhysicsEngineSimple(self.red_player, self.all_collision_list)
        self.physics_engine_blue = arcade.PhysicsEngineSimple(self.blue_player, self.all_collision_list)

        self.red_keys_pressed = set()
        self.blue_keys_pressed = set()

        self.red_angle = RedAngle(self.width, self.height)
        self.blue_angle = BlueAngle(self.width, self.height)
        self.angles_list = arcade.SpriteList()
        self.angles_list.append(self.red_angle)
        self.angles_list.append(self.blue_angle)

        self.create_checkpoints(offset_x, offset_y)

    def update_car_movement(self, car, delta_time):
        if not car.can_move or self.game_over:
            car.change_x = 0
            car.change_y = 0
            return

        max_steering_angle = 45

        if car == self.red_player:
            if arcade.key.A in self.red_keys_pressed and arcade.key.D not in self.red_keys_pressed:
                car.steering_angle = -max_steering_angle
            elif arcade.key.D in self.red_keys_pressed and arcade.key.A not in self.red_keys_pressed:
                car.steering_angle = max_steering_angle
            else:
                car.steering_angle *= 0.7

            if arcade.key.S in self.red_keys_pressed:
                car.is_reversing = True
            else:
                car.is_reversing = False

        elif car == self.blue_player:
            if arcade.key.LEFT in self.blue_keys_pressed and arcade.key.RIGHT not in self.blue_keys_pressed:
                car.steering_angle = -max_steering_angle
            elif arcade.key.RIGHT in self.blue_keys_pressed and arcade.key.LEFT not in self.blue_keys_pressed:
                car.steering_angle = max_steering_angle
            else:
                car.steering_angle *= 0.7

            if arcade.key.DOWN in self.blue_keys_pressed:
                car.is_reversing = True
            else:
                car.is_reversing = False

        car.steering_angle = max(-max_steering_angle, min(max_steering_angle, car.steering_angle))

        speed = -car.reverse_speed if car.is_reversing else car.speed
        steering_rad = math.radians(car.steering_angle)
        angle_rad = math.radians(car.angle)
        new_angle_rad = angle_rad + steering_rad * delta_time * 1.5
        car.angle = math.degrees(new_angle_rad)

        car.change_x = math.sin(new_angle_rad) * abs(speed)
        car.change_y = math.cos(new_angle_rad) * abs(speed)

        if speed < 0:
            car.change_x = -car.change_x
            car.change_y = -car.change_y

    def update_countdown(self, delta_time):
        if not self.is_countdown_active:
            if self.show_go_text:
                self.go_text_timer -= delta_time
                if self.go_text_timer <= 0:
                    self.show_go_text = False
            return

        self.countdown_timer -= delta_time

        if self.countdown_timer > 2.0:
            self.countdown_text = "3"
        elif self.countdown_timer > 1.0:
            self.countdown_text = "2"
        elif self.countdown_timer > 0.0:
            self.countdown_text = "1"
        else:
            self.countdown_text = "GO!"
            self.is_countdown_active = False
            self.show_go_text = True
            self.go_text_timer = 1.0
            self.red_player.can_move = True
            self.blue_player.can_move = True
            angle_rad = math.radians(self.red_player.angle)
            self.red_player.change_x = math.sin(angle_rad) * self.red_player.speed
            self.red_player.change_y = math.cos(angle_rad) * self.red_player.speed

            angle_rad = math.radians(self.blue_player.angle)
            self.blue_player.change_x = math.sin(angle_rad) * self.blue_player.speed
            self.blue_player.change_y = math.cos(angle_rad) * self.blue_player.speed

            if not self.red_player.has_started and not self.blue_player.has_started:
                self.play_start_sound()
                self.red_player.has_started = True
                self.blue_player.has_started = True

    def on_draw(self):
        self.clear()

        self.ground_list.draw()
        self.road_list.draw()
        self.player_list.draw()
        self.finish_list.draw()
        self.on_finish_list.draw()
        self.fance_list.draw()
        self.angles_list.draw()

        if not self.is_countdown_active and not self.show_go_text and not self.game_over:
            self.draw_lap_indicators()

        for particle in self.confetti_particles:
            particle.draw()

        if self.game_over:
            self.manager.draw()

        elif self.is_countdown_active:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (0, 0, 0, 150))

            font_size = 200
            color = arcade.color.WHITE

            arcade.draw_text(self.countdown_text, self.width // 2, self.height // 2, color, font_size,
                             anchor_x="center", anchor_y="center", bold=True)

            arcade.draw_text("Красная машина: A/D/S | Синяя машина: ←/→/↓ ", self.width // 2, self.height // 2 - 100,
                             arcade.color.LIGHT_GRAY, 20, anchor_x="center", anchor_y="center")

        elif self.show_go_text:
            arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height,
                                              (0, 0, 0, max(0, int(150 * self.go_text_timer))))

            alpha = max(0, min(255, int(255 * self.go_text_timer)))
            arcade.draw_text("GO!", self.width // 2, self.height // 2, (0, 255, 0, alpha), 180,
                             anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        if self.game_over:
            if self.confetti_active:
                self.update_confetti(delta_time)
            return

        self.update_countdown(delta_time)

        if not self.is_countdown_active and not self.show_go_text:
            self.update_car_movement(self.red_player, delta_time)
            self.update_car_movement(self.blue_player, delta_time)

            self.physics_engine_red.update()
            self.physics_engine_blue.update()

            self.check_checkpoints(self.red_player)
            self.check_checkpoints(self.blue_player)

            if self.red_player.can_move and self.blue_player.can_move:
                self.play_drive_sound()

    def on_key_press(self, key, modifiers):
        if self.is_countdown_active:
            return

        if key in [arcade.key.A, arcade.key.D, arcade.key.S]:
            self.red_keys_pressed.add(key)
        elif key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.DOWN]:
            self.blue_keys_pressed.add(key)
        elif key == arcade.key.R:
            self.restart_game()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.game_over:
            self.manager.on_mouse_press(x, y, button, modifiers)
            return

    def on_key_release(self, key, modifiers):
        if self.is_countdown_active:
            return

        if key in [arcade.key.A, arcade.key.D, arcade.key.S]:
            if key in self.red_keys_pressed:
                self.red_keys_pressed.remove(key)

            if key == arcade.key.S:
                self.red_player.is_reversing = False
                angle_rad = math.radians(self.red_player.angle)
                self.red_player.change_x = math.sin(angle_rad) * self.red_player.speed
                self.red_player.change_y = math.cos(angle_rad) * self.red_player.speed

        elif key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.DOWN]:
            if key in self.blue_keys_pressed:
                self.blue_keys_pressed.remove(key)

            if key == arcade.key.DOWN:
                self.blue_player.is_reversing = False
                angle_rad = math.radians(self.blue_player.angle)
                self.blue_player.change_x = math.sin(angle_rad) * self.blue_player.speed
                self.blue_player.change_y = math.cos(angle_rad) * self.blue_player.speed


def main():
    game = Races()
    arcade.run()


if __name__ == "__main__":
    main()
