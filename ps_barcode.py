#!/usr/bin/env python3
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image

def scan_barcode(frame):
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

def list_cameras(max_tested=10):
    available_cameras = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            available_cameras.append(i)
            cap.release()
    return available_cameras

def main(camera_index):
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
            barcode_data = scan_barcode(frame)
            cv2.imshow('Barcode Scanner', frame)

            if barcode_data:
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return barcode_data # Return the barcode

if __name__ == '__main__':
    # main() # Commented out, not meant for direct execution.
    print("Not meant for direct execution.")