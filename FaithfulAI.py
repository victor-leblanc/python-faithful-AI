import PyQt5.QtWidgets as QtWidgets
import sys

from src.window import Window

if __name__ == '__main__':
	application = QtWidgets.QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(application.exec_())