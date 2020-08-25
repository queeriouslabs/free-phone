import RPi.GPIO as GPIO
import time


class Keypad:
    buttons = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['*', '0', '#']
    ]

    COLS = [7, 8, 10]
    ROWS = [12, 16, 18, 22]

    def __init__(self):
        self.callback = None
        self.keypad_history = {
            '1': 10 * [0],
            '2': 10 * [0],
            '3': 10 * [0],
            '4': 10 * [0],
            '5': 10 * [0],
            '6': 10 * [0],
            '7': 10 * [0],
            '8': 10 * [0],
            '9': 10 * [0],
            '*': 10 * [0],
            '0': 10 * [0],
            '#': 10 * [0]
        }
        self.keypad_state = {
            '1': False,
            '2': False,
            '3': False,
            '4': False,
            '5': False,
            '6': False,
            '7': False,
            '8': False,
            '9': False,
            '*': False,
            '0': False,
            '#': False
        }

        # GPIO init
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(Keypad.COLS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(Keypad.ROWS, GPIO.OUT)

        GPIO.output(Keypad.ROWS, GPIO.LOW)

    def set_callback(self, callback):
        self.callback = callback

    def read_keypad(self):
        for row in range(len(Keypad.ROWS)):
            GPIO.output(Keypad.ROWS[row], GPIO.HIGH)
            for col in range(len(Keypad.COLS)):
                button = Keypad.buttons[row][col]
                self.keypad_history[button].append(
                    GPIO.input(Keypad.COLS[col]))
            GPIO.output(Keypad.ROWS[row], GPIO.LOW)

    def compute_keypad_delta(self):
        delta = {}

        for key in self.keypad_state:
            state = self.keypad_state[key]
            samples = self.key_sample_count(key)

            if not state and samples >= 8:
                delta[key] = 'key_down'
            elif state and samples <= 2:
                delta[key] = 'key_up'

        return delta

    def key_sample_count(self, key):
        return sum(self.keypad_history[key][-10:])

    def polling_loop(self):
        while True:
            self.read_keypad()
            delta = self.compute_keypad_delta()
            # print(self.keypad_history['1'])
            for key in delta:
                self.keypad_state[key] = delta[key] == 'key_down'
                if self.callback is not None:
                    self.callback(key, delta[key])
            time.sleep(0.001)
