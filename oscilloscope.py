import pyvisa
import sys 
import datetime

class Oscilloscope(): 
    def __init__(self): 
        self.rm = pyvisa.ResourceManager() 
        for connected_device in self.rm.list_resources(): 
            try: 
                self.connection = self.rm.open_resource(connected_device)
                self.response = self.connection.query("*IDN?").lower() 
                if "rigol" in self.response: 
                    self.type = "Rigol"
                    print(f"{self.type} Oscilloscope Connected")
            except: 
                raise IOError("Unable to find an acceptable scope.")
            
    def screenshot(self, args):
        try: 
            fname_stem = str(sys.arg[1])
        except IndexError: 
            fname_stem = input("Please enter a file name: ")

        date_string = datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S_")
        fname = date_string + fname_stem + f".png" 


        pass 

    def set_time(self): 
        pass 

    def set_voltage(self): 
        pass 

    def set_trigger(self):

        #user needs to pass the desired second per div and voiltage per div 
        # call set seconds per div 
        # call set voltage per div  
        pass 

        