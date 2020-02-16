import os
import subprocess

from src.config import Config
from src.texture import Texture

class Utility:
	@staticmethod
	def delete_folder(path):
		for item in os.listdir(path):
			item_path = os.path.join(path, item)
			if os.path.isfile(item_path):
				os.remove(item_path)
			else:
				Utility.delete_folder(item_path)
		os.rmdir(path)

	@staticmethod
	def scan_folder(file_list, folder_path, extension = None):
		for item in os.listdir(folder_path):
			item_path = os.path.join(folder_path, item)
			if os.path.isfile(item_path):
				if extension is None or item_path.endswith('.%s' % extension):
					file_list.append(item_path)
			else:
				Utility.scan_folder(file_list, item_path, extension)
	
	@staticmethod
	def upscale_texture(texturePath):
		texture = Texture(texturePath)
		if texture.is_tiled():
			texture.duplicate()
			texture.save(texture.is_masked())
		elif texture.is_masked():
			texture.save(True)
		subprocess.Popen('%s /load \"%s\" /resize auto \"XBR 4x <NoBlend>\" /save \"%s\"' % (Config.UPSCALER, texture.path, texture.path.replace('.png', '.tmp.png')), stdout = subprocess.PIPE, shell = True).communicate()
		texture.merge()
		texture.load()
		if texture.is_tiled():
			texture.crop()
		texture.downscale()
		if texture.is_masked():
			texture.mask()
			os.remove(texture.path.replace('.png', '.mask.png'))
		texture.save()