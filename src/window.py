import os
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import threading

from src.archive import Archive
from src.config import Config
from src.language import Language
from src.texture import Texture
from src.upscaler import Upscaler
from src.utility import Utility

class Window(QtWidgets.QWidget):
	upscalingButtonEnabled = QtCore.pyqtSignal(bool)
	progressBar1Format = QtCore.pyqtSignal(str)
	progressBar1Maximum = QtCore.pyqtSignal(int)
	progressBar1Value = QtCore.pyqtSignal(int)
	progressBar2Maximum = QtCore.pyqtSignal(int)
	progressBar2Value = QtCore.pyqtSignal(int)

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

		self.upscalingThread = None
		self.upscalingButton = QtWidgets.QPushButton(Language.GUI[Config.LANGUAGE]['START_UPSCALING'], self.sourceFrame)
		self.upscalingButton.clicked.connect(self.startUpscaling)
		self.upscalingButton.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
		self.upscalingButtonEnabled.connect(self.upscalingButton.setEnabled)
		self.sourceFrameLayout.addWidget(self.upscalingButton, 1)
		self.windowLayout.addWidget(self.sourceFrame)

		self.progressBar1 = QtWidgets.QProgressBar(self)
		self.progressBar1.setAlignment(QtCore.Qt.AlignHCenter)
		self.progressBar1Format.connect(self.progressBar1.setFormat)
		self.progressBar1Maximum.connect(self.progressBar1.setMaximum)
		self.progressBar1Value.connect(self.progressBar1.setValue)
		self.windowLayout.addWidget(self.progressBar1)
		self.progressBar2 = QtWidgets.QProgressBar(self)
		self.progressBar2.setAlignment(QtCore.Qt.AlignHCenter)
		self.progressBar2Maximum.connect(self.progressBar2.setMaximum)
		self.progressBar2Value.connect(self.progressBar2.setValue)
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
		self.upscalingButton.setEnabled(False)
		self.upscalingThread = threading.Thread(target = self.__startUpscaling)
		self.upscalingThread.start()

	def __startUpscaling(self):
		sourcePath = None
		try:
			sourcePath = self.sourcePathList[self.sourcePathDropdown.currentIndex()]
		except:
			self.displayError(Language.ERROR[Config.LANGUAGE]['NO_FILE_SELECTED'])
			return
		self.progressBar1Maximum.emit(7)
		self.progressBar2Maximum.emit(0)
	
		self.progressBar1Format.emit('Extracting source files')
		self.progressBar1Value.emit(1)
		sourceArchive = Archive(sourcePath)
		sourceArchive.extract(Config.CACHE,
			extension_list = ('.mcmeta', '.png'),
			exception_list = ('assets/minecraft/textures/colormap', 'assets/minecraft/textures/gui/title/background'),
			folder_list = ('assets')
		)

		self.progressBar1Format.emit('Loading textures')
		self.progressBar1Value.emit(2)
		textureCount = [0]
		textureList = []
		self.scanTextures(Config.CACHE, textureList, textureCount)
		textureCount = textureCount[0]

		self.progressBar1Format.emit('Applying pre-processing effects')
		self.progressBar1Value.emit(3)
		self.progressBar2Maximum.emit(textureCount)
		self.progressBar2Value.emit(0)
		progressCount = 0
		for texture in textureList:
			if texture.is_tiled():
				texture.duplicate()
				texture.save(texture.is_masked())
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit('Upscaling textures')
		self.progressBar1Value.emit(4)
		self.progressBar2Value.emit(0)
		upscaler = Upscaler()
		progressCount = 0
		for texture in textureList:
			upscaler.upscale(texture)
			progressCount += 1
			self.progressBar2Value.emit(progressCount)
		self.progressBar1Format.emit('Upscaling textures (Waiting for the processes to finish)')
		self.progressBar2Maximum.emit(0)
		upscaler.wait()
		self.progressBar1Format.emit('Upscaling textures (Removing the base textures)')
		self.progressBar2Maximum.emit(textureCount)
		self.progressBar2Value.emit(0)
		progressCount = 0
		for texture in textureList:
			texture.merge()
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit('Applying post-processing effects')
		self.progressBar1Value.emit(5)
		self.progressBar2Value.emit(0)
		progressCount = 0
		for texture in textureList:
			texture.load()
			if texture.is_tiled():
				texture.crop()
			texture.downscale()
			if texture.is_masked():
				texture.mask()
				os.remove(self.path.replace('.png', '.mask.png'))
			texture.save()
			del texture
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit('Generating resource pack')
		self.progressBar1Value.emit(6)
		self.progressBar2Maximum.emit(0)
		with open('%s/pack.mcmeta' % Config.CACHE, 'w') as metaFile:
			metaFile.write('{\"pack\": {\"pack_format\": 5, \"description\": \"FaithfulAI, the first fully generated resource pack.\"}}')
		outputArchive = Archive('FaithfulAI - %s.zip' % sourcePath.replace('\\', '/').split('/')[-1].split('.')[0])
		outputArchive.generate(Config.CACHE, destination_path = '%s/resourcepacks/%s' % (Config.MINECRAFT_DIRECTORY, outputArchive.path))

		self.progressBar1Format.emit('Done')
		self.progressBar1Value.emit(8)
		self.progressBar2Maximum.emit(1)
		self.progressBar2Value.emit(1)
		self.upscalingButtonEnabled.emit(True)

	def updateSourcePathDropdown(self, sourceCategory):
		self.sourcePathList = []
		if sourceCategory == 'MINECRAFT_VERSION':
			Utility.scan_folder(self.sourcePathList, '%s/versions' % Config.MINECRAFT_DIRECTORY, 'jar')
		else:
			Utility.scan_folder(self.sourcePathList, '%s/resourcepacks' % Config.MINECRAFT_DIRECTORY, 'zip')
		self.sourcePathDropdown.clear()
		for sourcePath in self.sourcePathList:
			self.sourcePathDropdown.addItem('.minecraft%s' % Utility.normalize_path(sourcePath).split('.minecraft')[1])