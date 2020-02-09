import os
import png
import sys
import zipfile

CACHE_DIR = 'faithfulAI-cache'
SOFTWARE_NAME = 'ImageResizer-r129.exe'
RESOURCE_PACK = 'FaithfulAI.zip'

def empty_cache(path):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			os.remove(item_path)
		else:
			empty_cache(item_path)
			os.rmdir(item_path)

def extract_assets(path):
	with zipfile.ZipFile(path, 'r') as zip_ref:
		for item in zip_ref.namelist():
			if item.startswith('assets') and (item.endswith('.mcmeta') or item.endswith('.png')) and \
				not item.startswith('assets/minecraft/textures/colormap') and \
				not item.startswith('assets/minecraft/textures/gui/title/background'):
				zip_ref.extract(item, CACHE_DIR)

def analyze_textures(path, texture_list):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			if item_path.endswith('.png'):
				is_transparent = False
				with open(item_path, 'rb') as texture_file:
					texture = png.Reader(file = texture_file).read()
					if 'palette' in texture[3]:
						for sample in texture[3]['palette']:
							if len(sample) != 4:
								break
							elif sample[3] == 0:
								is_transparent = True
								break
					else:
						for pixel_row in texture[2]:
							if len(pixel_row) // 4 != texture[0]:
								break
							for i in range(3, len(pixel_row), 4):
								if pixel_row[i] == 0:
									is_transparent = True
									break
							if is_transparent:
								break
				texture_list.append({
					'path': item_path,
					'transparent': is_transparent
				})
		else:
			analyze_textures(item_path, texture_list)

def expand_texture(texture_data):
	with open(texture_data['path'], 'rb') as texture_file:
		texture = png.Reader(file = texture_file).read()
		texture_grid = list(texture[2])
		byte_per_pixel = len(texture_grid[0]) // texture[0]
		new_texture_width = texture[0] * 3
		new_texture_height = texture[1] * 3
		new_texture_grid = []
		for y in range(new_texture_height):
			pixel_row = []
			for x in range(new_texture_width * byte_per_pixel):
				pixel_row.append(texture_grid[y % texture[1]][x % (texture[0] * byte_per_pixel)])
			new_texture_grid.append(pixel_row)
		with open(texture_data['path'].replace('.png', '_.png'), 'wb') as new_texture:
			writer = None
			if 'palette' in texture[3]:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = texture_data['transparent'], bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'], palette = texture[3]['palette'])
			else:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = byte_per_pixel == (2 if texture[3]['greyscale'] else 4), bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'])
			writer.write(new_texture, new_texture_grid)
	os.remove(texture_data['path'])
	os.rename(texture_data['path'].replace('.png', '_.png'), texture_data['path'])

def crop_texture(texture_data):
	with open(texture_data['path'], 'rb') as texture_file:
		texture = png.Reader(file = texture_file).read()
		texture_grid = list(texture[2])
		byte_per_pixel = len(texture_grid[0]) // texture[0]
		new_texture_width = texture[0] // 3
		new_texture_height = texture[1] // 3
		new_texture_grid = []
		for y in range(new_texture_height):
			pixel_row = []
			for x in range(new_texture_width * byte_per_pixel):
				pixel_row.append(texture_grid[new_texture_height + y][new_texture_width * byte_per_pixel + x])
			new_texture_grid.append(pixel_row)
		with open(texture_data['path'].replace('.png', '_.png'), 'wb') as new_texture:
			writer = None
			if 'palette' in texture[3]:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = texture_data['transparent'], bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'], palette = texture[3]['palette'])
			else:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = byte_per_pixel == (2 if texture[3]['greyscale'] else 4), bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'])
			writer.write(new_texture, new_texture_grid)
	os.remove(texture_data['path'])
	os.rename(texture_data['path'].replace('.png', '_.png'), texture_data['path'])

def zip_files(path, zip_ref):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			zip_ref.write(item_path, item_path[len(CACHE_DIR) + 1:])
		else:
			zip_files(item_path, zip_ref)

if __name__ == '__main__':
	source_file = sys.argv[1]
	try:
		scaling_multiplier = int(sys.argv[2])
	except:
		scaling_multiplier = 1
	try:
		os.remove(RESOURCE_PACK)
	except:
		pass
	try:
		empty_cache(CACHE_DIR)
	except:
		pass
	extract_assets(source_file)
	texture_list = []
	analyze_textures(CACHE_DIR, texture_list)
	texture_nb = len(texture_list)
	print('Found %i %s.' % (texture_nb, 'textures' if texture_nb > 1 else 'texture'))
	if texture_nb > 0:
		step_nb = texture_nb * scaling_multiplier
		progress_count = 0
		for i in range(scaling_multiplier):
			cmd = SOFTWARE_NAME
			for texture_data in texture_list:
				if not texture_data['transparent']:
					expand_texture(texture_data)
				texture_cmd = ' /load \"%s\" /resize auto \"%s\" /save \"%s\"' % (texture_data['path'], 'EPXB' if texture_data['transparent'] else 'XBR 2x <NoBlend>', texture_data['path'].replace('.png', '_.png'))
				if len(cmd) + len(texture_cmd) > 4096:
					os.popen(cmd)
					cmd = SOFTWARE_NAME
					print('Progress: %.2f%%' % (progress_count / step_nb * 100))
				cmd += texture_cmd
				progress_count += 1
			if cmd != SOFTWARE_NAME:
				os.popen(cmd)
			for texture_data in texture_list:
				os.remove(texture_data['path'])
				os.rename(texture_data['path'].replace('.png', '_.png'), texture_data['path'])
				if not texture_data['transparent']:
					crop_texture(texture_data)
		with open('%s/pack.mcmeta' % CACHE_DIR, 'w') as meta_file:
			meta_file.write('{\"pack\": {\"pack_format\": 5, \"description\": \"FaithfulAI, the first fully generated resource pack.\"}}')
		with zipfile.ZipFile(RESOURCE_PACK, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
			zip_files(CACHE_DIR, zip_ref)
	try:
		empty_cache(CACHE_DIR)
	except:
		pass
	try:
		os.rmdir(CACHE_DIR)
	except:
		pass