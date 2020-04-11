'''
Windows für alle Funktionen
try except mit Pop.up für leere pfade
datepicker
count reset für go back 
progress bar für copy
images folder erstellen
Fehler beheben
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
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser


Window.size = (600, 400)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

count = sort_foto.Data_info()


class Start_Window(Screen):
    def set_desktop(self):
        GlobalVar.path_desktop = os.path.expanduser("~/Desktop")
        fc = self.manager.get_screen('my_filechooser')
        fc.ids.filechooser.path = GlobalVar.path_desktop


class Window_DateInfo(Screen):
    
    def set_pathtype(self, path_type):
        GlobalVar.path_type = path_type
        
    def date_startparse(self):
        global count
        sort_foto.parse_fotos(GlobalVar.path_origin, GlobalVar.path_destination, count)
        GlobalVar.count = count
        
        
        sortdate = self.manager.get_screen('sortdate')
        sortdate.ids.l_date_num_images.text = str(count.count_images)
        sortdate.ids.l_date_num_noexif.text = str(count.count_noexif_date)
        sortdate.ids.l_date_num_noloc.text = str(count.count_images-count.count_gps)
        sortdate.ids.l_date_num_videos.text = str(count.count_videos)
        sortdate.ids.l_date_num_memory.text = str(int(count.memory_size_MB))
        
    def reset_count(self):
        global count 
        count = sort_foto.Data_info()


class Window_SortDate(Screen):
    def date_startsort(self):
        sort_foto.build_folder_structure(GlobalVar.path_destination, count.dict_years,count.list_years_videos)
        sort_foto.copy_file_date(count)

    def location_startsort(self):
        sort_foto.build_folder_structure_loc(GlobalVar.path_destination, count.dict_locations,count.list_years_videos)
        sort_foto.copy_file_loc(count)


class My_Filechooser(Screen):
    def open(self, path):
        if GlobalVar.path_type == "origin":
            GlobalVar.path_origin = path
            infodate = self.manager.get_screen('dateinfo')
            infodate.ids.l_date_origin_filepath.text = path
        if GlobalVar.path_type == "destination":
            GlobalVar.path_destination = path
            infodate = self.manager.get_screen('dateinfo')
            infodate.ids.l_date_dest_filepath.text = path


class Search_Date(Screen):
    pass


class Last_Screen(Screen):
    pass


class WindowManager(ScreenManager):
    pass








class SortApp(App):
    def build(self):
        return sm
    
if __name__ == '__main__':
    kv = Builder.load_file("sort.kv")
    sm = WindowManager()

    screens = [Start_Window(name="start"), Window_DateInfo(name="dateinfo"), My_Filechooser(name ="my_filechooser"), Window_SortDate(name="sortdate"),
               Search_Date(name="searchdate"),Last_Screen(name="last_screen")]
    for screen in screens:
        sm.add_widget(screen)

    sm.current = "start"
    SortApp().run()

