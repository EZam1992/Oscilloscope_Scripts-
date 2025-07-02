from Oscilloscope import Oscilloscope
import sys
import os
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps

def main(args): 
    volts_div = 2  # volts
    time_div = 0.5 # seconds
    channel_list = [1, 2, 3, 4]

    scope = Oscilloscope()

    # the plan is to run the script, set the trigger parameters, save screenshot 
        # save csv, and reset 
        #scope.set_trigger(volts_div, time_div, which channels)
    scope.set_trigger(volts_div, time_div, channel_list) 
    scope.screenshot(args) 
        #scope.save_csv() 
    
    


if __name__ == '__main__': 
    main(sys.argv)