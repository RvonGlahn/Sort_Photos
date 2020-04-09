'''
Windows für alle Funktionen
try except mit Pop.up für leere pfade
filechooser
datepicker
count reset für go back 
progress bar für copy
'''
import os
import kivy
import GlobalVar
import sort_foto
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser

Window.size = (600, 400)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

origin = ObjectProperty(None)
destination = ObjectProperty(None)
count = sort_foto.Data_info()


class Start_Window(Screen):
    pass


class Window_DateInfo(Screen):
    
    def set_destination(self):
        global destination
        destination = r"C:\Users\Rasmus\Desktop\Rasmus\Photos"
        self.ids.l_date_dest_filepath.text = destination
        
    def set_origin(self):
        global origin
        origin = r"C:\Users\Rasmus\Desktop\Rasmus\Fotos\Smartphone\Mi 9 SE"
        self.ids.l_date_origin_filepath.text = origin
        
    def date_startparse(self):
        global count
        sort_foto.parse_fotos(origin, destination,count)
        GlobalVar.count = count
        
        sortdate = self.manager.get_screen('sortdate')
        sortdate.ids.l_date_num_images.text = str(count.count_images)
        sortdate.ids.l_date_num_noexif.text = str(count.count_noexif_date)
        sortdate.ids.l_date_num_videos.text = str(count.count_videos)
        sortdate.ids.l_date_num_memory.text = str(int(count.memory_size_MB))
        
    def reset_count(self):
        global count 
        count = sort_foto.Data_info()


class Window_SortDate(Screen):
    def date_startsort(self):
        sort_foto.build_folder_structure(destination, count.dict_years,count.list_years_videos)
        sort_foto.copy_file_date(count)


class Window_LocationInfo(Screen):
    pass


class Window_SearchInfo(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class SortApp(App):
    def build(self):
        return sm
    
if __name__ == '__main__':
    kv = Builder.load_file("sort.kv")
    sm = WindowManager()

    screens = [Start_Window(name="start"), Window_DateInfo(name="dateinfo"), Window_SortDate(name="sortdate"),
           Window_LocationInfo(name="locationinfo"), Window_SearchInfo(name="searchinfo")]
    for screen in screens:
        sm.add_widget(screen)

    sm.current = "start"
    SortApp().run()

