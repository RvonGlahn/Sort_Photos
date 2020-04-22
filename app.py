'''
open copied fotos
tab through inputfields
'''
import os
import sys
import kivy
import GlobalVar
import sort_foto
import datetime
import time
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


class Start_Window(Screen):
    def set_desktop(self):
        GlobalVar.path_desktop = os.path.expanduser("~/Desktop")
        fc = self.manager.get_screen('my_filechooser')
        fc.ids.filechooser.path = GlobalVar.path_desktop


class Window_DateInfo(Screen):
    
    def set_pathtype(self, path_type):
        GlobalVar.path_type = path_type
        
    def check_path(self):
        if GlobalVar.path_origin == "" or GlobalVar.path_destination == "" :
            popup = Popup(title='Reminder', content=Label(text='Please select a folder \nfor origin and destination',font_size = "16sp"),size_hint=(None, None), size=(300, 300))
            popup.open()
        else:
            self.date_startparse()
            sm.current = "sortdate"
        
    def date_startparse(self):
        '''
        Sets
        -------
        Label Texts in "Sortdate" with parsed info from function sort_foto.parse_fotos

        '''
        sort_foto.parse_fotos(GlobalVar.path_origin, GlobalVar.path_destination, GlobalVar.count)           
        
        sortdate = self.manager.get_screen('sortdate')
        sortdate.ids.l_date_num_images.text = str(GlobalVar.count.count_images)
        sortdate.ids.l_date_num_noexif.text = str(GlobalVar.count.count_noexif_date)+" (" + str(int(GlobalVar.count.count_noexif_date*100/GlobalVar.count.count_images))+ "%)"
        sortdate.ids.l_date_num_noloc.text = str(GlobalVar.count.count_images-GlobalVar.count.count_gps)+" (" + str(int((GlobalVar.count.count_images-GlobalVar.count.count_gps)*100/GlobalVar.count.count_images))+ "%)"
        sortdate.ids.l_date_num_videos.text = str(GlobalVar.count.count_videos)
        sortdate.ids.l_date_num_memory.text = str(int(GlobalVar.count.memory_size_MB))

   
class Add_Exif(Screen):
    
    def get_datelist(self):
        ''' 
        Iterate over photos to find ones without exif date. Get Infos from User and store them in no_date_list 
        info[0]: path to image , info[3]: Boolean-> False if no Exif data
        '''
        if not GlobalVar.no_date_list:
            for date, photos in GlobalVar.count.search_dict_date.items():
                for info in photos:
                    if info[3] == False:                 
                        GlobalVar.no_date_list.append([info[0],info[3]])
                        
    def next_image(self):
        ''' loads newimage in GUI and sets True for all images skipped or not'''
        count = 0
        for path , check in GlobalVar.no_date_list:
            if check == False:
                self.ids.image_exif.source = path
                GlobalVar.exif_path = path
                GlobalVar.no_date_list[count][1] = True
                break
            count += 1
                    
    def set_exif(self,year,month,day):
        '''
        
        Parameters
        ----------
        year : String
        month : String
        day : String

        Exception 
        -------
        ValueError opens a Pop Up to demand correct inputs
        If input correct sort_foto.add_exif adds exif date to Image
        '''
        try: 
            if int(year) and int(month) and int(day):
                if len(year)==4 and len(month)<=2 and len(day)<=2:
                    sort_foto.add_exif(GlobalVar.exif_path, datetime.datetime(int(year),int(month),int(day)))
                    self.ids.year.text = ""
                    self.ids.month.text = ""
                    self.ids.day.text = ""
                else:
                    popupp = Popup(title='Reminder', content=Label(text='Please insert numbers for \nyear, month and day.',font_size = "16sp"),size_hint=(None, None), size=(300, 300))
                    popupp.open()
        except ValueError:        
            popup = Popup(title='Reminder', content=Label(text='Please insert numbers for \nyear, month and day.',font_size = "16sp"),size_hint=(None, None), size=(300, 300))
            popup.open()
            
    def reset_exif(self):
        self.ids.image_exif.source = 'images/exif_picture.png'
        GlobalVar.no_date_list.clear()
        
    def reset_count(self):
        '''Delete Count for clearing the foto data befor analyzing new Photos '''
        del (GlobalVar.count)
        GlobalVar.count = sort_foto.Data_info()



