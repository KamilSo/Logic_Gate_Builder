
from tkinter import *
from PIL import Image,ImageTk

window = Tk()

OR_img = ImageTk.PhotoImage(file  ='Images/OR.png')
label = Label(window,text = 'yes')
label2 = Label(window,image =  OR_img)
label.place(x=1,y=1)
label2.pack(side = 'right')
window.mainloop()