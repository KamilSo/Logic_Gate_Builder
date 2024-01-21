from tkinter import *

window = Tk()
canvas = Canvas(window, bg='black')
canvas.pack(expand=True)

def update_canvas_size(event):
    canvas.config(width=2*event.width, height=event.height)

# Bind the <Configure> event to the window and call the update_canvas_size function
window.bind("<Configure>", update_canvas_size)

window.mainloop()

