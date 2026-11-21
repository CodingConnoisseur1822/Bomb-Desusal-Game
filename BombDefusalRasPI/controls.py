import settings as S

def make_controls():
    if S.USE_KEYBOARD:
        from keyboard_controls import KeyboardControls
        return KeyboardControls()

    from pi_controls import PiControls
    return PiControls()