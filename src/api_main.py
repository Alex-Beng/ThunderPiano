import time
from queue import Queue
from threading import Lock, Thread

import cv2
import numpy as np

from adbutils import adb
import scrcpy


xy_queue = Queue()
lock = Lock()

def on_queue():
    global xy_queue
    while True:
        try:
            lock.acquire()
            # if xy_queue.qsize() == 2:
            if xy_queue.qsize():
                while not xy_queue.empty():
                    x,y = xy_queue.get()
                    client.control.touch(x, y, scrcpy.ACTION_DOWN)
                    client.control.touch(x, y, scrcpy.ACTION_UP)
        finally:
            lock.release()
        time.sleep(0.00001)


b_rows = [0.60, 0.47, 0.25, 0.1]
# b_rows = [0.75, 0.60]

colors = [(0,0,255),(0,255,0),(255,0,0), (255,255,0)]

def on_frame(frame):
    global xy_queue
    if frame is not None:
        try:
            lock.acquire()
            if xy_queue.empty():
                row, col, _ = frame.shape
                t_row = int(row*0.81)
                for i,b in enumerate(b_rows):
                    b_row = int(row*b)
                    for c in range(0, col, col//10):
                        if np.sum(frame[b_row, c]) < 100:
                            x = c+5
                            y = t_row
                            xy_queue.put((x,y))
                            frame = cv2.circle(frame, (x,b_row), 10, colors[i], 5)
                            break
        finally:
            lock.release()

        cv2.imshow("cao", frame)
        cv2.waitKey(1)



def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)
        client.control.touch(x, y, scrcpy.ACTION_DOWN)
        client.control.touch(x, y, scrcpy.ACTION_UP)

device = adb.device()

client = scrcpy.Client(
            max_width=250, device=device)

client.add_listener(scrcpy.EVENT_FRAME, on_frame)
cv2.namedWindow("cao")
cv2.setMouseCallback("cao", on_mouse)

Thread(target=on_queue).start()
client.start()


