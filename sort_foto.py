import PIL 
from PIL.ExifTags import TAGS
import piexif
from datetime import datetime, timedelta
import os
import shutil
import sys
from geopy.geocoders import Nominatim

'''
Anpassungen:
pytoexe
pytoapp
Objekterkennung
 - Freunde finden
 - Selfies
 - Datum schätzen
GAN - Freunde erstellen
'''


class Data_info:
    """
    Class to store information about all files that will be accesed in the Programm
    """
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
        self.dict_locations = {}   
        
        self.search_dict_date = {}
        self.search_dict_date_video = {}
        self.search_dict_loc = {}

    def update_search_dict_loc(self, image_data):
        """
        search_dict_location stores all locations for searching fotos
        (location) :  [[path_orig,path_dest,image_name],[path_orig,path_dest,image_name], ...]
        """
        country, city =  image_data.location
        key = str(image_data.year)+'-'+country+'-'+city
        
        info = []
        info.append(image_data.path_origin)
        info.append(image_data.path_dest)
        info.append(image_data.name) 
        if key in self.search_dict_loc:
            self.search_dict_loc[key].append(info)
        else:
            self.search_dict_loc.update({key:[info]})
    
    def update_search_dict_date(self, image_data):
        """
        search_dict_date stores all dates for searching fotos
        (year,month,day) :  [[path_orig,path_dest, image_name],[path_orig,path_dest,image_name], ...]
        """
        date = datetime.date(datetime(image_data.year, image_data.month, image_data.day))
        key = date.strftime("%Y-%m-%d")
        
        info = []
        info.append(image_data.path_origin)
        info.append(image_data.path_dest)
        info.append(image_data.name)
        info.append(image_data.has_exifdate)
        
        if key in self.search_dict_date:
            self.search_dict_date[key].append(info)
        else:
            self.search_dict_date.update({key:[info]})
       
    def update_search_dict_date_video(self, year , path_origin, path_dest, name):
        """
        search_dict_date stores all dates for searching videos
        (year,month,day) :  [[path_orig,path_dest, image_name],[path_orig,path_dest,image_name], ...]
        """
        key = year 
        info = []
        info.append(path_origin)
        info.append(path_dest)
        info.append(name)

        if key in self.search_dict_date_video:
            self.search_dict_date_video[key].append(info)
        else:
            self.search_dict_date_video.update({key:[info]})

    '''__________________________________________________________________________________________'''

    def update_memory(self, file_size):
        """updates the size of memory for all copied fotos"""
        self.memory_size_MB += file_size/pow(2,20)
     
    def updatefoto_years(self, year, month):
        """update dict that has all dates (year,month) to build folder structure for images """
        if year in self.dict_years:
            if month in self.dict_years[year]:
                return
            else:
                self.dict_years[year].append(month)  
        else:    
            self.dict_years.update({year:[month]})
    
    def updatevideo_years(self, year, month):
        """update dict that has all dates (year,month) to build folder structure for video"""
        if year in self.list_years_videos:
            return
        else:
            self.list_years_videos.append(year)
            
    def update_location(self, image_data):
        """
        update dict that has all years and locations (year,country,city)
        to build folder structure for images
        cities only for Germany
        """
        country, city = image_data.location
        year = image_data.year
        
        if year in self.dict_locations:
            if country in self.dict_locations[year]:
                if city in self.dict_locations[year][country]:
                    return
                else:
                    self.dict_locations[year][country].append(city)  
            else:    
                self.dict_locations[year].update({country:[city]})
        else:        
            self.dict_locations.update({year: {}})
            self.dict_locations[year].update({country:[city]})


'''
_____________________________________________________________________________________________________
'''


