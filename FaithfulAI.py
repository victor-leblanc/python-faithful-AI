import multiprocessing
import os
import png
import subprocess
import sys
import zipfile

CACHE_DIR = 'faithfulAI-cache'
SOFTWARE_NAME = 'ImageResizer-r129.exe'
RESOURCE_PACK = 'FaithfulAI.zip'

def write_help():
	sys.stdout.write('FaithfulAI --archive=<ArchivePath> [--scaling=<ScalingMultiplier>]\n\
		<ArchivePath>\t\tPath to the archive containing the assets to use. It can be a minecraft jar or a resource pack.\n\
		<ScalingMultiplier>\t(Optionnal) Number of times that the upscaling algorithm is applied to the textures. Must be a number greater than zero.\n')

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
				texture_list.append(item_path)
		else:
			analyze_textures(item_path, texture_list)

def expand_texture(texture_path):
	with open(texture_path, 'rb') as texture_file:
		texture = png.Reader(file = texture_file).read()
		texture_grid = list(texture[2])
		byte_per_pixel = len(texture_grid[0]) // texture[0]
		new_texture_width = texture[0] * 3
		new_texture_height = texture[1] * 3
		with open(texture_path.replace('.png', '_.png'), 'wb') as new_texture:
			writer = None
			transparency = byte_per_pixel == (2 if texture[3]['greyscale'] else 4)
			if 'palette' in texture[3]:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'], palette = texture[3]['palette'])
			else:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'])
			writer.write(new_texture, (texture_grid[y % texture[1]] * 3 for y in range(new_texture_height)))
	os.remove(texture_path)
	os.rename(texture_path.replace('.png', '_.png'), texture_path)

def crop_texture(texture_path):
	with open(texture_path, 'rb') as texture_file:
		texture = png.Reader(file = texture_file).read()
		texture_grid = list(texture[2])
		byte_per_pixel = len(texture_grid[0]) // texture[0]
		new_texture_width = texture[0] // 3
		new_texture_height = texture[1] // 3
		with open(texture_path.replace('.png', '_.png'), 'wb') as new_texture:
			writer = None
			transparency = byte_per_pixel == (2 if texture[3]['greyscale'] else 4)
			if 'palette' in texture[3]:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'], palette = texture[3]['palette'])
			else:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'])
			writer.write(new_texture, (texture_grid[new_texture_height + y][new_texture_width * byte_per_pixel:2 * new_texture_width * byte_per_pixel] for y in range(new_texture_height)))
	os.remove(texture_path)
	os.rename(texture_path.replace('.png', '_.png'), texture_path)

