import os
import subprocess
import sys

BIN = 'FaithfulAI'
SRC = (
	'./launcher.py',
	'./src/archive.py',
	'./src/config.py',
	'./src/language.py',
	'./src/pixel.py',
	'./src/texture.py',
	'./src/upscaler.py',
	'./src/utility.py',
	'./src/window.py'
)

def run_command(command):
	process = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
	process_status = process.poll()
	while process_status is None:
		sys.stdout.write(str(process.stdout.readline(), 'ascii').split(os.path.pathsep)[0])
		sys.stdout.flush()
		process_status = process.poll()
	if process_status != 0:
		raise Exception('ERROR: \'%s\' failed.' % command)

def linux_build():
	pass

def windows_build():
	run_command('pip install -r requirements.txt --user')
	run_command('pyinstaller %s -n %s' % (' '.join(SRC), BIN))

if __name__ == '__main__':
	{'nt': windows_build, 'posix': linux_build}[os.name]()
	sys.exit(0)