class Fotoinfo:
    """
    Class to store the important information of every Foto in an Object
    """
    def __init__(self, img,image_name, path_dest, path_origin,count):
        self.name = image_name
        self.foto = img
        self.has_exifdate = False
        self.path_dest = path_dest
        self.path_origin = path_origin
        self.exif_data = self.get_exif_data(count)
        self.geo_coords = self.get_geotagging(count)
        self.location = self.get_location()
        self.date =self.get_date_time(count)
        self.year = 0
        self.month = 0
        self.day = 0
        super(Fotoinfo, self).__init__()
        
    def get_exif_data(self,count):
        """
        class method to read the labelled exif Data from foto files
        """
        try:
            self.foto.verify()
            exif =  self.foto._getexif()
            labeled = {}
            for (key, val) in exif.items():
                labeled[TAGS.get(key)] = val
            return labeled
        except:
            count.count_noexif += 1
            return"No exif_data in", self.name

    def get_date_time(self,count):
        """
        class method to read the Date from the labelled exif data
        """
        try:
            if 'DateTime' in self.exif_data:
                date_and_time = self.exif_data['DateTime']
                self.has_exifdate = True
                count.count_date += 1
                return date_and_time
            else:    
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
        """
        Convert Exif Data for values of longitude and latitude
        to geo coordiantes
        """
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1] / 60.0
        seconds = dms[2][0] / dms[2][1] / 3600.0
        
        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds
        
        return round(degrees + minutes + seconds, 5)

    def get_geotagging(self,count):
        """Read GPSInfo from EXIF DATA
        converts GPS data to latitude and longitude in get_decimal_from_dms()
        returns  latitude and longitude"""
        if not self.exif_data:
            raise ValueError("No EXIF metadata found")
            
        try:
            geotags = []
            if 'GPSInfo' in self.exif_data:
                count.count_gps += 1
                gps = self.exif_data['GPSInfo']
                for key in range(1,5):
                    geotags.append((key, gps[key]))
            dict_geotags = dict(geotags)        
            
            lat = self.get_decimal_from_dms(dict_geotags[2], dict_geotags[1])
        
            lon = self.get_decimal_from_dms(dict_geotags[4], dict_geotags[3])
                
            return str(lon),str(lat)
        except:
            return False

    def get_location(self):
        """convert lat,long to location"""
        if not self.geo_coords:
            return False
        lon,lat = self.geo_coords
        geolocator = Nominatim(user_agent="sort")
        try:
            loc = geolocator.reverse(lat+","+ lon, language='en',timeout=10000)
        except:
            return False
        dict_loc = loc.raw["address"]
        country = dict_loc["country"]
        try:
            city = dict_loc["city"]
        except:
            city = dict_loc["town"]
        return country, city


'''
___________________________________________________________________________________________________________
'''


def set_filepaths():
    """
    origin: folder from which you import the pictures
    destintion: folder where you will save the new folder structure
    """
    origin = r"C:\Users\Rasmus\Desktop\Rasmus\Fotos\Smartphone\Test"
    destination = r"C:\Users\Rasmus\Desktop\Rasmus\Photos"
    search = r"C:\Users\Rasmus\Desktop\Rasmus\Photos\search"
    return origin, destination, search


def month_to_foldername(month):
    """group months for folder structure"""
    folder_name = " "
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
    """
    Anhand des globalen Objektes Count wird die Ordner Struktur gebildet
    Für jedes Jahr wird ein Ordner angelegt, der in 4 Unterordner strukturiert wird, sofern Fotos für die Monate vorhanden sind
    Videos erhalten eigenen Ordner der in Jahre unterteilt ist.
    """
    for year in dict_images:
         path = os.path.join(path_dest, str(year))
         for month in dict_images[year]:
            folder_name = month_to_foldername(month)  
            if not os.path.exists(os.path.join(path, folder_name)):    
                os.makedirs(os.path.join(path, folder_name))
    path_video = os.path.join(path_dest, "videos")
    for year in list_videos:
        if not os.path.exists(os.path.join(path_video, str(year))):
            os.makedirs(os.path.join(path_video, str(year)))


def build_folder_structure_loc(path_dest, dict_images, list_videos ):
    """
    Anhand des globalen Objektes Count wird die Ordner Struktur gebildet
    Für jedes Jahr wird ein Ordner angelegt, der in 4 Unterordner strukturiert wird, sofern Fotos für die Monate vorhanden sind
    Videos erhalten eigenen Ordner der in Jahre unterteilt ist.
    """
    for year in dict_images:
         path = os.path.join(path_dest, str(year))
         for country in dict_images[year]:
             if country == "Germany":
                 for city in dict_images[year][country]:
                     if not os.path.exists(os.path.join(path, country, city)):    
                         os.makedirs(os.path.join(path, country, city))
             if not os.path.exists(os.path.join(path, country)):    
                 os.makedirs(os.path.join(path, country))
    path_video = os.path.join(path_dest, "videos")
    for year in list_videos:
        if not os.path.exists(os.path.join(path_video, str(year))):
            os.makedirs(os.path.join(path_video, str(year)))

        
