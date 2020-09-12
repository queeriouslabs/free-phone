import RPi.GPIO as GPIO
import threading
import time

import tonegenerator as tg


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
        self.tone_mode = 'normal'
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
        self.callback = None

        # GPIO init
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(Keypad.COLS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(Keypad.ROWS, GPIO.OUT)

        GPIO.output(Keypad.ROWS, GPIO.LOW)

        # Tone Generator

        self.tone_generator = tg.ToneGenerator()
        self.tone_generator.start()

    def set_tone_mode(self, new_mode):
        if new_mode in ['normal', 'deusex']:
            self.tone_mode = new_mode

    def has_pressed(self):
        for key in self.keypad_state:
            if self.keypad_state[key]:
                return True

        return False

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

    def start(self):
        def daemon():
            while True:
                self.read_keypad()
                delta = self.compute_keypad_delta()
                for key in delta:
                    self.handle(key, delta[key])

                if len(delta) > 0:
                    self.play_tones(
                        [key for key in self.keypad_state if self.keypad_state[key]])
                time.sleep(0.001)

        thread = threading.Thread(target=daemon)
        thread.daemon = True
        thread.start()

    def set_callback(self, callback):
        self.callback = callback

    def handle(self, key, event):
        self.keypad_state[key] = event == 'key_down'
        if self.callback is not None:
            self.callback(key, event)

    deusex_remap = {
        '1': '9',
        '2': '6',
        '3': '5',
        '4': '7',
        '5': '1',
        '6': '5',
        '7': '3',
        '8': '6',
        '9': '1',
        '*': '8',
        '0': '4',
        '#': '5'
    }

    def play_tones(self, keys):
        tones = []

        if self.tone_mode == 'normal':
            for key in self.keypad_state:
                if self.keypad_state[key]:
                    tones += tg.ToneGenerator.dtmf_key(key)

        elif self.tone_mode == 'deusex':
            for key in self.keypad_state:
                if self.keypad_state[key]:
                    tones += tg.ToneGenerator.dtmf_key(
                        Keypad.deusex_remap[key])

        self.tone_generator.set_tones(list(set(tones)))


if __name__ == '__main__':
    keypad = Keypad()
    keypad.start()
    keypad.set_tone_mode('deusex')

    def cb(key, event):
        print([key for key in keypad.keypad_state if keypad.keypad_state[key]])
    keypad.set_callback(cb)
    while True:
        print('tick')
        time.sleep(10)
