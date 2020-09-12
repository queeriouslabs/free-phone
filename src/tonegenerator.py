import datetime
import math
import numpy
import struct
from subprocess import Popen, PIPE, STDOUT
import threading
import time


class ToneGenerator(object):
    def __init__(self):
        self.sample_rate = 0
        self.current_time = 0
        self.tones = []
        self.aplay = None
        self.running = False

    def set_tones(self, tones):
        self.tones = tones

    def value_at_time(self, t):
        val = 0
        for freq, shape in self.tones:
            if shape == 'sine':
                val += ToneGenerator.sine_value_at_time(t, freq)
            elif shape == 'square':
                val += ToneGenerator.square_value_at_time(t, freq)
            elif shape == 'thin-square':
                val += ToneGenerator.thin_square_value_at_time(t, freq)
            else:
                pass
        return val

    @staticmethod
    def sine_value_at_time(t, freq):
        return math.sin(2 * math.pi * freq * t)

    @staticmethod
    def square_value_at_time(t, freq):
        if ToneGenerator.sine_value_at_time(t, freq) >= 0:
            return 1
        else:
            return -1

    @staticmethod
    def thin_square_value_at_time(t, freq):
        if ToneGenerator.sine_value_at_time(t, freq) >= 0.5:
            return 1
        else:
            return -1

    def start(self):
        sample_rate = 48000
        self.aplay = Popen(['aplay', '-c', '1', '-t', 'raw',
                            '-r', str(sample_rate), '-f', 'FLOAT_LE'],
                           stdin=PIPE)

        def daemon():
            time_zero = datetime.datetime.now()
            total_buffered = 0
            refresh_time = 0.001
            max_buffer = 3 * refresh_time

            t = 0
            dt = 1 / sample_rate
            while self.running:
                time_delta = (datetime.datetime.now() -
                              time_zero).total_seconds()
                remaining_buffer = total_buffered - time_delta
                generate_time = max_buffer - remaining_buffer
                generate_samples = int(generate_time / dt)
                total_buffered += generate_time

                self.aplay.stdin.write(struct.pack(
                    '<%if' % generate_samples, *[self.value_at_time(t + i * dt)
                                                 for i in range(generate_samples)]))

                t += generate_samples * dt
                time.sleep(refresh_time)

        self.thread = threading.Thread(target=daemon)
        self.thread.daemon = True
        self.running = True
        self.thread.start()

    def stop(self):
        self.aplay.terminate()
        self.aplay = None
        self.running = False

    @staticmethod
    def dtmf_key(key):
        dtmf_info = {
            '1': (697, 1209),
            '2': (697, 1336),
            '3': (697, 1477),
            'a': (697, 1633),
            '4': (770, 1209),
            '5': (770, 1336),
            '6': (770, 1477),
            'b': (770, 1633),
            '7': (852, 1209),
            '8': (852, 1336),
            '9': (852, 1477),
            'c': (852, 1633),
            '*': (941, 1209),
            '0': (941, 1336),
            '#': (941, 1477),
            'd': (941, 1633)
        }

        row, col = dtmf_info[key]
        return [(row, 'sine'), (col, 'sine')]


if __name__ == '__main__':
    tg = ToneGenerator()
    tg.start()

    tg.set_tones([(2600, 'sine')])
    time.sleep(10)

    # for c in '04511337':
    #     tg.set_tones(ToneGenerator.dtmf_key(c))
    #     time.sleep(0.2)
    #     tg.set_tones([])
    #     time.sleep(0.1)

    tg.stop()
