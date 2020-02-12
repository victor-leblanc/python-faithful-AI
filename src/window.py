import os
import tkinter

from src.config import Config
from src.language import Language

class Window:
	def __init__(self, master):
		self.master = master
		self.master.title("FaithfulAI")
		self.master.overrideredirect(True)

		self.master.update_idletasks()
		width = 640
		height = 360
		x = (self.master.winfo_screenwidth() // 2) - (width // 2)
		y = (self.master.winfo_screenheight() // 2) - (height // 2)
		self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

		self.source_category = tkinter.StringVar(self.master)
		self.source_category.set('MINECRAFT_VERSION')
		self.source_category_title = tkinter.Label(self.master, text = "Source assets selection:")
		self.source_category_title.pack()
		self.source_category_minecraft_version = tkinter.Radiobutton(self.master, text = 'Minecraft default assets', variable = self.source_category, value = 'MINECRAFT_VERSION', command = self.source_path_dropdown_fill)
		self.source_category_minecraft_version.pack()
		self.source_category_resource_pack = tkinter.Radiobutton(self.master, text = 'Existing resource pack', variable = self.source_category, value = 'RESOURCE_PACK', command = self.source_path_dropdown_fill)
		self.source_category_resource_pack.pack()

		self.source_path = tkinter.StringVar(self.master)
		self.source_path_list = []
		self.source_path_dropdown = tkinter.OptionMenu(self.master, self.source_path, '', *self.source_path_list)
		self.source_path_dropdown.pack()
		self.source_path_dropdown_fill()

		self.close_button = tkinter.Button(master, text = "Close", command = master.quit)
		self.close_button.pack()

	def source_path_dropdown_fill(self):
		self.source_path_list = []
		if self.source_category.get() == 'MINECRAFT_VERSION':
			self.scan_sources('%s/versions' % Config.MINECRAFT_DIRECTORY, 'jar')
		else:
			self.scan_sources('%s/resourcepacks' % Config.MINECRAFT_DIRECTORY, 'zip')
		source_path_dropdown = self.source_path_dropdown['menu']
		source_path_dropdown.delete(0, 'end')
		for source_path in self.source_path_list:
			label = '.minecraft%s' % source_path.split('.minecraft')[1]
			source_path_dropdown.add_command(label = label, command = lambda value = label: self.source_path.set(source_path))

	def scan_sources(self, folder_path, extension = None):
		for item in os.listdir(folder_path):
			item_path = os.path.join(folder_path, item)
			if os.path.isfile(item_path):
				if extension is None or item_path.endswith('.%s' % extension):
					self.source_path_list.append(item_path)
			else:
				self.scan_sources(item_path, extension)