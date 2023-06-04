import tkinter as tk
import time
import PIL, PIL.ImageTk
import cv2
import numpy as np
import ctypes

def padding(array, xx, yy):
    
    dif_height = xx - array.shape[1]
    dif_width = yy - array.shape[0]
    
    array = np.pad(array, ((0, dif_width//2), (0, dif_height//2)), 'constant', constant_values=(0, 0))
    array = np.pad(array, ((dif_width//2, 0), (dif_height//2, 0)), 'constant', constant_values=(0, 0))

    return array

# Getting screen resolution
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
print(f"Screen Resolution (or the maximum resolution supported by the camera): {screensize[0]} x {screensize[1]}")

# Setting capture resolution = screen resolution (is supported)
vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, screensize[0])
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, screensize[1])

flip = True
def flip_video():
    print("Flipping video...")
    global flip
    flip = not flip

thresh_1 = 0
def change_thresh_1_val(value):
    global thresh_1
    thresh_1 = int(value)
    
thresh_2 = 0
def change_thresh_2_val(value):
    global thresh_2
    thresh_2 = int(value)

scale = 1
def change_scale_val(value):
    global scale
    scale = int(value)

window = tk.Tk()

button = tk.Button(
    window,
    text="Flip Video",
    command=flip_video
).grid(row=0, column=0)

tk.Label(window, text="Upper Threshold").grid(row=1, column=0)
slider = tk.Scale(from_=0, to=100, orient=tk.HORIZONTAL, command=change_thresh_1_val)
slider.set(30)
slider.grid(row=1, column=1)

tk.Label(window, text="Lower Threshold").grid(row=2, column=0)
slider2 = tk.Scale(from_=0, to=100, orient=tk.HORIZONTAL, command=change_thresh_2_val)
slider2.set(60)
slider2.grid(row=2, column=1)

tk.Label(window, text="Scale").grid(row=3, column=0)
slider3 = tk.Scale(from_=1, to=10, orient=tk.HORIZONTAL, command=change_scale_val)
slider3.set(10)
slider3.grid(row=3, column=1)

ret, frame = vid.read()
canvas = tk.Canvas(window, width = screensize[0] // 4, height = screensize[1] // 4)
canvas.grid(row=4, column=0, columnspan=2)

black_frame = np.zeros((screensize[1], screensize[0]), dtype=np.uint8)

n_frames = 0

while 1:
    
    if n_frames == 0:
        cv2.imshow('frame', black_frame)
    
    else:
        ret, frame = vid.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_filtered = cv2.bilateralFilter(gray, 10, 40, 40)
        edges_filtered = cv2.Canny(gray_filtered, thresh_1, thresh_2)
        
        edges_filtered = cv2.resize(edges_filtered, (int(edges_filtered.shape[1] * (scale/10)), int(edges_filtered.shape[0] * (scale/10))))
        edges_filtered = padding(edges_filtered, screensize[0], screensize[1])
        
        if flip is True:
            edges_filtered = cv2.flip(edges_filtered, 1)
    
        cv2.imshow('frame', edges_filtered)
        preview = cv2.resize(edges_filtered, (screensize[0] // 4, screensize[1] // 4))
        
        photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(preview))
        canvas.create_image(0, 0, image = photo, anchor = tk.NW)
    
    n_frames = (n_frames + 1) % 10
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    window.update_idletasks()
    window.update()
    
vid.release()
cv2.destroyAllWindows()