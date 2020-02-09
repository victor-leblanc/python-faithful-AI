import multiprocessing
import os
import png
import sys
import zipfile

CACHE_DIR = 'faithfulAI-cache'
SOFTWARE_NAME = 'ImageResizer-r129.exe'
RESOURCE_PACK = 'FaithfulAI.zip'

#Manage program arguments
source_file = sys.argv[1]
try:
	scaling_multiplier = int(sys.argv[2])
except:
	scaling_multiplier = 1

#Delete resource pack and empty previous cache
try:
	os.remove(RESOURCE_PACK)
except:
	pass
def empty_cache(path):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			os.remove(item_path)
		else:
			empty_cache(item_path)
			os.rmdir(item_path)
try:
	empty_cache(CACHE_DIR)
except:
	pass

#Extract minecraft textures
with zipfile.ZipFile(sys.argv[1], 'r') as zip_ref:
	print("Extracting assets...")
	for item in zip_ref.namelist():
		if item.startswith('assets') and (item.endswith('.mcmeta') or item.endswith('.png')) and \
			not item.startswith('assets/minecraft/textures/colormap') and \
			not item.startswith('assets/minecraft/textures/gui/title/background'):
			zip_ref.extract(item, CACHE_DIR)

#List texture paths
def find_textures(path, texture_list):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			if item_path.endswith('.png'):
				texture_list.append(item_path)
		else:
			find_textures(item_path, texture_list)
texture_list = []
find_textures(CACHE_DIR, texture_list)
texture_nb = len(texture_list)
print("Found %i textures." % texture_nb)

#Generate and execute the command
progress_count = 0
step_nb = texture_nb * scaling_multiplier
for i in range(scaling_multiplier):
	print("Progress: %i/%i (%.2f%%)" % (progress_count, step_nb, progress_count / step_nb * 100))
	cmd = SOFTWARE_NAME
	for texture_path in texture_list:
		texture_cmd = ' /load \"%s\" /resize auto ' % texture_path
		with open(texture_path, 'rb') as texture_file:
			texture = png.Reader(file = texture_file).read()
			has_transparent_pixel = False
			if 'palette' in texture[3]:
				for sample in texture[3]['palette']:
					if len(sample) != 4:
						break
					elif sample[3] == 0:
						has_transparent_pixel = True
						break
			else:
				for pixel_row in texture[2]:
					if len(pixel_row) // 4 != texture[0]:
						break
					for i in range(3, len(pixel_row), 4):
						if pixel_row[i] == 0:
							has_transparent_pixel = True
							break
					if has_transparent_pixel:
						break
			texture_cmd += '\"EPXB\"' if has_transparent_pixel else '\"XBR 2x <NoBlend>\"'
		texture_cmd += ' /save \"%s\"' % texture_path.replace('.png', '_.png')
		if len(cmd) + len(texture_cmd) > 4096:
			os.popen(cmd)
			print("Progress: %i/%i (%.2f%%)" % (progress_count, step_nb, progress_count / step_nb * 100))
			cmd = SOFTWARE_NAME
		cmd += texture_cmd
		progress_count += 1
	if cmd != SOFTWARE_NAME:
		os.popen(cmd)
	for texture_path in texture_list:
		os.remove(texture_path)
		os.rename(texture_path.replace('.png', '_.png'), texture_path)
print("Progress: %i/%i (%.2f%%)" % (progress_count, step_nb, progress_count / step_nb * 100))

#Generate resource pack
print("Generating the resource pack...")
with open('%s/pack.mcmeta' % CACHE_DIR, 'w') as meta_file:
	meta_file.write('{"pack": {"pack_format": 5, "description": "FaithfulAI, the first fully generated resource pack."}}')
def zip_files(path, zip_ref):
	for item in os.listdir(path):
		item_path = os.path.join(path, item)
		if os.path.isfile(item_path):
			zip_ref.write(item_path, item_path[len(CACHE_DIR) + 1:])
		else:
			zip_files(item_path, zip_ref)
with zipfile.ZipFile(RESOURCE_PACK, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
	zip_files(CACHE_DIR, zip_ref)

#Delete cache
empty_cache(CACHE_DIR)
os.rmdir(CACHE_DIR)
print("Done!")