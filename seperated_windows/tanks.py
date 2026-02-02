import arcade
import math

TANK_SCALE = 1
TANK_SPEED = 1.5

ROCKET_SCALE = 0.5
ROCKET_SPEED = 5


class Tank_red(arcade.Sprite):
    def __init__(self):
        super(Tank_red, self).__init__()
        self.texture = arcade.load_texture(f'Assets/images/tank_red.png')
        self.center_x = arcade.get_window().width // 2
        self.center_y = arcade.get_window().height // 4

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        elif self.right > arcade.get_window().width:
            self.right = arcade.get_window().width

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > arcade.get_window().height:
            self.top = arcade.get_window().height

        if self.change_x != 0 or self.change_y != 0:
            angle_rad = math.atan2(self.change_x, self.change_y)
            self.angle = math.degrees(angle_rad)

    def shoot(self, angle):
        rocket = Rocket_red(self.center_x, self.center_y, angle)
        return rocket


class Tank_blue(arcade.Sprite):
    def __init__(self):
        super(Tank_blue, self).__init__()
        self.texture = arcade.load_texture(f'Assets/images/tank_blue.png')
        self.center_x = arcade.get_window().width // 2
        self.center_y = arcade.get_window().height * 3 // 4

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        elif self.right > arcade.get_window().width:
            self.right = arcade.get_window().width

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > arcade.get_window().height:
            self.top = arcade.get_window().height

        if self.change_x != 0 or self.change_y != 0:
            angle_rad = math.atan2(self.change_x, self.change_y)
            self.angle = math.degrees(angle_rad)

    def shoot(self, angle):
        rocket = Rocket_blue(self.center_x, self.center_y, angle)
        return rocket


class Rocket_red(arcade.Sprite):
    def __init__(self, start_x, start_y, angle):
        super().__init__(arcade.load_texture(':resources:/images/topdown_tanks/tankRed_barrel1.png'), ROCKET_SCALE)
        self.texture = arcade.load_texture(':resources:/images/topdown_tanks/tankRed_barrel1.png')
        self.center_x = start_x
        self.center_y = start_y
        self.angle = angle
        self.owner_color = "red"
        self.angle = math.radians(angle - 90)
        self.change_x = ROCKET_SPEED * math.cos(self.angle)
        self.change_y = ROCKET_SPEED * math.sin(self.angle)
        if self.change_x != 0 or self.change_y != 0:
            angle_rad = math.atan2(self.change_x, self.change_y)
            self.angle = math.degrees(angle_rad)

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (self.owner_color == "red" and self.bottom > arcade.get_window().height) or \
                (self.owner_color == "blue" and self.top < 0):
            self.remove_from_sprite_lists()


class Rocket_blue(arcade.Sprite):
    def __init__(self, start_x, start_y, angle):
        super().__init__(arcade.load_texture(':resources:/images/topdown_tanks/tankBlue_barrel1.png'), ROCKET_SCALE)
        self.texture = arcade.load_texture(':resources:/images/topdown_tanks/tankBlue_barrel1.png')
        self.center_x = start_x
        self.center_y = start_y
        self.angle = angle
        self.owner_color = "blue"
        self.angle = math.radians(angle - 90)
        self.change_x = ROCKET_SPEED * math.cos(self.angle)
        self.change_y = ROCKET_SPEED * math.sin(self.angle)
        if self.change_x != 0 or self.change_y != 0:
            angle_rad = math.atan2(self.change_x, self.change_y)
            self.angle = math.degrees(angle_rad)

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if (self.owner_color == "red" and self.bottom > arcade.get_window().height) or \
                (self.owner_color == "blue" and self.top < 0):
            self.remove_from_sprite_lists()


class TankGame(arcade.Window):
    def __init__(self):
        super().__init__()
        self.texture_back = arcade.load_texture(f'Assets/images/place_of_tanks.png')
        self.red_tank = Tank_red()
        self.blue_tank = Tank_blue()
        self.game_over = False
        self.setup()

    def setup(self):
        self.rockets = arcade.SpriteList()
        self.tanks_list = arcade.SpriteList()
        self.tanks_list.append(self.red_tank)
        self.tanks_list.append(self.blue_tank)
        self.keys_pressed = set()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.texture_back,
                                 arcade.rect.XYWH(arcade.get_window().width // 2, arcade.get_window().height // 2,
                                                  arcade.get_window().width, arcade.get_window().height))
        self.tanks_list.draw()
        self.rockets.draw()

        if self.game_over and self.winner == 'red':
            arcade.draw_text("WINNER IS RED!",
                             arcade.get_window().width // 2, arcade.get_window().height // 2,
                             arcade.color.RED, 50,
                             anchor_x="center", anchor_y="center")

        elif self.game_over and self.winner == 'blue':
            arcade.draw_text("WINNER IS BLUE!",
                             arcade.get_window().width // 2, arcade.get_window().height // 2,
                             arcade.color.BLUE, 50,
                             anchor_x="center", anchor_y="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.red_tank.update(delta_time)
        self.blue_tank.update(delta_time)
        self.rockets.update()

        for rocket in self.rockets:
            if rocket.owner_color == "red" and arcade.check_for_collision(rocket, self.blue_tank):
                self.game_over = True
                self.winner = 'red'
            elif rocket.owner_color == "blue" and arcade.check_for_collision(rocket, self.red_tank):
                self.game_over = True
                self.winner = 'blue'

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if self.game_over:
            return
        if arcade.key.UP in self.keys_pressed:
            self.blue_tank.change_y = TANK_SPEED
            rocket = self.blue_tank.shoot(180)
            self.rockets.append(rocket)
        if arcade.key.DOWN in self.keys_pressed:
            self.blue_tank.change_y = -TANK_SPEED
            rocket = self.blue_tank.shoot(0)
            self.rockets.append(rocket)
        if arcade.key.LEFT in self.keys_pressed:
            self.blue_tank.change_x = -TANK_SPEED
            rocket = self.blue_tank.shoot(270)
            self.rockets.append(rocket)
        if arcade.key.RIGHT in self.keys_pressed:
            self.blue_tank.change_x = TANK_SPEED
            rocket = self.blue_tank.shoot(90)
            self.rockets.append(rocket)

        if arcade.key.W in self.keys_pressed:
            self.red_tank.change_y = TANK_SPEED
            rocket = self.red_tank.shoot(180)
            self.rockets.append(rocket)
        if arcade.key.S in self.keys_pressed:
            self.red_tank.change_y = -TANK_SPEED
            rocket = self.red_tank.shoot(0)
            self.rockets.append(rocket)
        if arcade.key.A in self.keys_pressed:
            self.red_tank.change_x = -TANK_SPEED
            rocket = self.red_tank.shoot(270)
            self.rockets.append(rocket)
        if arcade.key.D in self.keys_pressed:
            self.red_tank.change_x = TANK_SPEED
            rocket = self.red_tank.shoot(90)
            self.rockets.append(rocket)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.blue_tank.change_x = 0
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.blue_tank.change_y = 0

        if key in [arcade.key.W, arcade.key.S]:
            self.red_tank.change_x = 0
        if key in [arcade.key.A, arcade.key.D]:
            self.red_tank.change_y = 0


def main():
    game = TankGame()
    arcade.run()


if __name__ == "__main__":
    main()

