import math
import numpy
import pygame

pygame.mixer.init(44100, -16, 2)

SAMPLE_RATE = 44100
MAX_VOLUME = 2 ** 15 - 1


class Audio:
    def __init__(self, frequency, duration):
        total_samples = int(duration * SAMPLE_RATE)
        times = numpy.arange(total_samples) / SAMPLE_RATE
        wave = MAX_VOLUME * numpy.sin(2 * math.pi * frequency * times)
        wave = wave.astype(numpy.int16)
        data = numpy.column_stack((wave, wave))
        self.sound = pygame.sndarray.make_sound(data)

    def play(self):
        channel = pygame.mixer.find_channel(True)
        channel.play(self.sound)

    @staticmethod
    def play_victory():
        notes = [(800, 0.08, 120), (1200, 0.06, 100), (1800, 0.05, 300)]
        for repeat in range(2):
            for frequency, duration, pause in notes:
                Audio(frequency, duration).play()
                pygame.time.delay(pause)