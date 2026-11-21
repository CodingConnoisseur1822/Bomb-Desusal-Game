import pygame
import settings as S


class DigitalTimer:
    def __init__(self, start_seconds, font_size, timer_display):
        self.start_seconds = start_seconds
        self.timer_display = timer_display
        self.frame_count = 0
        self.font = pygame.font.SysFont("DS-Digital", font_size, True, True)

    def update(self):
        if self.get_remaining_seconds() > 0:
            self.frame_count += 1

    def get_remaining_seconds(self):
        remaining = self.start_seconds - (self.frame_count // S.FPS)
        return max(0, remaining)

    def draw(self, screen):
        total_seconds = self.get_remaining_seconds()
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"{minutes:02}:{seconds:02}"

        text_surface = self.font.render(time_text, True, S.TIMER_TEXT_COLOUR)
        text_rect = text_surface.get_rect(center=self.timer_display.display_rect.center)
        screen.blit(text_surface, text_rect)