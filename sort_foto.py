import PIL 
#import PIL.Image as PILimage
#from PIL import ImageDraw, ImageFont, ImageEnhance
from PIL.ExifTags import TAGS

from datetime import datetime
import os
import shutil
import sys

'''
Anpassungen:
dicts für date und location 
iphone_data für location überprüfen
Foto_info erweitern um date Funktionen
search_date oder folder_structure erstellen
geo to location implementieren
GUI kivy
pytoexe
'''


class Data_info:
    '''
    Class to store information about all files that will be accesed in the Programm 
    '''
    def __init__(self):
        self.memory_size_MB = 0
        self.count_images = 0
        self.count_videos = 0
        self.count_date = 0
        self.count_gps = 0
        self.count_noexif_date = 0 
        self.count_noexif= 0 
        self.dict_years = {}
        self.list_years_videos = []
        self.list_locations = []        
        self.search_dict_date = {}
        self.search_dict_loc = {}
        #sys.getsizeof(self.search_dict_date)
    
    def update_search_dict_date(self, image_data):
        key = str(image_data.year)+str(image_data.day)+str(image_data.day)
        info = []
        info.append(image_data.path_dest)
        info.append(image_data.name)
        if key in self.search_dict_date:
            self.search_dict_date[key].append(info)
        else:
            self.search_dict_loc.update({key:[info]})
            
    def update_search_dict_loc(self, image_data):
        key = image_data.loc
        info = []
        info.append(image_data.path_dest)
        info.append(image_data.name)
        if key in self.search_dict_loc:
            self.search_dict_loc[key].append(info)
        else:
            self.search_dict_loc.update({key:[info]})
        
    def update_memory(self, file_size):
        self.memory_size_MB += file_size/pow(2,20)
     
    def updatefoto_years(self, year, month):
        if year in self.dict_years:
            if month in self.dict_years[year]:
                return
            else:
                self.dict_years[year].append(month)  
        else:    
            self.dict_years.update({year:[month]})
    
    def updatevideo_years(self, year, month):
        if year in self.list_years_videos:
            return
        else:
            self.list_years_videos.append(year)
            
    def search_date(self, date):
        '''
        Opens the folder in which the fotos of the date(s) should be. 
        Create new Folder "search - date"  
        copy all Fotos that match the Date to folder. 
        '''
        pass 
        
        
count = Data_info()        
'''
_____________________________________________________________________________________________________
'''
class Fotoinfo:
    '''
    Class to store the important information of every Foto in an Object
    '''    
    def __init__(self, img,image_name, path_dest, path_origin):
        self.name = image_name
        self.foto = img
        self.path_dest = path_dest
        self.path_origin = path_origin
        self.exif_data = self.get_exif_data()
        self.geo_coords = self.get_geotagging()
        #self.location = self.get_location()
        #self.lens_Model = self.get_lensModel()
        self.date =self.get_date_time()
        self.year = 0
        self.month = 0
        self.day = 0
        super(Fotoinfo, self).__init__()
        
    def get_exif_data(self):
        '''
        class method to read the labelled exif Data from foto files
        '''
        try:
            self.foto.verify()
            exif =  self.foto._getexif()
            labeled = {}
            for (key, val) in exif.items():
                labeled[TAGS.get(key)] = val
            print(labeled)    
            return labeled
        except:
            count.count_noexif += 1
            return("No exif_data in", self.name)
            #return False         # bei False soll manuelle Eingabe ausgelöst werden
    
    def get_date_time(self):
        '''
        class method to read the Date from the labelled exif data
        '''
        try:
            #b = self.exif_data
            if 'DateTimeOriginal' in self.exif_data:
                date_and_time = self.exif_data['DateTime']
                count.count_date += 1
                return date_and_time
            else:    
                #print("No Date inside the data." , self.name)
                count.count_noexif_date += 1    
                return False         # bei False soll manuelle Eingabe ausgelöst werden
        except:
            print( "No data for exif-date in picture" , self.name)
      
    def set_year(self,year_new):
        self.year = year_new
    def set_month(self,month_new):
        self.month = month_new
    def set_day(self,day_new):
        self.day = day_new
        
    def get_decimal_from_dms(self, dms, ref):
        '''
        Convert Exif Data for values of longitude and latitude
        to geo coordiantes
        '''
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1] / 60.0
        seconds = dms[2][0] / dms[2][1] / 3600.0
        
        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds
        
        return round(degrees + minutes + seconds, 5)
    
    def get_geotagging(self):
        '''
        Read GPSInfo from EXIF DATA
        converts GPS data to latitude and longitude in get_decimal_from_dms()
        returns  latitude and longitude
        '''
        if not self.exif_data:
            raise ValueError("No EXIF metadata found")
            
        try:
            geotags = []
            if 'GPSInfo' in self.exif_data:
                gps = self.exif_data['GPSInfo']
                for key in range(1,5):
                    geotags.append((key, gps[key]))
            dict_geotags = dict(geotags)        
            
            lat = self.get_decimal_from_dms(dict_geotags[2], dict_geotags[1])
        
            lon = self.get_decimal_from_dms(dict_geotags[4], dict_geotags[3])
                
            return (lon, lat)  
        except:
            #print("Foto doesn't contain Geo_Data")
            return False
'''
___________________________________________________________________________________________________________
'''



def set_filepaths():
    '''
    origin: folder from which you import the pictures
    destintion: folder where you will save the new folder structure
    '''
    origin = r"C:\Users\Rasmus\Desktop\Rasmus\Fotos\Smartphone\Test"
    destination = r"C:\Users\Rasmus\Desktop\Rasmus\Photos"
    return origin, destination


