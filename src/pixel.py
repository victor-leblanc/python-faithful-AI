from src.config import Config
from src.language import Language

class Pixel:
	def __init__(self, pixel_data):
		if len(pixel_data) != 4 or not all(0 <= value < 256 for value in pixel_data):
			raise Exception(Language.ERROR[Config.LANGUAGE]['INVALID_PIXEL'] % str(pixel_data))
		self.r = pixel_data[0]
		self.g = pixel_data[1]
		self.b = pixel_data[2]
		self.a = pixel_data[3]

	def as_list(self):
		return self.r, self.g, self.b, self.a

	def average(self, alpha = False, integer = False):
		values = (self.r, self.g, self.b, self.a) if alpha else (self.r, self.g, self.b)
		result = sum(values) / len(values)
		return int(result) if integer else result

	def match(self, pixel, alpha = False):
		return 1 - abs(self.average(alpha = alpha) - pixel.average(alpha = alpha)) / 255