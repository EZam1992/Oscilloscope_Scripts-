from Oscilloscope import Oscilloscope
import sys 

def main(args): 
    volts_div = 2  # volts
    time_div = 0.5 # seconds
    channel_list = [1, 2, 3, 4]

    scope = Oscilloscope()
    scope.set_trigger(volts_div, time_div, channel_list)
    scope.save_csv(volts_div, time_div, channel_list)

if __name__ == '__main__': 
    main(sys.argv)

