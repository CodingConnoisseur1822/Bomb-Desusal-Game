import random
import pygame
import settings as S
from Audio import Audio

KEYS_FOR_ANGLE = {
    0: pygame.K_LEFT,
    90: pygame.K_DOWN,
    180: pygame.K_RIGHT,
    270: pygame.K_UP
}


class Arrow(pygame.sprite.Sprite):
    base_image = pygame.image.load("images/Left-arrow.png")

    def __init__(self, x, y, angle):
        super().__init__()
        size = Arrow.base_image.get_size()
        new_size = (int(size[0] * S.ARROW_SCALE), int(size[1] * S.ARROW_SCALE))
        scaled_image = pygame.transform.scale(Arrow.base_image, new_size)

        self.image = pygame.transform.rotate(scaled_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.cleared_image = self.image.copy()
        self.cleared_image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)

    def set_cleared(self):
        self.image = self.cleared_image


class ArrowGame:
    def __init__(self, grey_box, background_colour):
        self.grey_box = grey_box
        self.background_colour = background_colour
        self.is_active = False
        self.is_finished = False

        self.arrow_group = pygame.sprite.Group()
        self.arrows = []
        self.correct_keys = []
        self.spawn_queue = []

        self.rounds_completed = 0
        self.current_arrow = 0
        self.arrow_count = 0
        self.spawn_timer = 0
        self.round_end_time = 0

        self.spawn_sound = Audio(800, 0.05)
        self.correct_sound = Audio(1000, 0.1)
        self.wrong_sound = Audio(200, 0.3)
        self.round_sound = Audio(1200, 0.4)

    def start(self):
        self.is_active = True
        self.is_finished = False
        self.rounds_completed = 0
        self.reset_round()

    def stop(self):
        self.is_active = False
        self.is_finished = True

    def reset_round(self):
        self.arrow_group.empty()
        self.arrows = []
        self.correct_keys = []
        self.spawn_queue = []
        self.current_arrow = 0
        self.round_end_time = 0
        self.arrow_count = random.randint(S.ARROW_MIN, S.ARROW_MAX)

    def get_screen_rects(self):
        rim_rect = self.grey_box.rect.inflate(-S.ARROW_RIM_MARGIN, -S.ARROW_RIM_MARGIN)
        display_rect = rim_rect.inflate(-S.ARROW_INNER_MARGIN, -S.ARROW_INNER_MARGIN)
        return rim_rect, display_rect

    def create_arrows(self, display_rect):
        total_width = S.ARROW_SPACING * (self.arrow_count - 1)
        start_x = display_rect.centerx - total_width // 2
        y = display_rect.centery

        for i in range(self.arrow_count):
            angle = random.choice([0, 90, 180, 270])
            arrow = Arrow(start_x + i * S.ARROW_SPACING, y, angle)
            self.arrows.append(arrow)
            self.correct_keys.append(KEYS_FOR_ANGLE[angle])

        middle = self.arrow_count // 2
        if self.arrow_count % 2 != 0:
            self.spawn_queue.append([self.arrows[middle]])
            left = middle - 1
            right = middle + 1
        else:
            left = middle - 1
            right = middle

        while left >= 0 and right < self.arrow_count:
            self.spawn_queue.append([self.arrows[left], self.arrows[right]])
            left -= 1
            right += 1

        self.spawn_timer = pygame.time.get_ticks()

    def handle_event(self, key):
        if not self.is_active or self.is_finished:
            return
        if self.spawn_queue or self.round_end_time != 0:
            return
        if self.current_arrow >= len(self.correct_keys):
            return

        if key != self.correct_keys[self.current_arrow]:
            self.wrong_sound.play()
            self.reset_round()
            return

        self.correct_sound.play()
        self.arrows[self.current_arrow].set_cleared()
        self.current_arrow += 1

        if self.current_arrow < len(self.correct_keys):
            return

        self.rounds_completed += 1
        if self.rounds_completed >= S.ARROW_ROUNDS:
            Audio.play_victory()
            self.is_finished = True
        else:
            self.round_sound.play()
            self.round_end_time = pygame.time.get_ticks()

    def update(self):
        if not self.is_active or self.is_finished:
            return

        now = pygame.time.get_ticks()

        if self.round_end_time != 0:
            if now - self.round_end_time > S.ARROW_RESET_DELAY:
                self.reset_round()
            return

        if not self.arrows:
            rim_rect, display_rect = self.get_screen_rects()
            self.create_arrows(display_rect)

        if self.spawn_queue and now - self.spawn_timer > S.ARROW_SPAWN_DELAY:
            wave = self.spawn_queue.pop(0)
            self.spawn_sound.play()
            for arrow in wave:
                self.arrow_group.add(arrow)
            self.spawn_timer = now

    def draw(self, screen):
        screen.fill(self.background_colour)
        self.grey_box.draw(screen, zoom=S.ARROW_GAME_ZOOM)

        rim_rect, display_rect = self.get_screen_rects()
        pygame.draw.rect(screen, S.DISPLAY_RIM_COLOUR, rim_rect, border_radius=10)
        pygame.draw.rect(screen, S.DISPLAY_COLOUR, display_rect, border_radius=8)

        self.arrow_group.draw(screen)