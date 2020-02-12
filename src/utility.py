import os

class Utility:
	@staticmethod
	def normalize_path(path):
		return path.replace('/', '\\') if os.name == 'nt' else path.replace('\\', '/')

	@staticmethod
	def scan_folder(file_list, folder_path, extension = None):
		for item in os.listdir(folder_path):
			item_path = os.path.join(folder_path, item)
			if os.path.isfile(item_path):
				if extension is None or item_path.endswith('.%s' % extension):
					file_list.append(item_path)
			else:
				Utility.scan_folder(file_list, item_path, extension)