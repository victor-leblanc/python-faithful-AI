import sys
import tkinter

from src.window import Window

if __name__ == '__main__':
	root = tkinter.Tk()
	window = Window(root)
	root.mainloop()
	sys.exit(0)