import os
import pyttsx3
import re
import threading
import subprocess
import time

import keypad
import tonegenerator as tg


class InvalidRoute(Exception):
    def __init__(self, path):
        self.path = path


class MissingResponseCode(Exception):
    def __init__(self, path):
        self.path = path


def prefix(a, b):
    return a[:len(b)] == b or b[:len(a)] == a


class Phreak(object):

    route_pattern = re.compile('^\\/(\d+(\\/\d+)*\\/?)?$')
    phone_number_pattern = re.compile('^\d\d\d\d\d\d\d(\d\d\d(\d))?')
    path_part_pattern = re.compile('^\d+$')

    def __init__(self, keypad_read_timeout=1.5):
        self.routes = {
            'parts': {}
        }
        self.debug_mode = os.environ.get('PHREAK_ENVIRONMENT')

        self.dialtone = None
        self.ringing_tone = None
        self.mode = 'normal'

        self.keypad_read_timeout = keypad_read_timeout

        self.keypad = keypad.Keypad()
        self.keypad.set_callback(self.handle)
        self.keypad.start()

        self.listening = False
        self.keypad_buffer = ''
        self.listen_timer = None

        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 175)
        self.tts.setProperty('volume', 3.0)

    def say(self, s=''):
        print(s)
        if not self.debug_mode == 'shell' and s != '':
            self.tts.say(s)
            self.tts.runAndWait()

    def debug(self, s=''):
        if self.debug_mode is not None:
            self.say(s)

    def listen(self, prompt):
        if self.debug_mode == 'shell':
            return input(prompt)
        else:
            print('Listening')
            self.listening = True
            self.keypad_buffer = ''
            while self.listening:
                time.sleep(0.01)
            print('Read: ' + self.keypad_buffer)
            time.sleep(0.5)
            return self.keypad_buffer

    def play_2600_chirp(self):
        subprocess.Popen(['aplay', '2600_chirp.wav'])

    def play_triple_dialtone_buzz(self):
        subprocess.Popen(['aplay', 'triple_dialtone_buzz.wav'])

    def set_keypad_tone_mode(self, tone_mode):
        self.keypad.set_tone_mode(tone_mode)

    def end_listen(self):
        self.listening = False
        print('End Listening')

    def handle(self, key, event):
        if self.mode == 'normal' and self.dialtone is not None:
            self.dialtone.kill()
            self.dialtone = None

        if event == 'key_down':
            self.keypad_buffer += key

        if self.listen_timer is not None:
            self.listen_timer.cancel()

        if not self.keypad.has_pressed():
            self.listen_timer = threading.Timer(
                self.keypad_read_timeout, self.end_listen)
            self.listen_timer.start()

    def route(self, number):
        def decorator(handler):
            self.add_route(number, handler)

        return decorator

    def add_route(self, route, handler):
        parts = self.normalize_route(route)
        if parts is None:
            raise InvalidRoute(route)

        self.insert_route(parts, handler)

    def insert_route(self, parts, handler):
        node = self.routes
        for part in parts:
            if part not in node['parts']:
                node['parts'][part] = {'parts': {}, 'handler': (lambda: None)}
            node = node['parts'][part]

        node['handler'] = handler

    def normalize_route(self, route):
        if re.match(Phreak.route_pattern, route) is None:
            return None
        else:
            parts = route[1:].split('/')
            if parts[-1] == '':
                parts = parts[:-1]
            return parts

    def lookup_route(self, parts):
        node = self.routes
        for part in parts:
            if part not in node['parts']:
                return None
            node = node['parts'][part]

        return node['handler']

    def run(self):
        current_path = None
        next_path = []
        last_dialed = None

        while True:
            time.sleep(0.1)

            if self.mode == 'normal':

                if self.dialtone is None:
                    self.dialtone = subprocess.Popen(['aplay', 'dialtone.wav'])

                    def dialtone_restart():
                        if self.dialtone:
                            self.dialtone.kill()
                            self.dialtone = subprocess.Popen(
                                ['aplay', 'dialtone.wav'])
                            to = threading.Timer(10, dialtone_restart)
                            to.daemon = True
                            to.start()
                    to = threading.Timer(10, dialtone_restart)
                    to.daemon = True
                    to.start()

                self.debug()
                self.debug('Please enter a number to dial.')
                dialed = self.listen('> ')

                if re.match(Phreak.phone_number_pattern, dialed) is not None:
                    self.play_2600_chirp()
                    time.sleep(0.5)
                    self.debug('Dialing ' + dialed)
                    last_dialed = dialed
                    self.mode = 'call'
                elif dialed == '*69':
                    if last_dialed == '':
                        self.play_triple_dialtone_buzz()
                    elif last_dialed is not None:
                        for c in last_dialed:
                            self.keypad.tone_generator.set_tones(
                                tg.ToneGenerator.dtmf_key(c))
                            time.sleep(0.1)
                            self.keypad.tone_generator.set_tones([])
                            time.sleep(0.05)
                        self.mode = 'call'
                elif dialed == '*':
                    self.play_2600_chirp()
                    time.sleep(0.5)
                    self.mode = 'star_menu'
                else:
                    self.play_triple_dialtone_buzz()
                    time.sleep(1)
                    self.debug('ERROR Invalid Number: ' + dialed)

            elif self.mode == 'call':
                if self.ringing_tone is None:
                    self.ringing_tone = subprocess.Popen(
                        ['aplay', 'ringing_tone.wav'])

                    time.sleep(12)
                    self.ringing_tone.kill()
                    self.play_triple_dialtone_buzz()
                    time.sleep(1)
                    self.mode = 'normal'
                    self.ringing_tone = None

            elif self.mode == 'star_menu':

                if next_path is not None:
                    # request
                    self.debug()
                    self.debug('< GET /' + '/'.join(next_path))
                    response = self.get_route(next_path)

                    redirect_or_prompt = None
                    if response == 404:
                        redirect_or_prompt = 'prompt'

                    elif isinstance(response, tuple) and response[0] == 302:
                        redirect_or_prompt = 'redirect'

                        new_path_parts = response[1]
                        if new_path_parts[0] == '/':
                            redirect = new_path_parts[1:].split('/')
                        else:
                            redirect = current_path + \
                                new_path_parts.split('/')
                        if redirect[-1] == '':
                            redirect = redirect[:-1]

                    elif response == 200:
                        current_path = next_path
                        redirect_or_prompt = 'prompt'

                    if redirect_or_prompt == 'redirect':
                        next_path = redirect
                    elif redirect_or_prompt == 'prompt':
                        # self.debug('Current path: ' + ('/' + '/'.join(current_path)
                        #                              if current_path is not None else 'none'))
                        while True:
                            dialed = self.listen('> ')

                            if dialed == '':
                                continue
                            elif re.match(Phreak.path_part_pattern, dialed):
                                next_path = current_path + [dialed]
                                if self.lookup_route(next_path) is None:
                                    self.play_triple_dialtone_buzz()
                                else:
                                    self.play_2600_chirp()
                                    time.sleep(0.5)

                                break
                            else:
                                self.debug('ERROR Invalid Menu: ' + dialed)
                                self.play_triple_dialtone_buzz()

    def get_route(self, route):
        handler = self.lookup_route(route)
        if handler is None:
            return 404
        else:
            response = handler()
            if response is None:
                return 200
            return response


if __name__ == '__main__':
    app = Phreak()

    @app.route('/')
    def root():
        app.say('Hello!')

    @app.route('/338739')
    def deusex():
        app.say('I definitely asked for this')
        app.set_keypad_tone_mode('deusex')

    @app.route('/338739/0451')
    def deusex_0451():
        app.say('What a shame.')
        pass

    @app.route('/1337')
    def hacker():
        app.say('Hack the planet!')
        return 302, '/'

    app.run()
