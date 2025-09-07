import cv2

import numpy as np

import mss

import pygetwindow as gw


def get_whatsapp_window():

    try:

        whatsapp_windows = gw.getWindowsWithTitle('WhatsApp')

        if not whatsapp_windows:

            raise Exception("WhatsApp window not found! Make sure WhatsApp is running.")


        window = whatsapp_windows[0]

        print(f"Found window: '{window.title}'")


    except Exception as e:

        print(e)

        exit()


    with mss.mss() as sct:

        while True:

            monitor = {

                "top": window.top,

                "left": window.left,

                "width": window.width,

                "height": window.height

            }


            img = sct.grab(monitor)


            frame = np.array(img)


            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)


       

            cv2.imshow("WhatsApp Capture", frame)

            cv2.imshow("Processed Frame", processed_frame)


            if cv2.waitKey(1) & 0xFF == ord('q'):

                break


    cv2.destroyAllWindows()


if __name__ == "__main__":

    get_whatsapp_window()