def month_to_foldername(month):
    if month in [1,2,3]:
        folder_name = "1-3"
    if month in [4,5,6]:
        folder_name = "4-6"
    if month in [7,8,9]:
        folder_name = "7-9"
    if month in [10,11,12]:
        folder_name = "10-12"      
    return folder_name

def build_folder_structure(path_dest, dict_images, list_videos ):
    '''
    Anhand des globalen Objektes Count wird die Ordner Struktur gebildet    
    Für jedes Jahr wird ein Ordner angelegt, der in 4 Unterordner strukturiert wird, sofern Fotos für die Monate vorhanden sind
    Videos erhalten eigenen Ordner der in Jahre unterteilt ist.
    '''
    for year in dict_images:
         #if not os.path.exists(os.path.join(path_dest, str(year))):
         path = os.path.join(path_dest, str(year))
         for month in dict_images[year]:
            folder_name = month_to_foldername(month)  
            if not os.path.exists(os.path.join(path, folder_name)):    
                os.makedirs(os.path.join(path, folder_name))
    #if not os.path.exists(os.path.join(path_dest, "videos")):
        #os.mkdir(os.path.join(path_dest, "videos"))
    path_video = os.path.join(path_dest, "videos")
    for year in list_videos:
        if not os.path.exists(os.path.join(path_video, str(year))):
            os.makedirs(os.path.join(path_video, str(year)))
        
        
        
def copy_file(path_origin, path_dest, file_name, image):
    '''
    copy file from origin to destination
    '''
    if image:
        folder_name = month_to_foldername(image.month)
        path_dest = os.path.join(path_dest, str(image.year), folder_name)
    #if not os.path.exists(os.path.join(path_dest, file_name)):         
    shutil.copy2(path_origin, path_dest)
            
        


def get_Data(image_path, path_dest, img_name, copy):
    '''
    copy:   True if image gets copied
            False if image only gets parsed
    image: currently chosen image 
    image_path: path to the currently chosen image
    open image and read exif_data if existent if not use mtime 
    '''
    try:                   
        img = PIL.Image.open(image_path)
        if not copy:
            count.count_images += 1                                                     # count total number of images
            count.update_memory(os.path.getsize(image_path))                            # update size of all images that will get copied in MB
    except:
        print("Image", img_name,"can't be opened.")
        e = sys.exc_info()[1]
        print( "<p>Error: %s</p>" % e )
        return 
    if True:
    #try:    
        image = Fotoinfo(img, img_name, path_dest, image_path)                                                             #check if picture has exif data
        #loc = image.location
        if image.date:
            time_exif = datetime.strptime(image.date, "%Y:%m:%d %H:%M:%S")
            count.updatefoto_years(time_exif.year, time_exif.month)
            image.set_year(time_exif.year)  
            image.set_month(time_exif.month)
            image.set_day(time_exif.day)
        else:                                                                       # if exif.date doenst exist use mtime 
            timestamp = os.path.getmtime(image_path)
            time_mtime = datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d %H:%M:%S')
            count.updatefoto_years(int(time_mtime[0:4]), int(time_mtime[5:7]))
            image.set_year(int(time_mtime[0:4]))  
            image.set_month(int(time_mtime[5:7]))
            image.set_day(int(time_mtime[8:10]))
            
        if image.geo_coords:    
            print(image.geo_coords)
        #count.update_search_dict(image)    
        img.close()
        if copy:
            copy_file(image_path, path_dest, img_name, image)
    #except: 
    #    e = sys.exc_info()[1]
    #    print( "<p>Error: %s</p>" % e )

def get_images(path, path_destination, copy):
    extensions_images = "JPG","jpg","jpeg","PNG","png","tiff","tif","TIF","BMP","bmp"
    extensions_videos = "mov","MOV","mp4","MP4"
    x = 0
    for image in os.listdir(path):
        x += 1
        if x == 10: 
             return
        if image.endswith(extensions_images):                                              #get Data from fotos
            get_Data(os.path.join(path, image), path_destination, image, copy)                
            
        if image.endswith(extensions_videos):                                              #get Data from videos
            timestamp = os.path.getmtime(os.path.join(path, image))
            time_mtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            count.updatevideo_years(int(time_mtime[0:4]), int(time_mtime[5:7]))
            if copy:
                year = int(time_mtime[0:4])
                copy_file(os.path.join(path,  image), os.path.join(path_destination, "videos" ,str(year)), image, False)
            if not copy:
                count.count_videos += 1                                                     # count total number of images
                count.update_memory(os.path.getsize(os.path.join(path, image))) 
    return x


def parse_fotos(path_origin, path_destination, copy):
    '''
    use os walk to parse all images from folder structure
    pass image_path to get_Data() to get date and location
    copy video based on year to new directory
    '''
    liste=[]
    for directory, subDirectories, files in os.walk(path_origin):
        liste.append(files) 
        
            #path = os.path.join(directory, subDir)  
        if files:
            get_images(os.path.join(directory), path_destination, copy)
        for subDir in subDirectories:               # nach und nach die einzelnen SUb Directories absuchen            
            get_images(os.path.join(directory, subDir),path_destination, copy)           # alle images einzeln auswerten
            break                       
                    
def main():
    path_origin, path_destination = set_filepaths()
    
    parse_fotos(path_origin, path_destination, False)
    build_folder_structure(path_destination, count.dict_years,count.list_years_videos)
    parse_fotos(path_origin, path_destination, True)

    #sort_fotos_bylocation(path_origin, path_destination)    
    
    
    
    print(count.dict_years) 
    #print(count.list_years_videos)

    print(count.count_images)
    #print(count.count_videos)
    print(int(count.memory_size_MB),"MB")


    
if __name__ == "__main__":
    count = main()    
    
