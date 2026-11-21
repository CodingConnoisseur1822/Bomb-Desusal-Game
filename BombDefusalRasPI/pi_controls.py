from gpiozero import Button, LED
import settings as S


class PiControls:
    def __init__(self):
        self.buttons = {
            "right": Button(S.RIGHT_BUTTON_PIN),
            "left": Button(S.LEFT_BUTTON_PIN),
            "interact": Button(S.INTERACT_BUTTON_PIN),
            "down": Button(S.DOWN_BUTTON_PIN),
            "up": Button(S.UP_BUTTON_PIN)
        }
        self.current = {}
        self.previous = {}
        for name in self.buttons:
            self.current[name] = False
            self.previous[name] = False

        self.leds = [LED(S.RED_LED_PIN), LED(S.YELLOW_LED_PIN), LED(S.BLUE_LED_PIN)]

    def update(self):
        for name in self.buttons:
            self.previous[name] = self.current[name]
            self.current[name] = self.buttons[name].is_pressed

    def is_down(self, name):
        return self.current[name]

    def just_pressed(self, name):
        return self.current[name] and not self.previous[name]

    def set_led(self, led_index):
        for i in range(len(self.leds)):
            self.leds[i].value = (i == led_index)