def search_date(count,path_dest_date,start_date,end_date = False):
    """
    Date (YYYY-MM-DD) und Path muss richtiges Format haben
    Opens the folder in which the fotos of the date(s) should be.
    Create new Folder "search - date"
    copy all Fotos that match the Date to folder.
    """
    if end_date:
        start_year, start_month, start_day = start_date.split("-")
        end_year, end_month, end_day = end_date.split("-")
        
        sdate = datetime.date(datetime(int(start_year), int(start_month), int(start_day)))
        edate = datetime.date(datetime(int(end_year), int(end_month), int(end_day)))
        delta = edate - sdate       # as timedelta
        
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            itter_day = day.strftime("%Y-%m-%d")
            if itter_day in count.search_dict_date:
                
                infos = count.search_dict_date[itter_day]      # iterate over all days
                for image_info in infos:                                               # iterate over all photos in list
                    path_origin = image_info[0]
                    shutil.copy2(path_origin, path_dest_date)    
    else:
        if start_date in count.search_dict_date:
            infos = count.search_dict_date[start_date]      # iterate over all days
            year,month,day = start_date.split("-")    
            for image_info in infos:                                                # iterate over all photos in list
                path_origin = image_info[0]
                shutil.copy2(path_origin, path_dest_date)    
        else:
            return False


def copy_file_loc(count):
    """
    copy file from origin to destination
    first images second vidoes
    """
    for keys, infos in count.search_dict_loc.items():                           # iterate over all locations
        year,country,city = keys.split("-")
        for image_info in infos:                                                # iterate over all photos in list
            if country == "Germany":
                path_dest= os.path.join(image_info[1], str(year), country, city)
            else:
                path_dest= os.path.join(image_info[1], str(year),country)
            path_origin = image_info[0]
            shutil.copy2(path_origin, path_dest)
    
    for year, infos in count.search_dict_date_video.items():
        for video_info in infos:
            path_dest= os.path.join(video_info[1],"videos",str(year))
            path_origin = video_info[0]
            shutil.copy2(path_origin, path_dest)
        
        
def copy_file_date(count):
    """
    copy file from origin to destination
    first images second vidoes
    """
    for date, infos in count.search_dict_date.items():      # iterate over all days
        year,month,day = date.split("-")    
        folder_name = month_to_foldername(int(month))
        for image_info in infos:                                                # iterate over all photos in list
            path_dest= os.path.join(image_info[1], str(year), folder_name)
            path_origin = image_info[0]
            shutil.copy2(path_origin, path_dest)
            
    for year, infos in count.search_dict_date_video.items():
        for video_info in infos:
            path_dest= os.path.join(video_info[1],"videos",str(year))
            path_origin = video_info[0]
            shutil.copy2(path_origin, path_dest)
        
    
def get_date(image,image_path,count):
    """ Change dates to datetime and edit modification time if no exif date exists"""
    if image.date:
        time_exif = datetime.strptime(image.date, "%Y:%m:%d %H:%M:%S")
        count.updatefoto_years(time_exif.year, time_exif.month)
        image.set_year(time_exif.year)  
        image.set_month(time_exif.month)
        image.set_day(time_exif.day)
    else:                                                                       # if exif.date doesnt exist use mtime
        timestamp = os.path.getmtime(image_path)
        time_mtime = datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d %H:%M:%S')
        count.updatefoto_years(int(time_mtime[0:4]), int(time_mtime[5:7]))
        image.set_year(int(time_mtime[0:4]))  
        image.set_month(int(time_mtime[5:7]))
        image.set_day(int(time_mtime[8:10]))
    count.update_search_dict_date(image)
    if image.location:
        count.update_location(image)


