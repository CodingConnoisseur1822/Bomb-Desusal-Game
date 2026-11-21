import random
import pygame
import settings as S
from Audio import Audio


class NumpadButton:
    def __init__(self, text, size, pos, font):
        self.text = text
        self.elevation = S.NUMPAD_BUTTON_ELEVATION
        self.dynamic_elevation = self.elevation
        self.original_y = pos[1]
        self.last_click_time = 0

        self.top_colour = (100, 110, 120)
        self.bottom_colour = (40, 45, 50)

        self.top_rect = pygame.Rect(pos, (size, size))
        self.bottom_rect = pygame.Rect(pos, (size, size + self.elevation))

        self.text_surface = font.render(text, True, (220, 220, 220))
        self.text_rect = self.text_surface.get_rect(center=self.top_rect.center)

    def draw(self, screen):
        if pygame.time.get_ticks() - self.last_click_time > S.NUMPAD_BUTTON_RELEASE_TIME:
            self.dynamic_elevation = self.elevation

        self.top_rect.y = self.original_y - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        pygame.draw.rect(screen, self.bottom_colour, self.bottom_rect, border_radius=8)
        pygame.draw.rect(screen, self.top_colour, self.top_rect, border_radius=8)
        pygame.draw.rect(screen, (30, 30, 30), self.top_rect, 2, border_radius=8)
        screen.blit(self.text_surface, self.text_rect)

    def check_click(self, pos):
        if self.top_rect.collidepoint(pos):
            self.dynamic_elevation = 0
            self.last_click_time = pygame.time.get_ticks()
            return True
        return False


class NumpadGame:
    def __init__(self, grey_box, background_colour):
        self.grey_box = grey_box
        self.background_colour = background_colour
        self.buttons = []

        self.is_active = False
        self.is_finished = False
        self.waiting_input = False

        self.sequence = []
        self.user_input = ""
        self.shown_digit = ""
        self.show_index = 0
        self.show_timer = 0

        self.display_font = pygame.font.SysFont("Consolas", 50, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 30, bold=True)

        self.key_sound = Audio(800, 0.1)
        self.delete_sound = Audio(400, 0.1)
        self.show_sound = Audio(600, 0.15)
        self.wrong_sound = Audio(200, 0.6)

    def create_buttons(self):
        self.buttons = []
        layout = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["<", "0", "E"]]
        size = S.NUMPAD_BUTTON_SIZE
        gap = S.NUMPAD_BUTTON_GAP

        grid_width = (3 * size) + (2 * gap)
        start_x = self.grey_box.rect.centerx - (grid_width // 2)
        start_y = self.grey_box.rect.top + S.NUMPAD_BUTTONS_TOP_OFFSET

        for row in range(len(layout)):
            for col in range(len(layout[row])):
                pos = (start_x + col * (size + gap), start_y + row * (size + gap))
                self.buttons.append(NumpadButton(layout[row][col], size, pos, self.button_font))

    def start(self):
        self.is_active = True
        self.is_finished = False
        self.reset_round()

    def stop(self):
        self.is_active = False
        self.is_finished = True

    def reset_round(self):
        self.user_input = ""
        self.shown_digit = ""
        self.show_index = 0
        self.show_timer = pygame.time.get_ticks()
        self.waiting_input = False

        length = random.randint(S.NUMPAD_MIN_DIGITS, S.NUMPAD_MAX_DIGITS)
        self.sequence = []
        for i in range(length):
            self.sequence.append(str(random.randint(0, 9)))

    def handle_event(self, pos):
        if not self.is_active or self.is_finished or not self.waiting_input:
            return

        for button in self.buttons:
            if button.check_click(pos):
                if button.text == "<":
                    self.user_input = self.user_input[:-1]
                    self.delete_sound.play()
                elif button.text == "E":
                    self.check_answer()
                elif len(self.user_input) < S.NUMPAD_MAX_INPUT:
                    self.user_input += button.text
                    self.key_sound.play()
                break

    def check_answer(self):
        if self.user_input == "".join(self.sequence):
            self.is_finished = True
            Audio.play_victory()
        else:
            self.wrong_sound.play()
            self.reset_round()

    def update(self):
        if not self.is_active or self.is_finished or self.waiting_input:
            return

        now = pygame.time.get_ticks()
        if now - self.show_timer > S.NUMPAD_SHOW_DELAY:
            if self.show_index < len(self.sequence):
                self.shown_digit = self.sequence[self.show_index]
                self.show_sound.play()
                self.show_index += 1
                self.show_timer = now
            else:
                self.shown_digit = ""
                self.waiting_input = True

    def draw(self, screen):
        screen.fill(self.background_colour)
        self.grey_box.draw(screen, zoom=S.NUMPAD_GAME_ZOOM)

        box = self.grey_box.rect
        margin = S.NUMPAD_DISPLAY_SIDE_MARGIN
        rim_rect = pygame.Rect(box.left + margin, box.top + margin,
                               box.width - 2 * margin, S.NUMPAD_DISPLAY_HEIGHT)
        display_rect = rim_rect.inflate(-15, -15)
        pygame.draw.rect(screen, S.DISPLAY_RIM_COLOUR, rim_rect, border_radius=10)
        pygame.draw.rect(screen, S.DISPLAY_COLOUR, display_rect, border_radius=8)

        for button in self.buttons:
            button.draw(screen)

        if not self.is_active:
            return

        if self.is_finished:
            colour = (50, 200, 50)
            text = "PASS"
        elif not self.waiting_input:
            colour = (200, 50, 50)
            text = self.shown_digit
        else:
            colour = (40, 40, 40)
            text = self.user_input

        if text != "":
            text_surface = self.display_font.render(text, True, colour)
            screen.blit(text_surface, text_surface.get_rect(center=display_rect.center))