import os
import subprocess

from src.config import Config
from src.language import Language

class Upscaler:
	def __init__(self):
		self.command = Config.UPSCALER
		self.process_list = []
		try:
			os.rename('./src/upscaler/%s' % Config.UPSCALER, './%s' % Config.UPSCALER)
		except:
			raise Exception(Language.ERROR[Config.LANGUAGE]['UPSCALER_UNIQUE'])
	
	def __del__(self):
		os.rename('./%s' % Config.UPSCALER, './src/upscaler/%s' % Config.UPSCALER)

	def upscale(self, texture):
		texture_command = ' /load \"%s\" /resize auto \"XBR 4x <NoBlend>\" /save \"%s\"' % (texture.path, texture.path.replace('.png', '.tmp.png'))
		if len(self.command) + len(texture_command) > 4096:
			self.process_list.append(subprocess.Popen(self.command, stdout = subprocess.PIPE, shell = True))
			self.command = Config.UPSCALER
		self.command += texture_command
	
	def wait(self):
		if self.command != Config.UPSCALER:
			self.process_list.append(subprocess.Popen(self.command, stdout = subprocess.PIPE, shell = True))
			self.command = Config.UPSCALER
		while len(self.process_list) > 0:
			self.process_list[0].communicate()
			del self.process_list[0]