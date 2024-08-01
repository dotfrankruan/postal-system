#!/usr/bin/env python3
import sys
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import tempfile

camera_index = 2


def bc_scan_barcode(frame):
    # Convert frame to PIL Image
    pil_image = Image.fromarray(frame)
    
    # Decode the barcode
    decoded_objects = decode(pil_image)
    barcode_detected = False

    for obj in decoded_objects:
        barcode_type = obj.type
        barcode_data = obj.data.decode('utf-8')
        #print(f"Detected Barcode Type: {barcode_type}")
        #print(f"Barcode Data: {barcode_data}")
        barcode_detected = True

        # Draw a rectangle around the barcode
        points = obj.polygon
        if len(points) > 4: 
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            points = hull
        n = len(points)
        for j in range(0, n):
            pt1 = (points[j].x, points[j].y)
            pt2 = (points[(j+1) % n].x, points[(j+1) % n].y)
            cv2.line(frame, pt1, pt2, (255,0,0), 3)
        return barcode_data
    return None

def bc_list_cameras(max_tested=10):
    available_cameras = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            available_cameras.append(i)
            cap.release()
    return available_cameras

def bc_main(camera_index):
    # print("Detecting cameras...")
    # cameras = list_cameras()
    # if not cameras:
    #     print("No cameras found. Please connect a camera and try again.")
    #     return

    # print(f"Available Cameras: {cameras}")
    # camera_index = int(input("Enter the number of the camera you want to use: "))

    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if ret:
            barcode_data = bc_scan_barcode(frame)
            cv2.imshow('Barcode Scanner', frame)

            if barcode_data:
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return barcode_data # Return the barcode

# print("Detecting cameras...")
# cameras = list_cameras()
# if not cameras:
#     print("No cameras found. Please connect a camera and try again.")
# print(f"Available Cameras: {cameras}")
# camera_index = int(input("Enter the number of the camera you want to use: "))
# print(bc_main(camera_index))

def scan_barcode(camera_index):
    while True:
        try:
            number = bc_main(camera_index)
        except AttributeError:
            continue
        break
    return number

def check_registration(number):
    """Currently it's only valid for China's Mainland domestic ones, I don't know other countries/regions."""
    try:
        int(number)
    except:
        return True
    return False

def get_region(region_code):
    if region_code == "CN":
        return "Mainland China"
    elif region_code == "DE":
        return "Germany"
    elif region_code == "RU":
        return "Russia"
    elif region_code == "IN":
        return "India"
    elif region_code == "FR":
        return "France"
    elif region_code == "FI":
        return "Finland"
    elif region_code == "LT":
        return "Lithuania"
    elif region_code == "US":
        return "United States"
    elif region_code == "GB":
        return "United Kingdom"
    elif region_code == "HK":
        return "Hong Kong"
    elif region_code == "TW":
        return "Taiwan"
    elif region_code == "JP":
        return "Japan"
    elif region_code == "DE":
        return "Germany"
    else:
        raise NotImplementedError("CURRENT REGION IS NOT IMPLEMENTED")
    # TODO: TO BE FINISHED

def makedir(barcode, country, mailtype, detailed_region=""):
    if detailed_region == "":
        dirname = country + "/" + mailtype + "/" + str(barcode)
        os.mkdir(dirname)
    else:
        dirname = country + "/" + mailtype + "/" + str(barcode) + " (" + str(detailed_region) + ")"
        os.mkdir(dirname)
    return dirname

device = 'hpaio:/net/Smart_Tank_510_series?ip=10.10.0.200'
mode = 'Color'
outfmt = 'tiff' # By default

def test_scan(x, y, dpi=75, extn="png"):
    if x == None and y == None:
        xyprovided = False
    else:
        xyprovided = True
    with tempfile.TemporaryDirectory() as tmpdir:
        if not xyprovided:
            os.system("scanimage --format {} -d '{}' --mode {} --resolution {} -p -o {}".format(extn, device, mode, str(dpi), tmpdir + "/sample.{}".format(extn)))
        else:
            os.system("scanimage --format {} -d '{}' --mode {} --resolution {} -p -x {} -y {} -o {}".format(extn, device, mode, str(dpi), str(x), str(y), tmpdir + "/sample.{}".format(extn)))
        os.system("xdg-open {}/sample.{}".format(tmpdir, extn))
        option = input("Valid scan? (y/n)")
        if option == 'n':
            return False
        else:
            return True
    
def actual_scan(x, y, outfile, dpi, extn):
    extn = extn.lower()
    if x == None and y == None:
        xyprovided = False
    else:
        xyprovided = True
    if not xyprovided:
        os.system('scanimage --format {} -d "{}" --mode {} --resolution {} -p -o "{}"'.format(extn, device, mode, str(dpi), outfile))
        print("INFO: FILE SAVED TO ", outfile)
    else:
        os.system('scanimage --format {} -d "{}" --mode {} --resolution {} -p -x {} -y {} -o "{}"'.format(extn, device, mode, str(dpi), str(x), str(y), outfile))
        print("INFO: FILE SAVED TO ", outfile)
    os.system("xdg-open {}".format(outfile))

