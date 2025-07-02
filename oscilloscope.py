import pyvisa
import sys 
from datetime import datetime 
from PIL import Image, ImageFont, ImageDraw, ImageOps

class Oscilloscope(): 
    def __init__(self): 
        self.rm = pyvisa.ResourceManager() 
        for connected_device in self.rm.list_resources(): 
            try: 
                self.connection = self.rm.open_resource(connected_device)
                self.connection.timeout = 3000
                self.response = self.connection.query("*IDN?").lower() 
                if "rigol" in self.response: 
                    self.type = "Rigol"
                    print(f"{self.type} Oscilloscope Connected")
            except: 
                raise IOError("Unable to find an acceptable scope.")
            
    def screenshot(self, args):
         
        try: 
            self.fname_stem = str(sys.argv[1])
        except IndexError: 
            self.fname_stem = input("Please enter a file name: ")

        self.date_string = datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S_")
        self.fname = self.date_string + self.fname_stem + f".png" 
        self.date_stamp_height_px = 23
        self.date_stamp_string = datetime.now().strftime("%A, %d %b %Y %H:%M:%S")
        self.date_stamp_font = ImageFont.truetype("arial.ttf", self.date_stamp_height_px)

        try: 
            self.connection.write(":DISP:DATA?")
            self.image_data = self.connection.read_raw()[11:]
        except: 
            raise IOError("Unable to connect to scope")
        

        
        print("Reading image data", flush=True)
        print(f"Saving image to {self.fname}", flush=True)
        with open(self.fname, "wb") as self.fout: 
            self.fout.write(self.image_data)


        self.img = Image.open(self.fname)
        self.img = ImageOps.expand(self.img,border=self.date_stamp_height_px,fill=0)
        self.img = self.img.crop((self.date_stamp_height_px,
                    0,
                    self.img.size[0] - self.date_stamp_height_px,
                    self.img.size[1]))
        self.img_editable = ImageDraw.Draw(self.img)
        self.img_editable.text((self.date_stamp_height_px, self.date_stamp_height_px * 0.1), 
                        self.date_stamp_string,
                        (248, 252, 248),
                        self.date_stamp_font)
        self.img.save(self.fname)

        

    def set_time(self): 
        pass 

    def set_voltage(self): 
        pass 

    def set_trigger(self):

        #user needs to pass the desired second per div and voiltage per div 
        # call set seconds per div 
        # call set voltage per div  
        pass 

        