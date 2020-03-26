import multiprocessing
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
	progressBar2Format = QtCore.pyqtSignal(str)
	progressBar2Maximum = QtCore.pyqtSignal(int)
	progressBar2Value = QtCore.pyqtSignal(int)

	def __init__(self):
		super().__init__()
		self.setWindowTitle('FaithfulAI')
		self.setFixedSize(500, 400)
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
		self.sourceCategoryButtonGroup=QtWidgets.QButtonGroup(self.sourceFrame)
		self.sourceCategoryButton1 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['MINECRAFT_VERSION'], self.sourceFrame)
		self.sourceCategoryButton1.clicked.connect(lambda: self.updateSourcePathDropdown('MINECRAFT_VERSION'))
		self.sourceCategoryButton1.setChecked(True)
		self.sourceCategoryButtonGroup.addButton(self.sourceCategoryButton1)
		self.sourceFrameLayout.addWidget(self.sourceCategoryButton1)
		self.sourceCategoryButton2 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['RESOURCE_PACK'], self.sourceFrame)
		self.sourceCategoryButton2.clicked.connect(lambda: self.updateSourcePathDropdown('RESOURCE_PACK'))
		self.sourceCategoryButtonGroup.addButton(self.sourceCategoryButton2)
		self.sourceFrameLayout.addWidget(self.sourceCategoryButton2)

		self.sourcePathLabel = QtWidgets.QLabel(self.sourceFrame, text = Language.GUI[Config.LANGUAGE]['SOURCE_FILE'])
		self.sourceFrameLayout.addWidget(self.sourcePathLabel)
		self.sourcePathDropdown = QtWidgets.QComboBox(self.sourceFrame)
		self.sourceFrameLayout.addWidget(self.sourcePathDropdown)
		self.updateSourcePathDropdown('MINECRAFT_VERSION')

		self.processingMethod = None
		self.processingModeLabel = QtWidgets.QLabel(self.sourceFrame, text = Language.GUI[Config.LANGUAGE]['PROCESSING_MODE'])
		self.sourceFrameLayout.addWidget(self.processingModeLabel)
		self.processingModeButtonGroup=QtWidgets.QButtonGroup(self.sourceFrame)
		self.processingModeButton1 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['MULTI_PROCESSING'], self.sourceFrame)
		self.processingModeButton1.clicked.connect(lambda: self.updateProcessingMode('MULTI_PROCESSING'))
		self.processingModeButton1.setChecked(True)
		self.processingModeButtonGroup.addButton(self.processingModeButton1)
		self.sourceFrameLayout.addWidget(self.processingModeButton1)
		self.processingModeButton2 = QtWidgets.QRadioButton(Language.GUI[Config.LANGUAGE]['MONO_PROCESSING'], self.sourceFrame)
		self.processingModeButton2.clicked.connect(lambda: self.updateProcessingMode('MONO_PROCESSING'))
		self.processingModeButtonGroup.addButton(self.processingModeButton2)
		self.sourceFrameLayout.addWidget(self.processingModeButton2)
		self.updateProcessingMode('MULTI_PROCESSING')

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
		self.progressBar2Format.connect(self.progressBar2.setFormat)
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

	def loadTextures(self, folderPath, textureList, textureCount):
		for item in os.listdir(folderPath):
			itemPath = os.path.normpath(os.path.join(folderPath, item))
			if os.path.isfile(itemPath):
				if itemPath.endswith('.png'):
					textureList.append(Texture(itemPath))
					textureCount[0] += 1
			else:
				self.loadTextures(itemPath, textureList, textureCount)

	def scanTextures(self, folderPath, texturePathList, textureCount):
		for item in os.listdir(folderPath):
			itemPath = os.path.normpath(os.path.join(folderPath, item))
			if os.path.isfile(itemPath):
				if itemPath.endswith('.png'):
					texturePathList.append(itemPath)
					textureCount[0] += 1
			else:
				self.scanTextures(itemPath, texturePathList, textureCount)

	def __startMonoUpscaling(self, sourcePath):
		self.progressBar1Maximum.emit(7)
		self.progressBar2Maximum.emit(0)
	
		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['EXTRACTING_SOURCE'])
		self.progressBar1Value.emit(1)
		sourceArchive = Archive(sourcePath)
		sourceArchive.extract(Config.CACHE,
			extension_list = ('.mcmeta', '.png'),
			exception_list = ('assets/minecraft/textures/colormap', 'assets/minecraft/textures/gui/title/background', 'assets/realms/textures/gui/realms/images'),
			folder_list = ('assets')
		)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['LOADING_TEXTURES'])
		self.progressBar1Value.emit(2)
		textureCount = [0]
		textureList = []
		self.loadTextures(Config.CACHE, textureList, textureCount)
		textureCount = textureCount[0]

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['APPLYING_PRE_PROCESSING'])
		self.progressBar1Value.emit(3)
		self.progressBar2Maximum.emit(textureCount)
		self.progressBar2Value.emit(0)
		progressCount = 0
		for texture in textureList:
			if texture.is_tiled():
				texture.duplicate()
				texture.save(texture.is_masked())
			elif texture.is_masked():
				texture.save(True)		
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['UPSCALING_TEXTURES'])
		self.progressBar1Value.emit(4)
		self.progressBar2Value.emit(0)
		upscaler = Upscaler()
		progressCount = 0
		for texture in textureList:
			upscaler.upscale(texture)
			progressCount += 1
			self.progressBar2Value.emit(progressCount)
		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['UPSCALING_TEXTURES_WAIT'])
		self.progressBar2Maximum.emit(0)
		upscaler.wait()
		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['UPSCALING_TEXTURES_REMOVE'])
		self.progressBar2Maximum.emit(textureCount)
		self.progressBar2Value.emit(0)
		progressCount = 0
		for texture in textureList:
			texture.merge()
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['APPLYING_POST_PROCESSING'])
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
				os.remove(texture.path.replace('.png', '.mask.png'))
			texture.save()
			del texture
			progressCount += 1
			self.progressBar2Value.emit(progressCount)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['GENERATING_RESOURCE_PACK'])
		self.progressBar1Value.emit(6)
		self.progressBar2Maximum.emit(0)
		with open('%s/pack.mcmeta' % Config.CACHE, 'w') as metaFile:
			metaFile.write('{\"pack\": {\"pack_format\": 5, \"description\": \"FaithfulAI, the first fully generated resource pack.\"}}')
		outputArchive = Archive('FaithfulAI - %s.zip' % '.'.join(sourcePath.split(os.path.sep)[-1].split('.')[:-1]))
		outputArchive.generate(Config.CACHE, destination_path = '%s/resourcepacks/%s' % (Config.MINECRAFT_DIRECTORY, outputArchive.path))

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['DONE'])
		self.progressBar1Value.emit(7)
		self.progressBar2Maximum.emit(1)
		self.progressBar2Value.emit(1)
		self.upscalingButtonEnabled.emit(True)

	def __startMultiUpscaling(self, sourcePath):
		self.progressBar1Maximum.emit(5)
		self.progressBar2Maximum.emit(0)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['EXTRACTING_SOURCE'])
		self.progressBar1Value.emit(1)
		sourceArchive = Archive(sourcePath)
		sourceArchive.extract(Config.CACHE,
			extension_list = ('.mcmeta', '.png'),
			exception_list = ('assets/minecraft/textures/colormap', 'assets/minecraft/textures/gui/title/background'),
			folder_list = ('assets')
		)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['SCANNING_TEXTURES'])
		self.progressBar1Value.emit(2)
		textureCount = [0]
		texturePathList = []
		self.scanTextures(Config.CACHE, texturePathList, textureCount)
		textureCount = textureCount[0]

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['PROCESSING_TEXTURES'])
		self.progressBar1Value.emit(3)
		self.progressBar2Maximum.emit(textureCount)
		processList = []
		threadCount = multiprocessing.cpu_count()
		os.rename('./bin/%s' % Config.UPSCALER, './%s' % Config.UPSCALER)
		for progress in range(textureCount):
			processCount = len(processList)
			while processCount + 1 == threadCount:
				processId = 0
				while processId < processCount:
					if not processList[processId].is_alive():
						del processList[processId]
						processCount -= 1
					else:
						processId += 1
			texturePath = texturePathList[progress]
			self.progressBar2Format.emit('%s (%i/%i)' % (texturePath.split(os.path.sep)[-1], progress + 1, textureCount))
			self.progressBar2Value.emit(progress + 1)
			processList.append(multiprocessing.Process(target = Utility.upscale_texture, args = (texturePath,)))
			processList[-1].start()
		processCount = len(processList)
		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['PROCESSING_TEXTURES_WAIT'])
		self.progressBar2.resetFormat()
		self.progressBar2Maximum.emit(processCount)
		for progress in range(processCount):
			self.progressBar2Value.emit(progress + 1)
			processList[progress].join()
		os.rename('./%s' % Config.UPSCALER, './bin/%s' % Config.UPSCALER)

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['GENERATING_RESOURCE_PACK'])
		self.progressBar1Value.emit(4)
		self.progressBar2Maximum.emit(0)
		with open('%s/pack.mcmeta' % Config.CACHE, 'w') as metaFile:
			metaFile.write('{\"pack\": {\"pack_format\": 5, \"description\": \"FaithfulAI, the first fully generated resource pack.\"}}')
		outputArchive = Archive('FaithfulAI - %s.zip' % '.'.join(sourcePath.split(os.path.sep)[-1].split('.')[:-1]))
		outputArchive.generate(Config.CACHE, destination_path = '%s/resourcepacks/%s' % (Config.MINECRAFT_DIRECTORY, outputArchive.path))

		self.progressBar1Format.emit(Language.GUI[Config.LANGUAGE]['DONE'])
		self.progressBar1Value.emit(5)
		self.progressBar2Maximum.emit(1)
		self.progressBar2Value.emit(1)
		self.upscalingButtonEnabled.emit(True)

	def startUpscaling(self):
		self.upscalingButton.setEnabled(False)
		sourcePath = None
		try:
			sourcePath = self.sourcePathList[self.sourcePathDropdown.currentIndex()]
		except:
			self.displayError(Language.ERROR[Config.LANGUAGE]['NO_FILE_SELECTED'])
			return
		self.upscalingThread = threading.Thread(target = self.processingMethod, args = (sourcePath,))
		self.upscalingThread.start()

	def updateProcessingMode(self, processingMode):
		if processingMode == 'MULTI_PROCESSING':
			self.processingMethod = self.__startMultiUpscaling
		else:
			self.processingMethod = self.__startMonoUpscaling

	def updateSourcePathDropdown(self, sourceCategory):
		self.sourcePathList = []
		if sourceCategory == 'MINECRAFT_VERSION':
			Utility.scan_folder(self.sourcePathList, '%s/versions' % Config.MINECRAFT_DIRECTORY, 'jar')
		else:
			Utility.scan_folder(self.sourcePathList, '%s/resourcepacks' % Config.MINECRAFT_DIRECTORY, 'zip')
		self.sourcePathDropdown.clear()
		for sourcePath in self.sourcePathList:
			self.sourcePathDropdown.addItem('.minecraft%s' % os.path.normpath(sourcePath).split('.minecraft')[1])