dir_made = False

# THIS WILL BE A CLI PROGRAM
print("WELCOME TO THE POSTAL MANAGEMENT SYSTEM")
while True:
    command = input(">> ")
    command = command.upper()
    commands = command.split()
    root_command = commands[0]
    if root_command == "BARCODE":
        try:
            str(barcode)
        except NameError: # That means barcode is not defined yet, which is good
            if commands[1] == "SCAN":
                barcode = scan_barcode(camera_index)
            else:
                barcode = commands[1]
            continue
        print("WARNING: BARCODE IS ALREADY SPECIFIED")
        print("         YOU MAY START A NEW SESSION")
    elif root_command == "SHOW":
        try:
            print("BARCODE: {}".format(barcode))
            print("REGISTRATION: {}".format(registration))
            print("COUNTRIES/REGIONS: {}".format(region))
            print("MAIL TYPE: {}".format(mailtype))
            try:
                print("DETAILED REGION: {}".format(detailed_region_text))
            except NameError:
                pass
        except NameError as err:
            print(err)
    elif root_command == "REGISTRATION":
        try:
            registration = check_registration(barcode)
        except NameError:
            registration = bool(commands[1])
    elif root_command == "REGION":
        try:
            if registration == True:
                region = barcode[-2:]
                print("REGION DETECTED, IT IS {}".format(region.upper()))
            else:
                try:
                    region = commands[1].upper()
                    # print(region)
                    if len(region) > 2:
                        print("WARNING: YOU SHALL USE ISO-3266-1 ALPHA 2 TO ENTER YOUR REGION CODE")
                        continue
                except IndexError:
                    print("WARNING: NO REGION PROVIDED")
                    continue
        except:
            try:
                region = commands[1].upper()
                if len(region) > 2:
                    print("WARNING: YOU SHALL USE ISO-3266-1 ALPHA 2 TO ENTER YOUR REGION CODE")
                    continue
            except IndexError:
                print("WARNING: NO REGION PROVIDED")
                continue
    elif root_command == "DETREG":
        detailed_region_text = ""
        detailed_region_raw = commands[1:]
        detailed_region = []
        for i in detailed_region_raw:
            detailed_region.append(i.title())
        for i in detailed_region:
            detailed_region_text += i
            detailed_region_text += " "
        detailed_region_text = detailed_region_text.strip()
        # print(detailed_region_text)
    elif root_command == "MKDIR":
        try:
            str(detailed_region_text)
        except NameError: # No detailed region
            detailed_region_text = ""
        try:
            parent_dir = makedir(barcode, get_region(region), mailtype, detailed_region_text)
            dir_made = True
        except NameError as e:
            print(e)
        except FileExistsError as e:
            print(e)
    elif root_command == "TYPE":
        try:
            if commands[1] == "POSTCARD":
                mailtype = "Postcards"
                continue
        except:
            pass
        try:
            if registration == True:
                mailtype = "Registered Mail"
            else:
                mailtype = "Regular Mail"
        except NameError:
            pass
    elif root_command == "QUIT":
        sys.exit(0)
    elif root_command == "SCAN":
        if not dir_made:
            print("WARNING: TARGET DIRECTORY IS NOT MADE YET")
            continue
        # THIS PART IS ADAPTED FROM 'cscan', also written by Frank Ruan
        xyprovided = True
        try:
            x = commands[1]
            y = commands[2]
        except IndexError:
            print("WARNING: NO X/Y AXIS SPECIFIED")
            continue
        try:
            int(x)
            int(y)
        except ValueError:
            print("WARNING: INVALID X/Y AXIS")
            continue
        if x == 0 or y == 0:
            # Full-glass scan
            xyprovided = False
        try:
            dpi = commands[3]
        except IndexError:
            print("WARNING: NO DPI SPECIFIED")
            continue
        try:
            int(dpi)
        except ValueError:
            print("WARNING: INVALID DPI")
            continue
        try:
            filename = commands[4]
        except IndexError:
            print("WARNING: NO FILENAME SPECIFIED")
            continue
        try:
            extn = commands[5]
        except IndexError:
            print("NOTE: NO OUTPUT FORMAT SPECIFIED, DEFAULTING TO {}".format(outfmt))
            extn = outfmt
        filename = parent_dir + "/" + str(filename)
        while True:
            res = test_scan(x, y)
            if not res:
                nx = input("PROVIDE NEW X AXIS, CURRENTLY {}: ".format(str(x)))
                if nx == "":
                    nx = x
                ny = input("PROVIDE NEW Y AXIS, CURRENTLY {}: ".format(str(y)))
                if ny == "":
                    ny = y
                x, y = nx, ny
                continue
            else:
                print("VALID SCAN WITH X={} and Y={}".format(str(x), str(y)))
                actual_scan(x, y, filename, dpi, extn.lower())
                break
        
    else:
        print("WARNING: INVALID COMMAND")
        continue