import pyvisa
import sys
import os
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw, ImageOps



def main(args):
    rm = pyvisa.ResourceManager()
    for connected_device in rm.list_resources():
        try:
            connection = rm.open_resource(connected_device)
            response = connection.query("*IDN?").lower()
            # print(response, flush=True)
            if "rigol" in response:
                take_screenshot = rigol_screenshot
                break
            elif "keysight" in response:
                take_screenshot = keysight_screenshot
                break
            elif "agilent" in response:
                take_screenshot = agilent_screenshot
                break
        except:
            raise IOError("Unable to find an acceptable scope. Please ensure scope is connected and VISA driver is installed")
            pass

    connection.timeout = 3000
    date_string = datetime.strftime(datetime.now(),"%Y%m%d_%H%M%S_")


    try:
        fname_stem = str(sys.argv[1])
    except IndexError:
        fname_stem = input("Please enter a filename: ")

    # filename has no suffix by default
    fname = date_string + fname_stem + f".png"

    fname_suffix = 0
    while os.path.exists(fname):
        # if there's a file that already exists (taken in the same second), add a suffix
        fname = date_string + fname_stem + f"_{fname_suffix}.png"
        fname_suffix += 1

    take_screenshot(fname, connection)


def rigol_screenshot(fname, connection):
    try:
        connection.write(":DISP:DATA?")
    except:
        raise IOError("Unable to connect to scope")
    image_data = connection.read_raw()[11:]
    print("Reading image data",flush=True)

    print(f"Saving image to {fname}", flush=True)
    with open(fname, "wb") as fout:
        fout.write(image_data)


    # add a timestamp 
    date_stamp_height_px = 23
    date_stamp_string = datetime.now().strftime("%A, %d %b %Y %H:%M:%S")
    date_stamp_font = ImageFont.truetype("fonts/FreeMono.ttf", date_stamp_height_px)
    img = Image.open(fname)
    img = ImageOps.expand(img,border=date_stamp_height_px,fill=0)
    img = img.crop((date_stamp_height_px,
                    0,
                    img.size[0] - date_stamp_height_px,
                    img.size[1]))
    img_editable = ImageDraw.Draw(img)
    img_editable.text((date_stamp_height_px, date_stamp_height_px * 0.1), 
                        date_stamp_string,
                        (248, 252, 248),
                        date_stamp_font)
    img.save(fname)



def keysight_screenshot(fname, connection):

    try:
        connection.write('save:image:format PNG')
        connection.write(':hardcopy:inksaver 0')
        connection.write(":disp:menu off")
        connection.write(":disp:mess:cle")
        # connection.write('save:image')
    except:
        raise IOError("Unable to connect to scope")



    connection.write(":DISP:DATA? PNG,COL")
    image_data = connection.read_raw()[10:]

    print(f"Saving image to {fname}")
    with open(fname, "wb") as fout:
        fout.write(image_data)

def agilent_screenshot(fname, connection):

    try:
        connection.write(':hardcopy:inksaver 0')
        connection.write(":DISP:DATA?")
        image_data = connection.read_raw()[10:]
    except:
        raise IOError("Unable to connect to scope")

    print(f"Saving image to {fname}")
    with open(fname, "wb") as fout:
        fout.write(image_data)






if __name__ == '__main__':
    main(sys.argv)