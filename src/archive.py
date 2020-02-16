import os
import zipfile

from src.config import Config

class Archive:
	def __init__(self, path):
		self.path = path
	
	def extract(self, destination_path, extension_list = None, exception_list = None, folder_list = None):
		file_nb = 0
		with zipfile.ZipFile(self.path, 'r') as zip_ref:
			for item in zip_ref.namelist():
				if (extension_list is None or any(item.endswith(extension) for extension in extension_list)) and \
					(exception_list is None or not any(item.startswith(exception) for exception in exception_list)) and \
					(folder_list is None or any(item.startswith(folder) for folder in folder_list)):
					zip_ref.extract(item, destination_path)
					file_nb += 1
		return file_nb
	
	def generate(self, origin_path, destination_path = None):
		if destination_path is None:
			destination_path = self.path
		file_nb = [0]
		with zipfile.ZipFile(destination_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
			self.__generate(origin_path, zip_ref, file_nb)
		return file_nb[0]
	
	def __generate(self, origin_path, archive_file, file_nb, progress_path = None):
		if progress_path is None:
			progress_path = origin_path
		for item in os.listdir(progress_path):
			item_path = os.path.normpath(os.path.join(progress_path, item))
			if os.path.isfile(item_path):
				archive_file.write(item_path, item_path[len(origin_path) + 1:])
				file_nb[0] += 1
			else:
				self.__generate(origin_path, archive_file, file_nb, item_path)