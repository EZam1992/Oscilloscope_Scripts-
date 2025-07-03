from Oscilloscope import Oscilloscope
import sys 

def main(args): 

    """ Defines the primary functionality of the script
    
    Args: 
        args (str): any argument the user would like to pass to the script 

    Outputs: csv files and screenshot of oscilloscop capture 
    
    """
    volts_div = int(input("Volts per division (V): ")) # volts
    time_div = float(input("Specify time per division (s): ")) # seconds
    channel_list = [1, 2, 3, 4] # Desired channels 


    scope = Oscilloscope(time_div)
    scope.set_trigger(volts_div, time_div, channel_list)
    scope.save_csv(volts_div, time_div, channel_list, args[1])

if __name__ == '__main__': 
    main(sys.argv)

