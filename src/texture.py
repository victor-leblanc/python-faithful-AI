import os
import png

from src.config import Config
from src.language import Language
from src.pixel import Pixel

class Texture:
	def __init__(self, path):
		self.attribute = {}
		self.category = path.split(Config.CACHE)[1].split('textures')[1].split(os.path.sep)[1]
		self.name = path.split(os.path.sep)[-1]
		self.path = path
		self.load()

	def crop(self, factor = 3):
		if factor > 1:
			self.size[0] //= factor
			self.size[1] //= factor			
			self.grid = [self.grid[self.size[1] + y][self.size[0]:2 * self.size[0]] for y in range(self.size[1])]

	def downscale(self, factor = 2, smooth = False):
		if factor > 1:
			self.size[0] //= factor
			self.size[1] //= factor
			grid = []
			for y in range(self.size[1]):
				row = []
				for x in range(self.size[0]):
					pixel_group = []
					for y_offset in range(factor):
						for x_offset in range(factor):
							pixel_group.append(self.grid[y * factor + y_offset][x * factor + x_offset])
					average_pixel_data = []
					for i in range(4):
						average_pixel_data.append(sum(pixel.as_list()[i] for pixel in pixel_group) // len(pixel_group))
					average_pixel = Pixel(average_pixel_data)
					if smooth:
						average_pixel.a //= 128
						row.append(average_pixel)
					else:
						matching_pixel = pixel_group[0]
						for pixel in pixel_group[1:]:
							if pixel.match(average_pixel) > matching_pixel.match(average_pixel):
								matching_pixel = pixel
						row.append(matching_pixel)
				grid.append(row)
			self.grid = grid

	def duplicate(self, factor = 3):
		if factor > 1:
			self.size[0] *= factor
			self.size[1] *= factor
			self.grid = [self.grid[y % len(self.grid)] * factor for y in range(self.size[1])]

	def expand(self, factor = 2):
		if factor > 1:
			grid = []
			for y in range(self.size[1]):
				row = []
				for x in range(self.size[0]):
					for i in range(factor):
						row.append(self.grid[y][x])
				for i in range(factor):
					grid.append(row)
			self.grid = grid
			self.size[0] *= factor
			self.size[1] *= factor

	def is_masked(self):
		if 'IS_MASKED' in self.attribute:
			return self.attribute['IS_MASKED']
		self.attribute['IS_MASKED'] = self.category == 'entity'
		return self.attribute['IS_MASKED']			

	def is_tiled(self):
		if 'IS_TILED' in self.attribute:
			return self.attribute['IS_TILED']
		match_count = 0
		match_total = 0
		for x in range(self.size[0]):
			if self.grid[0][x].a == self.grid[self.size[1] - 1][x].a == 255:
				match_count += 1
			match_total += 1
		for y in range(self.size[1]):
			if self.grid[y][0].a == self.grid[y][self.size[0] - 1].a == 255:
				match_count += 1
			match_total += 1
		self.attribute['IS_TILED'] = match_count / match_total > 0.3
		return self.attribute['IS_TILED']	

	def load(self):
		with open(self.path, 'rb') as texture_file:
			texture = png.Reader(file = texture_file).asRGBA8()
			self.grid = [[Pixel(row[x:x + 4]) for x in range(0, len(row), 4)] for row in texture[2]]
			self.size = list(texture[:2])

	def mask(self):
		mask_texture = Texture(self.path.replace('.png', '.mask.png'))
		factor = self.size[0] // mask_texture.size[0]
		if factor != int(factor) or self.size[1] / mask_texture.size[1] != factor:
			raise Exception(Language.ERROR[Config.LANGUAGE]['INVALID_MASK'] % self.name)
		mask_texture.expand(factor = factor)
		for y in range(self.size[1]):
			for x in range(self.size[0]):
				if self.grid[y][x].a == 0 and mask_texture.grid[y][x].a == 255:
					self.grid[y][x] = mask_texture.grid[y][x]

	def merge(self):
		os.remove(self.path)
		os.rename(self.path.replace('.png', '.tmp.png'), self.path)		

	def save(self, keep_mask = False):
		grid = []
		for y in range(self.size[1]):
			row = []
			for x in range(self.size[0]):
				row.extend(self.grid[y][x].as_list())
			grid.append(row)
		tmp_path = self.path.replace('.png', '.tmp.png')
		png.from_array(grid, 'RGBA;8').save(tmp_path)
		if keep_mask:
			os.rename(self.path, self.path.replace('.png', '.mask.png'))
		else:
			os.remove(self.path)
		os.rename(tmp_path, self.path)