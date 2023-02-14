#!/opt/homebrew/bin/python3

import cv2
from queue import Queue
from sys import argv
from reolinkapi import Camera

_resize = 1024

def display_frame(cam, frame, count):
    if frame is not None:
        print("Frame %5d" % count, end='\r')
        cv2.imshow(cam.ip, frame)

    key = cv2.waitKey(1)
    if key == ord('q') or key == ord('Q') or key == 27:
        cam.stop_stream()
        cv2.destroyAllWindows()
        return False

    return True

def non_blocking(cam):
    frames = Queue(maxsize=30)

    def inner_callback(frame):
        if _resize > 10:
            frames.put(maintain_aspect_ratio_resize(frame, width=_resize))
        else:
            frames.put(frame.copy())

    # t in this case is a thread
    t = cam.open_video_stream(callback=inner_callback)

    counter = 0

    while t.is_alive():
        frame = frames.get()
        counter = counter+1

        if not display_frame(cam, frame, counter):
            break

        if __debug__ and frames.qsize() > 1:
            # Can't consume frames fast enough??
            print("\nQueue: %d" % frames.qsize())



def blocking(cam):
    # stream in this case is a generator returning an image (in mat format)
    stream = cam.open_video_stream()
    counter = 0

    for frame in stream:
        if _resize > 10:
            frame = maintain_aspect_ratio_resize(frame, width=_resize)

        counter = counter + 1

        if not display_frame(cam, frame, counter):
            break;


# Resizes a image and maintains aspect ratio
def maintain_aspect_ratio_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # Grab the image size and initialize dimensions
    dim = None
    (h, w) = image.shape[:2]

    # Return original image if no need to resize
    if width is None and height is None:
        return image

    # We are resizing height if width is none
    if width is None:
        # Calculate the ratio of the height and construct the dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # We are resizing width if height is none
    else:
        # Calculate the ratio of the 0idth and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # Return the resized image
    return cv2.resize(image, dim, interpolation=inter)



if __name__ == "__main__":
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <Camera #>")
        exit(1)

    try:
        host = f"watchdog{argv[1]}"
        cam = Camera(host, username="rtsp", password="darknet")
    except:
        print(f"Failed to open camera: {host}")
        exit(1)

    if not cam.is_logged_in():
        print(f"Login failed for {host}")
        exit(1)

    # Call the methods. Either Blocking (using generator) or Non-Blocking using threads
    non_blocking(cam)
    # blocking(cam)

    print("\nDone.")
