# Interactive Bomb Defusal Game

A Python and PyGame puzzle game made as a first year project for uni. You've got five minutes to work through a set of mini-games on a bomb, find the right wires and cut them before the timer runs out. One wrong cut and it's game over.

The fun part: it's designed to be played on a **Raspberry Pi with real buttons and LEDs**, not just a keyboard. Five physical buttons move the on-screen cursor and click, and three LEDs on a breadboard light up during the wire-cutting stage to tell you when it's safe to cut. If you don't have a Pi handy, there's a keyboard mode so you can still play (and test) on any computer.

Built as a team project in a group of 3.

## How the game works

The bomb has four wires (red, blue, green, yellow) and four modules. To defuse it you cut every wire, one at a time, in a random order.

1. Press the big red button. One of the modules starts flashing its light, which means that's the one you need to solve.
2. Click into that module and complete the puzzle. Its light turns green when you're done.
3. Press the red button again for the next module. The number of modules you need to solve goes up with each wire (1, then 2, then 3, then 3).
4. Once you've solved enough modules, press the red button to reveal which wire to cut.
5. Go into the wire module and hover the cursor over the correct wire. The LEDs step through **red, then yellow, then blue**. You have to click to cut while the **blue** LED is on. Cut too early or cut the wrong wire and the bomb goes off.
6. Cut all four wires before the timer hits zero and you win.

### The modules

| Module | What you do |
| --- | --- |
| **Arrow sequence** | Arrows appear on screen working outwards from the middle. Once they've all appeared, press the matching arrow keys/buttons in order from left to right. A mistake resets the round, and you need to clear three rounds. |
| **Colour memory** | A Simon-style game. Four coloured LEDs flash in a growing pattern and you click the matching switches back in the same order. |
| **Numpad recall** | A short sequence of digits is flashed one at a time. Remember it, type it on the on-screen keypad, then hit `E` to submit (`<` deletes). |
| **Wire cutting** | The final stage for each wire, using the hover-and-LED timing described above. |

## Hardware (Raspberry Pi mode)

Everything is read and driven through [gpiozero](https://gpiozero.readthedocs.io/). The pins below use BCM numbering and are all set in `settings.py`, so they're easy to change if your wiring is different.

| Part | GPIO pin |
| --- | --- |
| Right button | 17 |
| Left button | 24 |
| Down button | 25 |
| Up button | 8 |
| Interact (click) button | 22 |
| Red LED | 7 |
| Yellow LED | 14 |
| Blue LED | 27 |

The LED timing during wire cutting is based on how long you keep the cursor on the right wire: red for the first second, yellow up to two seconds, blue from two to four seconds. After four seconds it resets and you have to start hovering again.

A nice side effect of the design is that all hardware input goes through a small controls interface (`controls.py`). It hands back either `PiControls` (real buttons and LEDs) or `KeyboardControls` (keyboard, LEDs do nothing), and the rest of the game doesn't know or care which one it's talking to.

## Running it

**Requirements:** Python 3, `pygame` and `numpy`. On a Raspberry Pi you'll also want `gpiozero`.

```bash
pip install pygame numpy
# on the Raspberry Pi only:
pip install gpiozero
```

**Keyboard mode (default):**

```bash
python Game.py
```

| Key | Action |
| --- | --- |
| Arrow keys | Move the cursor (and answer the arrow module) |
| Space | Click |

**Raspberry Pi mode:** open `settings.py`, set `USE_KEYBOARD = False`, wire up the buttons and LEDs to the pins above, and run the same command.

The game expects an `images/` folder next to the code (module covers, LED and switch graphics, wire pictures, cursor and explosion image). The timer also looks for the `DS-Digital` font and falls back to a default if it isn't installed.

## Project structure

```
Game.py            Main game loop, state machine and drawing
settings.py        All the tweakable numbers: pins, colours, sizes, timings
controls.py        Picks keyboard or Pi controls
keyboard_controls.py / pi_controls.py
design.py          Boxes, screen displays, the red button, the cursor
ArrowGame.py       Arrow sequence module
ColourGame.py      Colour memory module (with ColourGameConfig.py)
NumPad.py          Numpad recall module
Wires.py           Wire cutting module and LED timing
digital_timer.py   Countdown timer
endgame.py         Win / explosion screen
Audio.py           Sound effects generated in code with NumPy
```

All the sound effects are generated from sine waves with NumPy, so there are no audio files to ship.

## What I want to do next

This is a project I'm still keen to keep building on. The main things on my list:

- **A better-looking UI.** The current look is functional but pretty plain, since everything is drawn with PyGame shapes. I'd like to add proper artwork, smoother animations (buttons, wires snapping, the explosion), a main menu and a more polished win/lose screen.
- **A database for wins and losses.** I want to store every game's result, time remaining and which module caused a failure, so there's a history to look back on. Something like SQLite to start with, then a simple stats screen showing win rate and best times.
- **More Raspberry Pi hardware.** There's a lot more I could do with the GPIO side: a physical buzzer for the countdown that speeds up as time runs low, an LCD or 7-segment display for the timer, a physical switch or keypad for some of the modules, and a proper case so it feels like an actual bomb.
- **More modules and difficulty levels**, so every game feels a bit different.

## Author

Eduard-Alexandru Idu,
