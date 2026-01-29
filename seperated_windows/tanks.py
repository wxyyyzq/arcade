import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Red vs Blue: Tank Battle"
TANK_SCALE = 1
TANK_SPEED = 3

ROCKET_SCALE = 0.5
ROCKET_SPEED = 4


class Tank(arcade.Sprite):
    def __init__(self, color, x, y):
        super().__init__(f"images/tank_{color}.png", TANK_SCALE)

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.color = color

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT

    def shoot(self):
        rocket = Rocket(self.center_x, self.center_y, self.color)
        return rocket


class Rocket(arcade.Sprite):
    def __init__(self, x, y, owner_color):
        super().__init__(f"images / rocket{owner_color}.png", ROCKET_SCALE)

        self.center_x = x
        self.center_y = y
        self.owner_color = owner_color

    def update(self):
        if self.owner_color == "red":
            self.center_y += ROCKET_SPEED
        else:
            self.center_y -= ROCKET_SPEED

        if (self.owner_color == "red" and self.bottom > SCREEN_HEIGHT) or \
                (self.owner_color == "blue" and self.top < 0):
            self.remove_from_sprite_lists()


class TankGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_GREEN)

        self.red_tank = None
        self.blue_tank = None
        self.rockets = None
        self.game_over = False

    def setup(self):

        self.red_tank = Tank('red', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

        self.blue_tank = Tank('blue', SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

        self.rockets = arcade.SpriteList()

        self.game_over = False

    def on_draw(self):
        arcade.start_render()

        self.red_tank.draw()
        self.blue_tank.draw()
        self.rockets.draw()

        if self.game_over:
            arcade.draw_text("GAME OVER!",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, 50,
                             anchor_x="center", anchor_y="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.red_tank.update()
        self.blue_tank.update()
        self.rockets.update()

        for rocket in self.rockets:
            if rocket.owner_color == "red" and arcade.check_for_collision(rocket, self.blue_tank):
                self.game_over = True
                arcade.close_window()
            elif rocket.owner_color == "blue" and arcade.check_for_collision(rocket, self.red_tank):
                self.game_over = True
                arcade.close_window()

    def on_key_press(self, key, modifiers):
        if self.game_over:
            return

        if key == arcade.key.UP:
            self.red_tank.change_y = TANK_SPEED
            rocket = self.red_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.DOWN:
            self.red_tank.change_y = -TANK_SPEED
            rocket = self.red_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.LEFT:
            self.red_tank.change_x = -TANK_SPEED
            rocket = self.red_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.RIGHT:
            self.red_tank.change_x = TANK_SPEED
            rocket = self.red_tank.shoot()
            self.rockets.append(rocket)

        if key == arcade.key.W:
            self.blue_tank.change_y = TANK_SPEED
            rocket = self.blue_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.S:
            self.blue_tank.change_y = -TANK_SPEED
            rocket = self.blue_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.A:
            self.blue_tank.change_x = -TANK_SPEED
            rocket = self.blue_tank.shoot()
            self.rockets.append(rocket)
        elif key == arcade.key.D:
            self.blue_tank.change_x = TANK_SPEED
            rocket = self.blue_tank.shoot()
            self.rockets.append(rocket)

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.red_tank.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.red_tank.change_x = 0

        if key in [arcade.key.W, arcade.key.S]:
            self.blue_tank.change_y = 0
        elif key in [arcade.key.A, arcade.key.D]:
            self.blue_tank.change_x = 0


def main():
    game = TankGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
