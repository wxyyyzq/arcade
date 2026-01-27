import arcade
import random
import math
from arcade.gui import UIManager, UITextureButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from arcade.particles import FadeParticle, Emitter, EmitBurst
from pyglet.resource import texture

OBJECT_SPEED = 5
CAR_SCALE = 1.25
BUFFER_DISTANCE = 50


class Car(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = CAR_SCALE
        self.texture = random.choice([
            arcade.load_texture("Assets/images/car_red_tires.png"),
            arcade.load_texture("Assets/images/tank_red.png"),
            arcade.load_texture("Assets/images/tank_blue.png"),
            arcade.load_texture("Assets/images/car_cyan_tires.png")
        ])
        self.spawn_outside_screen()
        self.set_direction()

    def set_direction(self):
        angle_degrees = random.uniform(0, 360)
        angle_radians = math.radians(angle_degrees)

        self.change_x = OBJECT_SPEED * math.cos(angle_radians)
        self.change_y = OBJECT_SPEED * math.sin(angle_radians)

        self.angle = -angle_degrees + 90

    def spawn_outside_screen(self):
        screen_width = arcade.get_window().width
        screen_height = arcade.get_window().height

        offset = 50
        side = random.randint(0, 3)
        if side == 0:  
            self.center_x = random.uniform(0, screen_width)
            self.center_y = screen_height + offset
        elif side == 1:  
            self.center_x = screen_width + offset
            self.center_y = random.uniform(0, screen_height)
        elif side == 2:  
            self.center_x = random.uniform(0, screen_width)
            self.center_y = 0 - offset
        else:  
            self.center_x = 0 - offset
            self.center_y = random.uniform(0, screen_height)

    def is_out_of_bounds(self):
        screen_width = arcade.get_window().width
        screen_height = arcade.get_window().height

        return (self.center_x < -BUFFER_DISTANCE or
                self.center_x > screen_width + BUFFER_DISTANCE or
                self.center_y < -BUFFER_DISTANCE or
                self.center_y > screen_height + BUFFER_DISTANCE)

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x
        self.center_y += self.change_y


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=True)
        arcade.set_background_color(arcade.color.LIGHT_GRAY)

        self.current_sprites = None
        self.explosion_emitters = []
        self.explosion_textures = [
            arcade.load_texture("Assets/images/explosion1.png"),
            arcade.load_texture("Assets/images/explosion2.png"),
            arcade.load_texture("Assets/images/explosion3.png")
        ]

        self.manager = UIManager()
        self.manager.enable()

        self.main_horizontal = UIBoxLayout(vertical=False, space_between=40, padding=(20, 20, 20, 20))

        self.box_layout1 = UIBoxLayout(vertical=True, space_between=30)
        self.box_layout2 = UIBoxLayout(vertical=True, space_between=30)
        self.box_layout3 = UIBoxLayout(vertical=True, space_between=30)

        self.setup()

    def setup(self):
        self.current_sprites = arcade.SpriteList()
        for _ in range(5):
            car = Car()
            self.current_sprites.append(car)

        self.setup_widgets()

        self.main_horizontal.add(self.box_layout1)
        self.main_horizontal.add(self.box_layout2)
        self.main_horizontal.add(self.box_layout3)

        self.anchor_layout = UIAnchorLayout()
        self.anchor_layout.add(self.main_horizontal)

        self.manager.add(self.anchor_layout)

        music = arcade.load_sound("Assets/sound/background_menu.wav")
        arcade.play_sound(music, loop=True)

    def setup_widgets(self):
        info_label_red = UILabel(
            text="to move:",
            font_size=30,
            text_color=arcade.color.WHITE,
            width=300,
            align="left"
        )
        self.box_layout1.add(info_label_red)
        press_blue = UITextureButton(texture=arcade.load_texture("Assets/images/wasd.png"), scale=0.8)
        self.box_layout1.add(press_blue)

        player_red = UITextureButton(texture=arcade.load_texture("Assets/images/red_player.png"))
        self.box_layout1.add(player_red)

        label = UILabel(
            text="Games for 2 players",
            font_size=50,
            text_color=arcade.color.WHITE,
            width=500,
            align="center",
            bold=True
        )
        self.box_layout2.add(label)

        self.hor_andrew_layout = UIBoxLayout(vertical=False, space_between=80)
        self.box_layout2.add(self.hor_andrew_layout)

        texture_bombs = arcade.load_texture("Assets/images/bombs.png")
        bombs_button = UITextureButton(texture=texture_bombs, scale=0.8)
        self.hor_andrew_layout.add(bombs_button)

        texture_tanks = arcade.load_texture("Assets/images/tanks.png")
        tanks_button = UITextureButton(texture=texture_tanks, scale=0.8)
        self.hor_andrew_layout.add(tanks_button)

        self.hor_anna_layout = UIBoxLayout(vertical=False, space_between=80)
        self.box_layout2.add(self.hor_anna_layout)

        texture_crocodile = arcade.load_texture("Assets/images/crocodile.png")
        crocodile_button = UITextureButton(texture=texture_crocodile, scale=0.8)
        self.hor_anna_layout.add(crocodile_button)

        texture_race = arcade.load_texture("Assets/images/race.png")
        race_button = UITextureButton(texture=texture_race, scale=0.8)
        self.hor_anna_layout.add(race_button)

        info_label_blue = UILabel(
            text="to move:",
            font_size=30,
            text_color=arcade.color.WHITE,
            width=300,
            align="left"
        )
        self.box_layout3.add(info_label_blue)

        press_red = UITextureButton(texture=arcade.load_texture("Assets/images/strelochki.png"), scale=0.8)
        self.box_layout3.add(press_red)

        player_blue = UITextureButton(texture=arcade.load_texture("Assets/images/blue_player.png"))
        self.box_layout3.add(player_blue)

    def make_explosion(self, x, y, count=80):
        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(count),
            particle_factory=lambda emitter: FadeParticle(
                filename_or_texture=random.choice(self.explosion_textures),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.5),
                start_alpha=255,
                end_alpha=0,
                scale=random.uniform(0.35, 0.8),
            ),
        )

    def on_draw(self):
        self.clear()
        self.current_sprites.draw()
        for emitter in self.explosion_emitters:
            emitter.draw()

        self.manager.draw()

    def on_update(self, delta_time):
        self.current_sprites.update(delta_time)

        explosions_to_remove = []
        for i, emitter in enumerate(self.explosion_emitters):
            emitter.update(delta_time)
            if emitter.can_reap():
                explosions_to_remove.append(i)

        for index in sorted(explosions_to_remove, reverse=True):
            del self.explosion_emitters[index]

        sprites_to_remove = []
        for sprite in self.current_sprites:
            if sprite.is_out_of_bounds():
                sprites_to_remove.append(sprite)

        for sprite in sprites_to_remove:
            sprite.remove_from_sprite_lists()

        while len(self.current_sprites) < 5:
            new_car = Car()
            self.current_sprites.append(new_car)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            clicked_sprites = arcade.get_sprites_at_point((x, y), self.current_sprites)
            for car in clicked_sprites:
                explosion = self.make_explosion(car.center_x, car.center_y, count=50)
                self.explosion_emitters.append(explosion)

                for _ in range(3):
                    offset_x = random.uniform(-30, 30)
                    offset_y = random.uniform(-30, 30)
                    small_explosion = self.make_explosion(
                        car.center_x + offset_x,
                        car.center_y + offset_y,
                        count=30
                    )
                    self.explosion_emitters.append(small_explosion)

                car.remove_from_sprite_lists()


    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
