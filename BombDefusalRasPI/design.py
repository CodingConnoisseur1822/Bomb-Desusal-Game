import pygame
import settings as S


class FlashingLight:
    def __init__(self, colour=(255, 0, 0), interval=500):
        self.colour = colour
        self.interval = interval
        self.green = (0, 255, 0)
        self.off_colour = (20, 20, 20)

    def draw(self, screen, x, y, radius, state):
        light_colour = self.off_colour

        if state == S.LIGHT_GREEN:
            light_colour = self.green
        elif state == S.LIGHT_FLASHING:
            if (pygame.time.get_ticks() // self.interval) % 2 != 0:
                light_colour = self.colour

        pygame.draw.circle(screen, (50, 50, 50), (x, y), radius + 2)
        pygame.draw.circle(screen, light_colour, (x, y), radius)


class Cursor:
    def __init__(self, x, y):
        self.image = pygame.image.load("images/clicker.png").convert_alpha()
        self.x = x
        self.y = y

    def update(self, move_x, move_y):
        self.x = max(0, min(self.x + move_x, S.SCREEN_WIDTH))
        self.y = max(0, min(self.y + move_y, S.SCREEN_HEIGHT))

    def get_pos(self):
        return (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Box:
    def __init__(self, rect_tuple, top_colour, bottom_colour, is_background=False):
        self.top_shape = pygame.Rect(rect_tuple)
        self.rect = self.top_shape.copy()
        self.top_colour = top_colour
        self.bottom_colour = bottom_colour
        self.light = FlashingLight()

        if is_background:
            self.rect.center = (S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2)

    def zoom(self, factor):
        new_width = int(self.top_shape.width * factor)
        new_height = int(self.top_shape.height * factor)
        self.rect = pygame.Rect(0, 0, new_width, new_height)
        self.rect.center = (S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2)

    def reset_zoom(self):
        self.rect = self.top_shape.copy()

    def draw(self, screen, zoom=1.0):
        shadow_rect = self.rect.copy()
        shadow_rect.y += int(5 * zoom)
        radius = int(10 * zoom)
        pygame.draw.rect(screen, self.bottom_colour, shadow_rect, border_radius=radius)
        pygame.draw.rect(screen, self.top_colour, self.rect, border_radius=radius)

    def draw_attachment(self, screen, zoom, state):
        width = int(45 * zoom)
        height = int(35 * zoom)
        x = self.rect.centerx - (width // 2)
        y = self.rect.top - int(25 * zoom)

        attachment_rect = pygame.Rect(x, y, width, height)
        shadow_rect = pygame.Rect(x, y + 2, width, height)
        pygame.draw.rect(screen, self.bottom_colour, shadow_rect, border_radius=5)
        pygame.draw.rect(screen, self.top_colour, attachment_rect, border_radius=5)

        self.light.draw(screen, attachment_rect.centerx, attachment_rect.centery, int(6 * zoom), state)


class ScreenDisplay:
    def __init__(self, display_colour, rim_colour, fixed_height=None):
        self.display_colour = display_colour
        self.rim_colour = rim_colour
        self.fixed_height = fixed_height
        self.center = (0, 0)
        self.rim_rect = None
        self.display_rect = None

    def draw(self, screen, box):
        zoom = box.rect.width / box.top_shape.width

        if self.fixed_height:
            height = self.fixed_height * zoom
        else:
            height = box.top_shape.height * zoom

        rim_margin = 10 * zoom
        self.rim_rect = pygame.Rect(
            box.rect.left + rim_margin,
            box.rect.top + rim_margin,
            box.rect.width - 2 * rim_margin,
            height - 2 * rim_margin
        )
        pygame.draw.rect(screen, self.rim_colour, self.rim_rect, border_radius=int(10 * zoom))

        inner_margin = 5 * zoom
        self.display_rect = pygame.Rect(
            self.rim_rect.left + inner_margin,
            self.rim_rect.top + inner_margin,
            self.rim_rect.width - 2 * inner_margin,
            self.rim_rect.height - 2 * inner_margin
        )
        pygame.draw.rect(screen, self.display_colour, self.display_rect, border_radius=int(8 * zoom))
        self.center = self.rim_rect.center


class DefuseButton:
    def __init__(self, radius, relative_pos, top_colour, bottom_colour):
        self.radius = radius
        self.relative_pos = relative_pos
        self.top_colour = top_colour
        self.bottom_colour = bottom_colour
        self.center = (0, 0)

    def draw(self, screen, box):
        box_x, box_y = box.rect.center
        self.center = (box_x + self.relative_pos[0], box_y + self.relative_pos[1])

        shadow_center = (self.center[0], self.center[1] + 5)
        pygame.draw.circle(screen, self.bottom_colour, shadow_center, self.radius)
        pygame.draw.circle(screen, self.top_colour, self.center, self.radius)

    def is_clicked(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        return (dx ** 2 + dy ** 2) <= self.radius ** 2