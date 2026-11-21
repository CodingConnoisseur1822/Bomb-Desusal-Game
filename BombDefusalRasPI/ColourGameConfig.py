import pygame
import settings as S


class ColourLED:
    def __init__(self, image_on, image_off):
        size = (S.LED_IMAGE_SIZE, S.LED_IMAGE_SIZE)
        self.image_on = pygame.transform.scale(pygame.image.load(image_on), size)
        self.image_off = pygame.transform.scale(pygame.image.load(image_off), size)
        self.x = 0
        self.y = 0
        self.is_on = False

    def draw(self, screen):
        if self.is_on:
            screen.blit(self.image_on, (self.x, self.y))
        else:
            screen.blit(self.image_off, (self.x, self.y))


class ColourSwitch:
    def __init__(self, image_on, image_off, led):
        size = (S.LED_IMAGE_SIZE, S.LED_IMAGE_SIZE)
        self.image_on = pygame.transform.scale(pygame.image.load(image_on), size)
        self.image_off = pygame.transform.scale(pygame.image.load(image_off), size)
        self.x = 0
        self.y = 0
        self.is_on = False
        self.led = led

    def draw(self, screen):
        if self.is_on:
            screen.blit(self.image_on, (self.x, self.y))
        else:
            screen.blit(self.image_off, (self.x, self.y))

    def light_up(self):
        self.is_on = True
        self.led.is_on = True

    def turn_off(self):
        self.is_on = False
        self.led.is_on = False

    def clicked(self, pos):
        mouse_x, mouse_y = pos
        return (self.x <= mouse_x <= self.x + S.LED_IMAGE_SIZE and
                self.y <= mouse_y <= self.y + S.LED_IMAGE_SIZE)