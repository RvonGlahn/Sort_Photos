'''
Boxen um Buttons für Padding 
Windows


'''
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser

Window.size = (600, 400)
Window.clearcolor = (1, 1, 1, 1)

class Start_Window(Widget):

    def btn(self):
        print("Name:")




class SortApp(App):
    def build(self):
        return Start_Window()

    
if __name__ == '__main__':
    SortApp().run()

