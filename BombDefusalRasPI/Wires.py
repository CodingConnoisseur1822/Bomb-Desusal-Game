import pygame
import settings as S


class Wire:
    def __init__(self, colour_name, offset_y):
        self.colour_name = colour_name
        self.offset_y = offset_y
        self.is_cut = False

        file_name = colour_name.capitalize()
        size = (S.WIRE_WIDTH, S.WIRE_HEIGHT)
        uncut = pygame.image.load("images/" + file_name + "_wire.png").convert_alpha()
        cut = pygame.image.load("images/" + file_name + "_wire_cut.png").convert_alpha()
        self.image_uncut = pygame.transform.scale(uncut, size)
        self.image_cut = pygame.transform.scale(cut, size)

        self.image = self.image_uncut
        self.rect = self.image.get_rect()

    def cut(self):
        self.is_cut = True
        self.image = self.image_cut

    def update_pos(self, center_x, center_y):
        self.rect.centerx = center_x
        self.rect.centery = center_y + self.offset_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class WiresGame:
    def __init__(self, grey_box, background_colour):
        self.grey_box = grey_box
        self.background_colour = background_colour
        self.is_disarmed = False
        self.target_colour = None
        self.led_index = S.WIRE_LED_OFF
        self.led_timer = 0

        self.wires = []
        for i in range(len(S.WIRE_COLOURS)):
            self.wires.append(Wire(S.WIRE_COLOURS[i], S.WIRE_OFFSETS[i]))

    def next_wire(self):
        self.is_disarmed = False
        self.target_colour = None
        self.led_index = S.WIRE_LED_OFF
        self.led_timer = 0

    def handle_event(self, cursor_pos):
        # Returns True for a correct cut, False for a mistake, None if nothing happened
        if self.is_disarmed:
            return None

        for wire in self.wires:
            if wire.is_cut or not wire.rect.collidepoint(cursor_pos):
                continue

            if self.led_index != S.WIRE_LED_BLUE:
                return False
            if wire.colour_name != self.target_colour:
                return False

            wire.cut()
            self.is_disarmed = True
            self.led_index = S.WIRE_LED_OFF
            return True

        return None

    def update(self, cursor_pos):
        if self.target_colour is None or self.is_disarmed:
            self.led_index = S.WIRE_LED_OFF
            self.led_timer = 0
            return

        hovering_target = False
        for wire in self.wires:
            if wire.colour_name == self.target_colour and wire.rect.collidepoint(cursor_pos):
                hovering_target = True

        if not hovering_target:
            self.led_index = S.WIRE_LED_OFF
            self.led_timer = 0
            return

        now = pygame.time.get_ticks()
        if self.led_timer == 0:
            self.led_timer = now

        hover_time = now - self.led_timer
        if hover_time < S.WIRE_RED_TIME:
            self.led_index = S.WIRE_LED_RED
        elif hover_time < S.WIRE_YELLOW_TIME:
            self.led_index = S.WIRE_LED_YELLOW
        elif hover_time < S.WIRE_BLUE_TIME:
            self.led_index = S.WIRE_LED_BLUE
        else:
            self.led_index = S.WIRE_LED_OFF
            self.led_timer = 0

    def draw(self, screen):
        screen.fill(self.background_colour)
        self.grey_box.draw(screen, zoom=S.WIRES_GAME_ZOOM)

        box = self.grey_box.rect
        left_socket = pygame.Rect(box.left + 25, box.top + 40, 50, box.height - 80)
        right_socket = pygame.Rect(box.right - 75, box.top + 40, 50, box.height - 80)
        pygame.draw.rect(screen, S.WIRE_BAR_COLOUR, left_socket, border_radius=8)
        pygame.draw.rect(screen, S.WIRE_BAR_COLOUR, right_socket, border_radius=8)

        for wire in self.wires:
            wire.update_pos(box.centerx, box.centery)
            wire.draw(screen)