def reduce_texture(texture_path):
	with open(texture_path, 'rb') as texture_file:
		texture = png.Reader(file = texture_file).read()
		texture_grid = list(texture[2])
		byte_per_pixel = len(texture_grid[0]) // texture[0]
		new_texture_width = texture[0] // 2
		new_texture_height = texture[1] // 2
		new_texture_grid = []
		for y in range(new_texture_height):
			pixel_row = []
			for x in range(new_texture_width):
				base_pixels = (
					texture_grid[y * 2][x * byte_per_pixel * 2:x * byte_per_pixel * 2 + byte_per_pixel],
					texture_grid[y * 2][(x * 2 + 1) * byte_per_pixel:(x * 2 + 1) * byte_per_pixel + byte_per_pixel],
					texture_grid[y * 2 + 1][x * byte_per_pixel * 2:x * byte_per_pixel * 2 + byte_per_pixel],
					texture_grid[y * 2 + 1][(x * 2 + 1) * byte_per_pixel:(x * 2 + 1) * byte_per_pixel + byte_per_pixel]
				)
				average_pixel = []
				for i in range(len(base_pixels[0])):
					average_pixel.append(sum(pixel[i] for pixel in base_pixels) // 4)
				matching_scores = []
				for pixel in base_pixels:
					matching_score = 0
					for i in range(len(base_pixels[0])):
						matching_score += abs(pixel[i] - average_pixel[i])
					matching_scores.append(matching_score)
				pixel_row.extend(base_pixels[matching_scores.index(min(matching_scores))])
			new_texture_grid.append(pixel_row)				
		with open(texture_path.replace('.png', '_.png'), 'wb') as new_texture:
			writer = None
			transparency = byte_per_pixel == (2 if texture[3]['greyscale'] else 4)
			if 'palette' in texture[3]:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'], palette = texture[3]['palette'])
			else:
				writer = png.Writer(new_texture_width, new_texture_height, alpha = transparency, bitdepth = texture[3]['bitdepth'], greyscale = texture[3]['greyscale'])
			writer.write(new_texture, new_texture_grid)
	os.remove(texture_path)
	os.rename(texture_path.replace('.png', '_.png'), texture_path)

def zip_files(path, zip_ref):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			zip_ref.write(item_path, item_path[len(CACHE_DIR) + 1:])
		else:
			zip_files(item_path, zip_ref)

if __name__ == '__main__':
	settings = {
		'--assets': None,
		'--scaling': '1'
	}
	for argument in sys.argv[1:]:
		is_valid = False
		argument_split = argument.split('=')
		if argument_split[0] in settings:
			settings[argument_split[0]] = argument_split[1]
		else:
			sys.stderr.write('ERROR: \'%s\' is an invalid argument.\n' % argument_split[0])
			write_help()
			sys.exit(1)
	if settings['--assets'] is None:
		sys.stderr.write('ERROR: \'--assets\' is required.\n')
		write_help()
		sys.exit(1)
	try:
		settings['--scaling'] = int(settings['--scaling'])
	except:
		sys.stderr.write('ERROR: \'--scaling\' is invalid, %s is not an int.\n' % (settings['--scaling']))
		write_help()
		sys.exit(1)
	if settings['--scaling'] < 1:
		sys.stderr.write('ERROR: \'--settings\' must be greater than zero.\n')
		write_help()
		sys.exit(1)	

	try:
		os.remove(RESOURCE_PACK)
	except:
		pass
	try:
		empty_cache(CACHE_DIR)
	except:
		pass

	sys.stdout.write('Step 1: Extracting the assets...\n')
	extract_assets(settings['--assets'])
	sys.stdout.write('Done.\nStep 2: Analysing the textures...\n')

	texture_list = []
	analyze_textures(CACHE_DIR, texture_list)
	texture_nb = len(texture_list)
	sys.stdout.write('Done. Found %i %s.\n' % (texture_nb, 'textures' if texture_nb > 1 else 'texture'))

	if texture_nb > 0:
		step_nb = 3
		thread_nb = multiprocessing.cpu_count()
		for i in range(settings['--scaling']):
			sys.stdout.write('Step %i: Expanding the textures...\n' % step_nb)
			progress_count = 0
			process_list = []
			for texture_path in texture_list:
				process_nb = len(process_list)
				while process_nb + 1 == thread_nb:
					i = 0
					while i < process_nb:
						if not process_list[i].is_alive():
							del process_list[i]
							process_nb -= 1
						else:
							i += 1
				process = multiprocessing.Process(target = expand_texture, args = (texture_path,))
				process.start()
				process_list.append(process)
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
				sys.stdout.flush()
			sys.stdout.write('Waiting for the processes to finish...\n')
			progress_count = 0
			for process in process_list:
				process.join()
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%' % (progress_count / len(process_list) * 100))
				sys.stdout.flush()
			step_nb += 1
			sys.stdout.write('Done.\nStep %i: Applying the upscaling algorithm...\n' % step_nb)

			cmd = SOFTWARE_NAME
			progress_count = 0
			process_list = []
			for texture_path in texture_list:
				texture_cmd = ' /load \"%s\" /resize auto \"%s\" /save \"%s\"' % (texture_path, 'XBR 4x <NoBlend>', texture_path.replace('.png', '_.png'))
				if len(cmd) + len(texture_cmd) > 4096:
					process_list.append(subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True))
					sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
					sys.stdout.flush()
					cmd = SOFTWARE_NAME
				cmd += texture_cmd
				progress_count += 1
			if cmd != SOFTWARE_NAME:
				process_list.append(subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True))
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
				sys.stdout.flush()
			sys.stdout.write('Waiting for the processes to finish...\n')
			progress_count = 0
			for process in process_list:
				process.communicate()
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / len(process_list) * 100))
				sys.stdout.flush()
			step_nb += 1
			sys.stdout.write('Done.\nStep %i: Organizing the textures...\n' % step_nb)

			progress_count = 0
			for texture_path in texture_list:
				os.remove(texture_path)
				os.rename(texture_path.replace('.png', '_.png'), texture_path)
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
				sys.stdout.flush()
			step_nb += 1
			sys.stdout.write('Done.\nStep %i: Croping the results...\n' % step_nb)

			progress_count = 0
			process_list = []
			for texture_path in texture_list:
				process_nb = len(process_list)
				while process_nb + 1 == thread_nb:
					i = 0
					while i < process_nb:
						if not process_list[i].is_alive():
							del process_list[i]
							process_nb -= 1
						else:
							i += 1
				process = multiprocessing.Process(target = crop_texture, args = (texture_path,))
				process.start()
				process_list.append(process)
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
				sys.stdout.flush()
			sys.stdout.write('Waiting for the processes to finish...\n')
			progress_count = 0
			for process in process_list:
				process.join()
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / len(process_list) * 100))
				sys.stdout.flush()
			step_nb += 1
			sys.stdout.write('Done.\nStep %i: Polishing the textures...\n' % step_nb)

			progress_count = 0
			process_list = []
			for texture_path in texture_list:
				process_nb = len(process_list)
				while process_nb + 1 == thread_nb:
					i = 0
					while i < process_nb:
						if not process_list[i].is_alive():
							del process_list[i]
							process_nb -= 1
						else:
							i += 1
				process = multiprocessing.Process(target = reduce_texture, args = (texture_path,))
				process.start()
				process_list.append(process)
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / texture_nb * 100))
				sys.stdout.flush()
			sys.stdout.write('Waiting for the processes to finish...\n')
			progress_count = 0
			for process in process_list:
				process.join()
				progress_count += 1
				sys.stdout.write('Progress: %.2f%%\n' % (progress_count / len(process_list) * 100))
				sys.stdout.flush()
			step_nb += 1
			sys.stdout.write('Done.\n')

		sys.stdout.write('Step %i: Creating the resource pack...\n' % step_nb)
		with open('%s/pack.mcmeta' % CACHE_DIR, 'w') as meta_file:
			meta_file.write('{\"pack\": {\"pack_format\": 5, \"description\": \"FaithfulAI, the first fully generated resource pack.\"}}')
		with zipfile.ZipFile(RESOURCE_PACK, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
			zip_files(CACHE_DIR, zip_ref)
		sys.stdout.write('Done.')
	
	try:
		empty_cache(CACHE_DIR)
	except:
		pass
	try:
		os.rmdir(CACHE_DIR)
	except:
		pass
	sys.exit(0)