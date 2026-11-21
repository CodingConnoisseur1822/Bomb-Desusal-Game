import pygame
import settings as S


class BoomScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.boom_image = pygame.image.load("images/boom.jpg").convert()
        self.boom_image = pygame.transform.scale(self.boom_image, (S.SCREEN_WIDTH, S.SCREEN_HEIGHT))

        self.title_font = pygame.font.SysFont("Consolas", 50, bold=True)
        self.button_font = pygame.font.SysFont("Consolas", 30, bold=True)

        self.overlay = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        middle_x = S.SCREEN_WIDTH // 2
        middle_y = S.SCREEN_HEIGHT // 2
        self.restart_rect = pygame.Rect(0, 0, 220, 70)
        self.restart_rect.center = (middle_x, middle_y + 20)
        self.quit_rect = pygame.Rect(0, 0, 220, 70)
        self.quit_rect.center = (middle_x, middle_y + 110)

    def display(self, cursor, controls, is_victory):
        if is_victory:
            title_text = "BOMB DEFUSED"
            title_colour = (100, 255, 100)
            hover_colour = (0, 150, 0)
        else:
            title_text = "BOMB DETONATED"
            title_colour = (255, 50, 50)
            hover_colour = (180, 0, 0)

        title_surface = self.title_font.render(title_text, True, title_colour)
        title_rect = title_surface.get_rect(center=(S.SCREEN_WIDTH // 2, S.SCREEN_HEIGHT // 2 - 100))

        while True:
            self.clock.tick(S.FPS)
            controls.update()
            pos = cursor.get_pos()

            if is_victory:
                self.screen.fill((20, 60, 20))
            else:
                self.screen.blit(self.boom_image, (0, 0))
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(title_surface, title_rect)

            for rect, text in [(self.restart_rect, "RESTART"), (self.quit_rect, "QUIT")]:
                if rect.collidepoint(pos):
                    colour = hover_colour
                else:
                    colour = (60, 60, 60)

                pygame.draw.rect(self.screen, colour, rect, border_radius=15)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 3, border_radius=15)
                text_surface = self.button_font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, text_surface.get_rect(center=rect.center))

            if controls.just_pressed("interact"):
                if self.restart_rect.collidepoint(pos):
                    return "RESTART"
                if self.quit_rect.collidepoint(pos):
                    return "QUIT"

            move_x = (controls.is_down("right") - controls.is_down("left")) * S.CURSOR_SPEED
            move_y = (controls.is_down("down") - controls.is_down("up")) * S.CURSOR_SPEED
            cursor.update(move_x, move_y)
            cursor.draw(self.screen)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"