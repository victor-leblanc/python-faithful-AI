import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import os

from src.config import Config
from src.language import Language
from src.utility import Utility

class Window(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('FaithfulAI')
		self.setFixedSize(640, 360)
		self.windowLayout = QtWidgets.QVBoxLayout(self)

		self.sourceCategoryFrame = QtWidgets.QFrame(self)
		self.sourceCategoryFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.sourceCategoryFrame.setFrameShadow(QtWidgets.QFrame.Raised)
		self.sourceCategoryFrameLayout = QtWidgets.QVBoxLayout(self.sourceCategoryFrame)
		self.sourceCategoryLabel = QtWidgets.QLabel(self.sourceCategoryFrame, text = Language.GUI[Config.LANGUAGE]['SOURCE_CATEGORY'])
		self.sourceCategoryFrameLayout.addWidget(self.sourceCategoryLabel)
		self.sourceCategoryButton1 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['MINECRAFT_VERSION'], self.sourceCategoryFrame)
		self.sourceCategoryButton1.clicked.connect(lambda: self.updateSourcePathDropdown('MINECRAFT_VERSION'))
		self.sourceCategoryFrameLayout.addWidget(self.sourceCategoryButton1)
		self.sourceCategoryButton2 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['RESOURCE_PACK'], self.sourceCategoryFrame)
		self.sourceCategoryButton2.clicked.connect(lambda: self.updateSourcePathDropdown('RESOURCE_PACK'))
		self.sourceCategoryFrameLayout.addWidget(self.sourceCategoryButton2)
		self.windowLayout.addWidget(self.sourceCategoryFrame)

		self.sourcePathFrame = QtWidgets.QFrame(self)
		self.sourcePathFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.sourcePathFrame.setFrameShadow(QtWidgets.QFrame.Raised)
		self.sourcePathFrameLayout = QtWidgets.QVBoxLayout(self.sourcePathFrame)
		self.sourcePathLabel = QtWidgets.QLabel(self.sourcePathFrame, text = Language.GUI[Config.LANGUAGE]['SOURCE_FILE'])
		self.sourcePathFrameLayout.addWidget(self.sourcePathLabel)
		self.sourcePathDropdown = QtWidgets.QComboBox(self.sourcePathFrame)
		self.sourcePathFrameLayout.addWidget(self.sourcePathDropdown)
		self.windowLayout.addWidget(self.sourcePathFrame)

		self.upscalingButton = QtWidgets.QPushButton(Language.GUI[Config.LANGUAGE]['START_UPSCALING'], self)
		self.upscalingButton.clicked.connect(lambda: self.startUpscaling())
		self.windowLayout.addWidget(self.upscalingButton)

	def displayError(self, errorText):
		errorWindow = QtWidgets.QMessageBox()
		errorWindow.setIcon(QtWidgets.QMessageBox.Critical)
		errorWindow.setText(errorText)
		errorWindow.setWindowTitle(Language.ERROR[Config.LANGUAGE]['ERROR'])
		errorWindow.exec_()

	def startUpscaling(self):
		sourcePath = None
		try:
			sourcePath = self.sourcePathList[self.sourcePathDropdown.currentIndex()]
		except:
			self.displayError(Language.ERROR[Config.LANGUAGE]['NO_FILE_SELECTED'])
			return
		

	def updateSourcePathDropdown(self, sourceCategory):
		self.sourcePathList = []
		if sourceCategory == 'MINECRAFT_VERSION':
			Utility.scan_folder(self.sourcePathList, '%s/versions' % Config.MINECRAFT_DIRECTORY, 'jar')
		else:
			Utility.scan_folder(self.sourcePathList, '%s/resourcepacks' % Config.MINECRAFT_DIRECTORY, 'zip')
		self.sourcePathDropdown.clear()
		for sourcePath in self.sourcePathList:
			self.sourcePathDropdown.addItem('.minecraft%s' % Utility.normalize_path(sourcePath).split('.minecraft')[1])