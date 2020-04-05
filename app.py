'''
Boxen um Buttons für Padding 
Windows für alle Funktionen
round buttons

'''
import os
import kivy
import sort_foto
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser

Window.size = (500, 300)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

class Start_Window(Screen):
    origin = ObjectProperty(None)
    destination = ObjectProperty(None)
    search = ObjectProperty(None)


class Window_DateInfo(Screen):
    origin = ObjectProperty(None)
    destination = ObjectProperty(None)
    
    def date_startparse(self):
        count = sort_foto.Data_info()
        sort_foto.parse_fotos(self.origin, self.destination, count)


class Window_LocationInfo(Screen):
    pass


class Window_SearchInfo(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("sort.kv")
sm = WindowManager()

screens = [Start_Window(name="start"), Window_DateInfo(name="dateinfo"),Window_LocationInfo(name="locationinfo"),
           Window_SearchInfo(name="searchinfo")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "start"


class SortApp(App):
    def build(self):
        return kv

    
if __name__ == '__main__':
    SortApp().run()

