import kivy

kivy.require('2.0.0')

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class Shared:

    def __init__(self):
        self.username = ''
        self.login = None
        self.create = None
        self.main = None
        self.account = None
        self.user_events = None
        self.event_create = None
        self.public_event_search = None
        self.private_event_search = None
        self.app = None
        self.sm = None
        self.nm = None

    def popup_widget(self, popup_label, popup_title, close_button_label='Dismiss'):
        layout = BoxLayout(orientation='vertical')
        popup_content = Label(text=f'{popup_label}',
                              valign='center', halign='center')
        close_button = Button(text=f'{close_button_label}',
                              size_hint=(None, None), size=(80, 40),
                              pos_hint={'center_x': 0.5, 'center_y': 0.5})
        layout.add_widget(popup_content)
        layout.add_widget(close_button)
        popup = Popup(title=f'{popup_title}', title_align='center',
                      content=layout,
                      size_hint=(None, None), size=(300, 200),
                      auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()
