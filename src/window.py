import os
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from src.archive import Archive
from src.config import Config
from src.language import Language
from src.texture import Texture
from src.utility import Utility

class Window(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('FaithfulAI')
		self.setFixedSize(500, 350)
		self.windowLayout = QtWidgets.QVBoxLayout(self)

		self.titlePicture = QtWidgets.QLabel(self)
		self.titlePicture.setPixmap(QtGui.QPixmap('assets/logo.png'))
		self.titlePicture.setAlignment(QtCore.Qt.AlignHCenter)
		self.windowLayout.addWidget(self.titlePicture)

		self.sourceFrame = QtWidgets.QFrame(self)
		self.sourceFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.sourceFrameLayout = QtWidgets.QVBoxLayout(self.sourceFrame)
		self.sourceCategoryLabel = QtWidgets.QLabel(self.sourceFrame, text = Language.GUI[Config.LANGUAGE]['SOURCE_CATEGORY'])
		self.sourceFrameLayout.addWidget(self.sourceCategoryLabel)
		self.sourceCategoryButton1 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['MINECRAFT_VERSION'], self.sourceFrame)
		self.sourceCategoryButton1.clicked.connect(lambda: self.updateSourcePathDropdown('MINECRAFT_VERSION'))
		self.sourceFrameLayout.addWidget(self.sourceCategoryButton1)
		self.sourceCategoryButton2 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['RESOURCE_PACK'], self.sourceFrame)
		self.sourceCategoryButton2.clicked.connect(lambda: self.updateSourcePathDropdown('RESOURCE_PACK'))
		self.sourceFrameLayout.addWidget(self.sourceCategoryButton2)

		self.sourcePathLabel = QtWidgets.QLabel(self.sourceFrame, text = Language.GUI[Config.LANGUAGE]['SOURCE_FILE'])
		self.sourceFrameLayout.addWidget(self.sourcePathLabel)
		self.sourcePathDropdown = QtWidgets.QComboBox(self.sourceFrame)
		self.sourceFrameLayout.addWidget(self.sourcePathDropdown)

		self.upscalingButton = QtWidgets.QPushButton(Language.GUI[Config.LANGUAGE]['START_UPSCALING'], self.sourceFrame)
		self.upscalingButton.clicked.connect(self.startUpscaling)
		self.upscalingButton.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
		self.sourceFrameLayout.addWidget(self.upscalingButton, 1)
		self.windowLayout.addWidget(self.sourceFrame)

		self.progressBar1 = QtWidgets.QProgressBar(self)
		self.progressBar1.setAlignment(QtCore.Qt.AlignHCenter)
		self.windowLayout.addWidget(self.progressBar1)
		self.progressBar2 = QtWidgets.QProgressBar(self)
		self.progressBar2.setAlignment(QtCore.Qt.AlignHCenter)
		self.windowLayout.addWidget(self.progressBar2)
		self.setLayout(self.windowLayout)

	def displayError(self, errorText):
		errorWindow = QtWidgets.QMessageBox()
		errorWindow.setIcon(QtWidgets.QMessageBox.Critical)
		errorWindow.setText(errorText)
		errorWindow.setWindowTitle(Language.ERROR[Config.LANGUAGE]['ERROR'])
		errorWindow.exec_()

	def scanTextures(self, folderPath, textureList, textureCount):
		for item in os.listdir(folderPath):
			itemPath = os.path.join(folderPath, item)
			if os.path.isfile(itemPath):
				if itemPath.endswith('.png'):
					textureList.append(Texture(itemPath))
					textureCount[0] += 1
			else:
				self.scanTextures(itemPath, textureList, textureCount)

	def startUpscaling(self):
		sourcePath = None
		try:
			sourcePath = self.sourcePathList[self.sourcePathDropdown.currentIndex()]
		except:
			self.displayError(Language.ERROR[Config.LANGUAGE]['NO_FILE_SELECTED'])
			return
		sourceArchive = Archive(sourcePath)
		sourceArchive.extract(Config.CACHE,
			extension_list = ('.mcmeta', '.png'),
			exception_list = ('assets/minecraft/textures/colormap', 'assets/minecraft/textures/gui/title/background'),
			folder_list = ('assets')
		)
		textureCount = [0]
		textureList = []
		self.scanTextures(Config.CACHE, textureList, textureCount)
		textureCount = textureCount[0]

	def updateSourcePathDropdown(self, sourceCategory):
		self.sourcePathList = []
		if sourceCategory == 'MINECRAFT_VERSION':
			Utility.scan_folder(self.sourcePathList, '%s/versions' % Config.MINECRAFT_DIRECTORY, 'jar')
		else:
			Utility.scan_folder(self.sourcePathList, '%s/resourcepacks' % Config.MINECRAFT_DIRECTORY, 'zip')
		self.sourcePathDropdown.clear()
		for sourcePath in self.sourcePathList:
			self.sourcePathDropdown.addItem('.minecraft%s' % Utility.normalize_path(sourcePath).split('.minecraft')[1])