def get_Data(image_path, path_dest, img_name, count):
    """
    copy:   True if image gets copied
            False if image only gets parsed
    image: currently chosen image
    image_path: path to the currently chosen image
    open image and read exif_data if existent if not use mtime
    """
    try:                   
        img = PIL.Image.open(image_path)
        
        count.count_images += 1                                  # count total number of images
        count.update_memory(os.path.getsize(image_path))         # update size of all images that will get copied in MB
    except:
        e = sys.exc_info()[1]
        print( "<p>Error: %s</p>" % e )
        return 
    try:
        image = Fotoinfo(img, img_name, path_dest, image_path, count)                 #check if picture has exif data
        get_date(image,image_path,count)
        if image.geo_coords:    
            count.update_search_dict_loc(image)
        img.close()
    except:
        e = sys.exc_info()[1]
        print("<p>Error: %s</p>" % e )


def get_images(path, path_destination, count):
    """
    decide whether file is image or video
    pass images to get_data to extract exif data
    extract video_date directly and store it in a dict to the count object
    """
    extensions_images = "JPG","jpg","jpeg","PNG","png","tiff","tif","TIF","BMP","bmp"
    extensions_videos = "mov","MOV","mp4","MP4"
    for image in os.listdir(path):
        if image.endswith(extensions_images):                                              # get Data from fotos
            get_Data(os.path.join(path, image), path_destination, image, count)                
            
        if image.endswith(extensions_videos):                                              # get Data from videos
            timestamp = os.path.getmtime(os.path.join(path, image))
            time_mtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            count.updatevideo_years(int(time_mtime[0:4]), int(time_mtime[5:7]))
            count.update_search_dict_date_video(time_mtime[0:4], os.path.join(path, image) , path_destination, image)
            count.count_videos += 1                                                     # count total number of images
            count.update_memory(os.path.getsize(os.path.join(path, image))) 


def parse_fotos(path_origin, path_destination, count):
    """
    use os walk to parse all images from folder structure
    pass image_path to get_Data() to get date and location
    copy video based on year to new directory
    """
    liste = []
    x = 0
    for directory, subDirectories, files in os.walk(path_origin):
        liste.append(files) 
        
        if x == 0:
            x += 1
            if files:
                get_images(os.path.join(directory), path_destination, count)
        for subDir in subDirectories:               # nach und nach die einzelnen SUb Directories absuchen            
            get_images(os.path.join(directory, subDir),path_destination, count)         # alle images einzeln auswerten


def add_exif(file, datetime_object):
    img = PIL.Image.open(file)
    try:                                  # If the image already contains data, we only replace the relevant properties
        exif_dict = piexif.load(img.info['exif'])
        print(f"Exif load for file '{file}'' successful")
    except KeyError: # If the image has no Exif data, we create the relevant properties
        f_dict = {}
        f_dict["0th"] = {}
        f_dict["Exif"] = {}
    try: # We now have a useful Exif dict, time to adjust the values
        d = datetime_object.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["Exif"][36868] = d.encode("utf-8")
        exif_dict["Exif"][36867] = d.encode("utf-8")
        exif_dict["0th"][306] = d.encode("utf-8")    # Convert into bytes and dump into file
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file)
    except:
        print("Failed")

                
def main():
    count = Data_info()
    path_origin, path_destination, search_path = set_filepaths()
    
    parse_fotos(path_origin, path_destination, count)
    
    # build_folder_structure(path_destination, count.dict_years,count.list_years_videos)
    # copy_file_date(count)
    
    # search_date(count, search_path,"2017-10-17")
    
    # build_folder_structure_loc(path_destination, count.dict_locations,count.list_years_videos)
    # copy_file_loc(count)

    add_exif(r"C:\Users\Rasmus\Desktop\Rasmus\Fotos\Smartphone\Test\IMG_0010.JPG", datetime(2014, 1, 1))

    ''' Info Section '''
    # print(count.search_dict_date)
    # print(count.list_years_videos)
    print("Images",count.count_images)
    print("GPS",count.count_gps)
    print(int(count.memory_size_MB),"MB Memory copied")
    print("Videos:",count.count_videos)
    print("Exif_date exists",count.count_date)
    print("No Exif Date",count.count_noexif_date)
    print("No Exif",count.count_noexif)

    
if __name__ == "__main__":
    main()