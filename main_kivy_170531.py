from kivy.config import Config
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '150')

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.app import App


Builder.load_string('''
#:kivy 1.8.0

<KivyTimer>:
    BoxLayout:
        orientation: 'vertical'
        pos: root.pos
        size: root.size

        Label:
            text: str(root.left_time)
            font_size: 100
            
        Label:
            text: str(root.text_a)
            font_size: 100
            
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1.0, 0.3

            Button:
                text: '+1 minute'
                font_size: 16
                on_press: root.on_command('+1 minute')

            Button:
                text: 'Stop' if root.is_countdown else 'Start'
                font_size: 16
                on_press: root.on_command('start/stop')

            Button:
                text: 'Reset'
                font_size: 16
                on_press: root.on_command('reset')
''')


class KivyTimer(Widget):
    is_countdown = BooleanProperty(False)
    left_time = NumericProperty(0)
    text_a = "hello"

    def on_command(self, command):
        if command == '+1 minute':
            self.left_time += 60
        elif command == 'start/stop':
            if self.is_countdown:
                self.stop_timer()
            elif self.left_time > 0:
                self.start_timer()
        elif command == 'reset':
            self.stop_timer()
            self.left_time = 0

    def on_countdown(self, dt):
        self.left_time -= 1
        if self.left_time == 0:
            self.is_countdown = False
            return False

    def start_timer(self):
        self.is_countdown = True
        Clock.schedule_interval(self.on_countdown, 1.0)
        pass

    def stop_timer(self):
        self.is_countdown = False
        Clock.unschedule(self.on_countdown)
        pass


class KivyTimerApp(App):
    def build(self):
        return KivyTimer()


if __name__ == '__main__':
    KivyTimerApp().run()
