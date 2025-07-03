import pyvisa
import sys 
from datetime import datetime 
from PIL import Image, ImageFont, ImageDraw, ImageOps
import csv
import os
import numpy as np

class Oscilloscope(): 
    def __init__(self, time_div): 
        self.rm = pyvisa.ResourceManager() 
        for connected_device in self.rm.list_resources(): 
            try: 
                self.connection = self.rm.open_resource(connected_device)
                self.connection.timeout = 20000
                self.counter = 0 
                self.response = self.connection.query("*IDN?").lower() 
                if "rigol" in self.response: 
                    self.type = "Rigol"
                    print(f"{self.type} Oscilloscope Connected")
            except: 
                raise IOError("Unable to find an acceptable scope.")
            
            self.set_time_div(time_div)
            
    def screenshot(self, folder_path):
         
        # try: 
        #     self.fname_stem = str(sys.argv[1])
        # except IndexError: 
        #     self.fname_stem = input("Please enter a file name: ")
        self.fname_stem = "TEST"

        self.date_string = datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S_")
        self.fname = self.date_string + self.fname_stem + f".png" 
        self.full_path = os.path.join(folder_path, self.fname)
        self.date_stamp_height_px = 23
        self.date_stamp_string = datetime.now().strftime("%A, %d %b %Y %H:%M:%S")
        self.date_stamp_font = ImageFont.truetype("arial.ttf", self.date_stamp_height_px)

        try: 
            self.connection.write(":DISP:DATA?")
            self.image_data = self.connection.read_raw()[11:]
        except: 
            raise IOError("Unable to connect to scope")
        
        with open(self.full_path, "wb") as self.fout: 
            self.fout.write(self.image_data)


        self.img = Image.open(self.full_path)
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
        self.img.save(self.full_path)

        

    def set_time_div(self, time_div): 
        self.connection.write(f"TIMebase:MAIN:SCALe {time_div}") 

    def set_voltage_div(self, channel, volts_div): 
        self.connection.write(f":CHANnel{channel}:SCALe {volts_div}")

    def set_trigger(self, volts_div, time_div, channel_list):
        self.connection.write(":RUN")
        self.trigger_ON = True
        self.connection.write(":TRIGger:MODE EDGE")
        self.connection.write(":TRIGger:SWEep SINGle")
        self.connection.write(":TRIGger:EDGe:SOURce CHANnel4")
        self.connection.write(":TRIGger:EDGe:SLOpe POSitive")
        self.connection.write(":TRIGger:EDGe:LEVel 2.5")

        for channel in channel_list:
            self.counter += 1
            if self.counter <= 4:
                self.connection.write(f":CHANnel{channel}:DISPlay 1") 
                self.connection.write(f":CHANnel{channel}:OFFSet 0")
                self.connection.write(f":CHANnel{channel}:PROBe 1")
            
                self.set_voltage_div(channel, volts_div)

    def configure_channel(self,channel): 
        self.connection.write(":STOP")
        self.connection.write(f":WAVeform:SOURce CHANnel{channel}")
        self.connection.write(":WAVeform:MODE NORMal")
        self.connection.write(":WAVeform:FORMat ASCii")
        self.connection.write(":TIM:REF LEFT")

    
    def read_ascii(self):
        self.connection.write(":WAVeform:DATA?")
        self.data = self.connection.read_raw()
        # Get preamble
        self.preamble = self.connection.query(":WAVeform:PREamble?").split(',')
        self.x_incr = float(self.preamble[4])   # Time between points
        self.x_origin = float(self.preamble[5]) # Time at index 0
        # Parse SCPI header; this is needed bacause the ASCII data 
        # returned by the oscilloscope includes a header when the data is queried: #9<length><data> 
        if self.data[0:1] == b'#':
            self.header_len = int(self.data[1:2].decode())
            self.num_digits = int(self.data[2:2+ self.header_len].decode())
            self.data_start = 2 + self.header_len
            self.data = self.data[self.data_start:self.data_start + self.num_digits]
        else:
             raise ValueError("Invalid data format from scope.")
        

    def save_csv(self, volts_div, time_div, channel_list):
    
        

        while self.trigger_ON:
            flag = self.connection.query(":TRIGger:STATus?")
            if "STOP" in flag: 
                self.trigger_ON = False

                #Create a new folder using current timestamp
                folder_name = datetime.now().strftime("capture_%Y-%m-%d_%H-%M-%S")
                folder_path = os.path.join("captures", folder_name)
                os.makedirs(folder_path, exist_ok=True)

                for channel in channel_list:
                    self.configure_channel(channel)
                    self.read_ascii()

                    # Split and convert voltage values
                    self.ascii_data = self.data.decode()
                    self.voltages = np.array([float(v) for v in self.ascii_data.strip().split(',') if v.strip()])

                    # Generate time values
                    self.times = np.arange(len(self.voltages)) * self.x_incr + self.x_origin


                    csv_filename = os.path.join(folder_path, f"channel{channel}.csv")   
                    with open(csv_filename, mode='w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Time (s)", "Voltage (V)"])

                        for t, v in zip(self.times, self.voltages):
                            writer.writerow([f"{t:.6f}", f"{v:.6f}"])

                        #writer.writerows(zip(self.times, self.voltages))
                    
                self.screenshot(folder_path)
                    
                self.set_trigger(volts_div, time_div, channel_list)



        