class Window_SortDate(Screen):
    
    def date_startsort(self):
        sort_foto.build_folder_structure(GlobalVar.path_destination, GlobalVar.count.dict_years,GlobalVar.count.list_years_videos)
        sort_foto.copy_file_date(GlobalVar.count)

    def location_startsort(self):
        sort_foto.build_folder_structure_loc(GlobalVar.path_destination, GlobalVar.count.dict_locations,GlobalVar.count.list_years_videos)
        sort_foto.copy_file_loc(GlobalVar.count)
        
    def reset_count(self):
        '''Delete Count for clearing the foto data befor analyzing new Photos '''
        del (GlobalVar.count)
        GlobalVar.count = sort_foto.Data_info()
        
        

class My_Filechooser(Screen):
    def open(self, path):
        '''
        
        Parameters
        ----------
        path : string
            Set Path to origin and destination in DateInfo, depends on GlobalVar.path_type
        '''
        if GlobalVar.path_type == "origin":
            GlobalVar.path_origin = path
            infodate = self.manager.get_screen('dateinfo')
            infodate.ids.l_date_origin_filepath.text = path
        if GlobalVar.path_type == "destination":
            GlobalVar.path_destination = path
            infodate = self.manager.get_screen('dateinfo')
            infodate.ids.l_date_dest_filepath.text = path



class Search_Date(Screen):

    def search_date(self,start_date, end_date):
        '''
        Parameters
        ----------
        start_date : String
            string of integers "2017-12-31"
        end_date : String
            string of integers "2017-02-01"

        Opens
        -------
        search_date
            function to search photos between start and end date
        '''
        check1 = self.check_input(start_date)
        check2 = self.check_input(end_date)
        if check1 == True and check2 == True:
            sort_foto.search_date(GlobalVar.count, GlobalVar.path_destination, start_date, end_date)
            sm.current = "last_screen"
        else:
            popup_search1 = Popup(title='Reminder', content=Label(text='Please enter the date correctly. \nYYYY-MM-DD \nExample: 2020-04-12',
                                                                         font_size = "16sp"),size_hint=(None, None), size=(300, 300))
            popup_search1.open()
    
    def check_input(self, date_string):
        '''
        Parameters
        ----------
        date_string : string
            Needs to be String of Integers example 2017-

        Returns
        -------
        bool
            Boolean wheater the input is in correct 

        '''
        try:
            year,month,day = date_string.split("-")
            try: 
                if int(year) and int(month) and int(day):
                    if len(year)==4 and len(month)==2 and len(day)==2:
                        return True
                    else:    
                        return False
            except ValueError:
                 return False        
        except ValueError:
            return False
            


class Last_Screen(Screen):
    def reset_count(self):
        '''Delete Count for clearing the foto data befor analyzing new Photos '''
        del (GlobalVar.count)
        GlobalVar.count = sort_foto.Data_info()
        
        

class WindowManager(ScreenManager):
    pass



class SortApp(App):
    def build(self):
        return sm
 
    
def resourcePath():
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)

    return os.path.join(os.path.abspath("."))
    
    
if __name__ == '__main__':
    kivy.resources.resource_add_path(resourcePath()) 
    kv = Builder.load_file("sort.kv")
    sm = WindowManager()

    screens = [Start_Window(name="start"), Window_DateInfo(name="dateinfo"), My_Filechooser(name ="my_filechooser"), Add_Exif(name="addexif"), Window_SortDate(name="sortdate"),
               Search_Date(name="searchdate"),Last_Screen(name="last_screen")]
    for screen in screens:
        sm.add_widget(screen)

    sm.current = "start"
    SortApp().run()

