from Oscilloscope import Oscilloscope
import sys
import os
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps

def main(args): 

    scope = Oscilloscope()

    while True: # the plan is to run the script, set the trigger parameters, save screenshot 
        # save csv, and reset 
        #scope.set_trigger(volts_div, time_div, which channels)
        scope.screenshot(args) 
        #scope.save_csv() 
    
    


if __name__ == '__main__': 
    main(sys.argv)