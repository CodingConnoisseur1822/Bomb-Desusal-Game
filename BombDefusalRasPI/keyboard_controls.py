import pygame
import settings as S


class KeyboardControls:
    def __init__(self):
        self.current = {}
        self.previous = {}
        for name in S.KEYBOARD_KEYS:
            self.current[name] = False
            self.previous[name] = False

    def update(self):
        keys = pygame.key.get_pressed()
        for name in S.KEYBOARD_KEYS:
            self.previous[name] = self.current[name]
            self.current[name] = keys[S.KEYBOARD_KEYS[name]]

    def is_down(self, name):
        return self.current[name]

    def just_pressed(self, name):
        return self.current[name] and not self.previous[name]

    def set_led(self, led_index):
        pass