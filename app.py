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

Window.size = (600, 400)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

class Start_Window(Screen):
    pass

class Window_DateInfo(Screen):
    origin = ObjectProperty(None)
    destination = ObjectProperty(None)
    count = sort_foto.Data_info()
    
    def set_destination(self):
        self.destination = r"C:\Users\Rasmus\Desktop\Rasmus\Photos"
        self.ids.l_date_dest_filepath.text = self.destination
        
    def set_origin(self):
        self.origin = r"C:\Users\Rasmus\Desktop\Rasmus\Fotos\Smartphone\Mi 9 SE"
        self.ids.l_date_origin_filepath.text = self.origin
        
    def date_startparse(self):
        sort_foto.parse_fotos(self.origin, self.destination, self.count)
        print("Images", self.count.count_images)
        print("GPS", self.count.count_gps)
        print(int(self.count.memory_size_MB),"MB Memory copied")
        print("Videos:",self.count.count_videos)
        print("Exif_date exists",self.count.count_date)
        print("No Exif Date",self.count.count_noexif_date)
        print("No Exif",self.count.count_noexif)

class Window_SortDate(Screen):
    pass
#    def date_startsort(self):
#        sort_foto.build_folder_structure(self.destination, self.count.dict_years,self.count.list_years_videos)
#        sort_foto.copy_file_date(self.count)

class Window_LocationInfo(Screen):
    pass


class Window_SearchInfo(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("sort.kv")
sm = WindowManager()

screens = [Start_Window(name="start"), Window_DateInfo(name="dateinfo"), Window_SortDate(name="sortdate"),
           Window_LocationInfo(name="locationinfo"), Window_SearchInfo(name="searchinfo")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "start"


class SortApp(App):
    def build(self):
        return kv

    
if __name__ == '__main__':
    SortApp().run()

