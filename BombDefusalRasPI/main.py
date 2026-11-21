import sys
import random
import pygame
import settings as S
from controls import make_controls
from design import Box, ScreenDisplay, DefuseButton, Cursor
from digital_timer import DigitalTimer
from ArrowGame import ArrowGame
from ColourGame import ColourGame
from NumPad import NumpadGame
from Wires import WiresGame
from endgame import BoomScreen


def load_scaled_image(path, scale):
    image = pygame.image.load(path).convert_alpha()
    new_width = int(image.get_width() * scale)
    new_height = int(image.get_height() * scale)
    return pygame.transform.smoothscale(image, (new_width, new_height))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
        pygame.display.set_caption("Bomb Minigames")
        self.clock = pygame.time.Clock()
        self.defuse_font = pygame.font.SysFont("Consolas", S.DEFUSE_FONT_SIZE, bold=True)

        self.controls = make_controls()
        self.setup_boxes()

        self.numpad_cover = load_scaled_image("images/numpad_cover.png", S.NUMPAD_COVER_SCALE)
        self.colour_cover = load_scaled_image("images/colour_cover.png", S.COLOUR_COVER_SCALE)
        self.red_button = DefuseButton(S.DEFUSE_BUTTON_RADIUS, S.DEFUSE_BUTTON_OFFSET,
                                       S.DEFUSE_BUTTON_COLOR_TOP, S.DEFUSE_BUTTON_COLOR_BTM)
        self.cursor = Cursor(S.CURSOR_START[0], S.CURSOR_START[1])
        self.boom_screen = BoomScreen(self.screen)

        self.new()
        self.setup_mini_wires()

    def setup_boxes(self):
        bg_rect = (0, 0, S.BACKGROUND_BOX_WIDTH, S.BACKGROUND_BOX_HEIGHT)
        self.background_box = Box(bg_rect, S.BG_COLOUR, S.BG_SHADOW_COLOUR, True)

        module_colour = S.GAME_MODULE_COLOUR
        shadow_colour = S.GAME_MODULE_SHADOW_COLOUR
        self.boxes = {
            "arrow": Box(S.ARROW_GAME_RECT, module_colour, shadow_colour),
            "colour": Box(S.COLOUR_GAME_RECT, module_colour, shadow_colour),
            "numpad": Box(S.NUMPAD_GAME_RECT, module_colour, shadow_colour),
            "wires": Box(S.WIRES_GAME_RECT, module_colour, shadow_colour)
        }
        self.timer_box = Box(S.TIMER_GAME_RECT, module_colour, shadow_colour)
        self.defuse_box = Box(S.DEFUSE_RECT, module_colour, shadow_colour)

        self.zooms = {
            "arrow": S.ARROW_GAME_ZOOM,
            "colour": S.COLOUR_GAME_ZOOM,
            "numpad": S.NUMPAD_GAME_ZOOM,
            "wires": S.WIRES_GAME_ZOOM
        }

        self.numpad_display = ScreenDisplay(S.DISPLAY_COLOUR, S.DISPLAY_RIM_COLOUR, S.NUMPAD_DISPLAY_HEIGHT)
        self.arrow_display = ScreenDisplay(S.DISPLAY_COLOUR, S.DISPLAY_RIM_COLOUR)
        self.defuse_display = ScreenDisplay(S.DISPLAY_COLOUR, S.DISPLAY_RIM_COLOUR, S.DEFUSE_DISPLAY_HEIGHT)
        self.timer_display = ScreenDisplay(S.TIMER_DISPLAY_COLOUR, S.DISPLAY_RIM_COLOUR)

    def setup_minigames(self):
        self.arrow_game = ArrowGame(self.boxes["arrow"], S.BG_COLOUR)
        self.colour_game = ColourGame(self.boxes["colour"], S.BG_COLOUR)
        self.numpad_game = NumpadGame(self.boxes["numpad"], S.BG_COLOUR)
        self.wires_game = WiresGame(self.boxes["wires"], S.BG_COLOUR)
        self.minigames = {
            "arrow": self.arrow_game,
            "colour": self.colour_game,
            "numpad": self.numpad_game
        }

    def setup_mini_wires(self):
        # Small copies of the wire pictures for the closed bomb view
        mini_width = self.boxes["wires"].top_shape.width - S.MINI_WIRE_SIDE_SPACE
        mini_height = int(S.WIRE_HEIGHT * mini_width / S.WIRE_WIDTH)
        self.mini_scale = mini_width / S.WIRE_WIDTH

        self.mini_wires = {}
        for wire in self.wires_game.wires:
            uncut = pygame.transform.smoothscale(wire.image_uncut, (mini_width, mini_height))
            cut = pygame.transform.smoothscale(wire.image_cut, (mini_width, mini_height))
            self.mini_wires[wire.colour_name] = (uncut, cut)

    def new(self):
        self.setup_minigames()
        for box in self.boxes.values():
            box.reset_zoom()

        self.available_wires = list(S.WIRE_COLOURS)
        self.current_wire = 1
        self.games_per_round = S.GAMES_PER_WIRE[0]
        self.games_completed = 0
        self.completed_this_round = []
        self.target_game = None
        self.in_minigame = None
        self.state = "IDLE"
        self.defuse_text = "READY"
        self.digital_timer = DigitalTimer(S.TIME_DURATION, S.TIME_FONT_SIZE, self.timer_display)

    # ---------- Game flow ----------

    def handle_game_over(self, is_victory):
        choice = self.boom_screen.display(self.cursor, self.controls, is_victory)
        if choice == "RESTART":
            self.new()
        else:
            pygame.quit()
            sys.exit()

    def pick_next_target(self):
        remaining = []
        for name in self.minigames:
            if name not in self.completed_this_round:
                remaining.append(name)
        self.target_game = random.choice(remaining)

    def advance_to_next_wire(self):
        self.current_wire += 1

        if self.current_wire > len(S.WIRE_COLOURS):
            self.handle_game_over(True)
            return

        self.games_per_round = S.GAMES_PER_WIRE[self.current_wire - 1]
        self.games_completed = 0
        self.completed_this_round = []
        self.target_game = None
        self.state = "IDLE"
        self.defuse_text = "READY"
        self.wires_game.next_wire()

    def handle_defuse_logic(self, pos):
        if not self.red_button.is_clicked(pos):
            return

        if self.state == "IDLE" or self.state == "GAME_COMPLETE":
            self.pick_next_target()
            self.defuse_text = "WATCH LED"
            self.state = "PLAYING"

        elif self.state == "REVEAL_WIRE":
            colour = random.choice(self.available_wires)
            self.available_wires.remove(colour)
            self.wires_game.target_colour = colour
            self.defuse_text = "CUT " + colour
            self.state = "WIRE_WAIT"

        elif self.state == "WIRE_WAIT":
            if self.wires_game.is_disarmed:
                self.advance_to_next_wire()

    def enter_minigame(self, name):
        self.in_minigame = name
        self.boxes[name].zoom(self.zooms[name])

        if name == "wires":
            return

        if name == "numpad":
            self.numpad_game.create_buttons()

        if name == self.target_game:
            self.minigames[name].start()
        else:
            self.minigames[name].stop()

    def finish_minigame(self, name):
        self.completed_this_round.append(name)
        self.boxes[name].reset_zoom()
        self.games_completed += 1
        self.in_minigame = None
        self.target_game = None
        self.defuse_text = "PRESS RED"

        if self.games_completed < self.games_per_round:
            self.state = "GAME_COMPLETE"
        else:
            self.state = "REVEAL_WIRE"

    # ---------- Per-frame updates ----------

    def handle_click(self):
        pos = self.cursor.get_pos()

        if self.in_minigame is None:
            self.handle_defuse_logic(pos)
            for name, box in self.boxes.items():
                if box.rect.collidepoint(pos):
                    self.enter_minigame(name)
                    break
            return

        box = self.boxes[self.in_minigame]
        if box.rect.collidepoint(pos):
            if self.in_minigame == "colour":
                self.colour_game.handle_event(pos)
            elif self.in_minigame == "numpad":
                self.numpad_game.handle_event(pos)
            elif self.in_minigame == "wires":
                result = self.wires_game.handle_event(pos)
                if result is False:
                    self.handle_game_over(False)
        elif self.background_box.rect.collidepoint(pos):
            box.reset_zoom()
            self.in_minigame = None

    def check_arrow_buttons(self):
        arrow_keys = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN
        }
        for name, key in arrow_keys.items():
            if self.controls.just_pressed(name):
                self.arrow_game.handle_event(key)

    def update_minigame(self):
        self.digital_timer.update()
        if self.digital_timer.get_remaining_seconds() <= 0:
            self.handle_game_over(False)
            return

        name = self.in_minigame
        if name == "wires":
            self.wires_game.update(self.cursor.get_pos())
        elif name is not None:
            game = self.minigames[name]
            game.update()
            if name == "arrow":
                self.check_arrow_buttons()
            if name == self.target_game and game.is_finished:
                self.finish_minigame(name)

    def update_cursor(self):
        move_x = (self.controls.is_down("right") - self.controls.is_down("left")) * S.CURSOR_SPEED
        move_y = (self.controls.is_down("down") - self.controls.is_down("up")) * S.CURSOR_SPEED
        self.cursor.update(move_x, move_y)

    def update_physical_leds(self):
        led_index = S.WIRE_LED_OFF
        if self.in_minigame == "wires":
            led_index = self.wires_game.led_index
        self.controls.set_led(led_index)

    def run(self):
        while True:
            self.clock.tick(S.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.controls.update()

            if self.controls.just_pressed("interact"):
                self.handle_click()

            self.update_minigame()
            self.update_cursor()
            self.update_physical_leds()
            self.draw()

    # ---------- Drawing ----------

    def get_light_state(self, name):
        if name == "wires":
            if self.wires_game.is_disarmed:
                return S.LIGHT_GREEN
            if self.state == "WIRE_WAIT":
                return S.LIGHT_FLASHING
            return S.LIGHT_OFF

        if name in self.completed_this_round:
            return S.LIGHT_GREEN
        if name == self.target_game:
            return S.LIGHT_FLASHING
        return S.LIGHT_OFF

    def draw_mini_wires(self):
        box = self.boxes["wires"].rect
        left_bar = pygame.Rect(box.left + 10, box.top + 20, 20, box.height - 40)
        right_bar = pygame.Rect(box.right - 30, box.top + 20, 20, box.height - 40)
        pygame.draw.rect(self.screen, S.WIRE_BAR_COLOUR, left_bar, border_radius=4)
        pygame.draw.rect(self.screen, S.WIRE_BAR_COLOUR, right_bar, border_radius=4)

        for wire in self.wires_game.wires:
            uncut_image, cut_image = self.mini_wires[wire.colour_name]
            if wire.is_cut:
                image = cut_image
            else:
                image = uncut_image
            offset_y = wire.offset_y * self.mini_scale
            image_rect = image.get_rect(center=(box.centerx, box.centery + offset_y))
            self.screen.blit(image, image_rect)

    def draw_bomb(self):
        self.background_box.draw(self.screen)

        for name, box in self.boxes.items():
            box.draw_attachment(self.screen, 1.0, self.get_light_state(name))
        for box in self.boxes.values():
            box.draw(self.screen)
        self.timer_box.draw(self.screen)
        self.defuse_box.draw(self.screen)

        self.numpad_display.draw(self.screen, self.boxes["numpad"])
        self.arrow_display.draw(self.screen, self.boxes["arrow"])
        self.defuse_display.draw(self.screen, self.defuse_box)
        self.timer_display.draw(self.screen, self.timer_box)
        self.red_button.draw(self.screen, self.defuse_box)
        self.digital_timer.draw(self.screen)

        numpad_rect = self.boxes["numpad"].rect
        colour_rect = self.boxes["colour"].rect
        self.screen.blit(self.numpad_cover, (numpad_rect.left + S.NUMPAD_COVER_OFFSET_X, numpad_rect.top))
        self.screen.blit(self.colour_cover, (colour_rect.left + S.COLOUR_COVER_OFFSET_X, colour_rect.top))

        self.draw_mini_wires()

        if self.defuse_text == "READY":
            text_colour = S.DEFUSE_TEXT_READY_COLOUR
        else:
            text_colour = S.DEFUSE_TEXT_BUSY_COLOUR
        text_surface = self.defuse_font.render(self.defuse_text, True, text_colour)
        self.screen.blit(text_surface, text_surface.get_rect(center=self.defuse_display.center))

    def draw_minigame(self):
        name = self.in_minigame
        if name == "wires":
            self.wires_game.draw(self.screen)
        else:
            self.minigames[name].draw(self.screen)
        self.boxes[name].draw_attachment(self.screen, self.zooms[name], self.get_light_state(name))

    def draw(self):
        self.screen.fill(S.WINDOW_COLOUR)

        if self.in_minigame is None:
            self.draw_bomb()
        else:
            self.draw_minigame()

        self.cursor.draw(self.screen)
        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()