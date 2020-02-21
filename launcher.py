import multiprocessing
import PyQt5.QtWidgets as QtWidgets
import sys

from src.config import Config
from src.utility import Utility
from src.window import Window

if __name__ == '__main__':
	multiprocessing.freeze_support()
	try:
		Utility.delete_folder(Config.CACHE)
	except:
		pass
	application = QtWidgets.QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(application.exec_())