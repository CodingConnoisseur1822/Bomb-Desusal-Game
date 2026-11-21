import random
import pygame
import settings as S
from Audio import Audio
from ColourGameConfig import ColourLED, ColourSwitch

COLOURS = ["Red", "Green", "Blue", "Yellow"]


class ColourGame:
    def __init__(self, grey_box, background_colour):
        self.grey_box = grey_box
        self.background_colour = background_colour
        self.is_active = False
        self.is_finished = False
        self.score = 0
        self.target_score = 0

        self.sounds = [Audio(883, 0.3), Audio(659, 0.3), Audio(554, 0.3), Audio(440, 0.3)]
        self.wrong_sound = Audio(200, 0.3)

        self.leds = []
        self.switches = []
        for colour in COLOURS:
            led = ColourLED("images/" + colour + "-On.png", "images/" + colour + "-Off.png")
            switch = ColourSwitch("images/On-Switch.png", "images/Off-Switch.png", led)
            self.leds.append(led)
            self.switches.append(switch)

        self.reset_round()

    def start(self):
        self.is_active = True
        self.is_finished = False
        self.score = 0
        self.target_score = random.randint(S.COLOUR_ROUNDS_MIN, S.COLOUR_ROUNDS_MAX)
        self.reset_round()

    def stop(self):
        self.is_active = False
        self.is_finished = True

    def reset_round(self):
        self.pattern = []
        self.current_step = 0
        self.pattern_index = 0
        self.showing_pattern = False
        self.waiting_input = False
        self.active_switch = None
        self.led_timer = 0
        self.pattern_timer = pygame.time.get_ticks()

        for switch in self.switches:
            switch.turn_off()

    def handle_event(self, pos):
        if not self.is_active or self.is_finished or not self.waiting_input:
            return

        for switch in self.switches:
            if switch.clicked(pos):
                self.check_switch(switch)
                break

    def check_switch(self, switch):
        if switch != self.pattern[self.current_step]:
            self.wrong_sound.play()
            self.reset_round()
            return

        self.light_switch(switch)
        self.current_step += 1

        if self.current_step < len(self.pattern):
            return

        self.score += 1
        self.current_step = 0
        self.waiting_input = False

        if self.score >= self.target_score:
            Audio.play_victory()
            self.is_finished = True
            self.active_switch = None
            for other_switch in self.switches:
                other_switch.turn_off()
        else:
            self.pattern_timer = pygame.time.get_ticks() + S.COLOUR_NEXT_ROUND_DELAY

    def light_switch(self, switch):
        index = self.switches.index(switch)
        self.sounds[index].play()
        switch.light_up()
        self.active_switch = switch
        self.led_timer = pygame.time.get_ticks() + S.COLOUR_LED_TIME

    def update(self):
        if not self.is_active or self.is_finished:
            return

        now = pygame.time.get_ticks()

        if self.active_switch is not None and now > self.led_timer:
            self.active_switch.turn_off()
            self.active_switch = None

        if not self.waiting_input and not self.showing_pattern:
            if now > self.pattern_timer:
                self.pattern.append(random.choice(self.switches))
                self.showing_pattern = True
                self.pattern_index = 0
                self.pattern_timer = now

        if self.showing_pattern and now > self.pattern_timer + S.COLOUR_SHOW_DELAY:
            if self.pattern_index < len(self.pattern):
                self.light_switch(self.pattern[self.pattern_index])
                self.pattern_index += 1
                self.pattern_timer = now
            else:
                self.showing_pattern = False
                self.waiting_input = True

    def draw(self, screen):
        screen.fill(self.background_colour)
        self.grey_box.draw(screen, zoom=S.COLOUR_GAME_ZOOM)

        total_width = (len(self.leds) - 1) * S.LED_SPACING + S.LED_SLOT_SIZE
        start_x = self.grey_box.rect.centerx - (total_width // 2)
        led_y = self.grey_box.rect.top + S.COLOUR_TOP_MARGIN
        switch_y = led_y + S.LED_SLOT_SIZE + S.COLOUR_SWITCH_GAP

        for i in range(len(self.leds)):
            x = start_x + i * S.LED_SPACING

            self.leds[i].x = x
            self.leds[i].y = led_y
            self.leds[i].draw(screen)

            self.switches[i].x = x
            self.switches[i].y = switch_y
            self.switches[i].draw(screen)