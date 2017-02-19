#!/usr/bin/python3
import subprocess
import argparse
from pathlib import Path

from smb.SMBConnection import SMBConnection

# ffmpeg -i pipe:0 -vcodec mpeg4 -acodec aac video.mp4
# ffmpeg -i pipe:0 -vcodec h264 -acodec aac video.mp4
# ffmpeg -i pipe:0 -strict -2 -vcodec vp8 -acodec vorbis video.webm 




netmap = {
	'ROUTER/Download2': {
		'ip': '192.168.1.1'
		,'user': ''
		,'pass': ''
		}
	}


ffmpegCommand = ['ffmpeg']
ffmpegArgs    = ['-vcodec', 'mpeg4', '-acodec', 'aac']

def checkFilename(filename):
	return filename


def processFile( inputFile, outputFile ):
	if inputFile.isFile():
		outputFilename = ''
		outputFile = DirectoryManager.createFile( outputFilename )

		runffmpeg( inputFile, outputFile )



def runffmpeg( inputFile, outputFile ):
	inputPipe  = inputFile.open( mode='rb' )

	command = ffmpegCommand + ['-i', 'pipe:0'] + ffmpegArgs + [outputFile.fullname]
	print( command )

	subprocess.run( command, stdin=inputPipe, shell=False )



class DirectoryManager:
	@staticmethod
	def resolve( filename ):
		if 0 > filename.find(':'):
			filename = 'file://'+filename

		if filename.startswith('file://'):
			fileOrDirectory = Path( filename[7:] )

			if fileOrDirectory.exists():
				if fileOrDirectory.is_file():
					return File( fileOrDirectory )
				elif fileOrDirectory.is_dir():
					return Directory( fileOrDirectory )
			return



	def createFile( name ):
		filePath = Path( name )

		return File( filePath )

	def createDirectory( name ):
		filePath = Path( name )

		return Directory( filePath )



class Directory:
	innerObj = None
	name = None
	fullname = None


	def __init__( _self, path ):
		_self.innerObj = path
		_self.name = path.name

		if path.exists():
			_self.fullname = str( path.resolve() )
		else:
			_self.fullname = str( path.parent.resolve() ) + '/' + path.name

		print( 'DIR  '+_self.fullname )

	def isFile( _self ):
		return False

	def isDirectory( _self ):
		return True

	def getFiles( _self ):
		children = []
		for child in _self.innerObj.iterdir():
			if child.is_dir() and '.' != child.name:
				children.append( Diretory(child) )
			elif child.is_file():
				children.append( File(child) )
		return children



class File( Directory ):
	innerObj = None
	name = None
	fullname = None


	def __init__( _self, path ):
		_self.innerObj = path
		_self.name = path.name

		if path.exists():
			_self.fullname = str( path.resolve() )
		else:
			_self.fullname = str( path.parent.resolve() ) + '/' + path.name

		print( 'FILE '+_self.fullname )

	def isFile( _self ):
		return True

	def isDirectory( _self ):
		return False

	def open( _self, mode='rb' ):
		return _self.innerObj.open( mode, buffering=(1024*1024) )





class SmbDirectory:
	innerObj = None
	name     = None
	fullname = None


	def __init__( _self, host, sharedObj, path, connection=None, attributes=None ):
		#_self.innerObj = path
		#_self.name = path.name
		_self.fullname = 'smb://'+host+'/'+sharedObj+'/'+path

		print( 'DIR  '+_self.fullname )

	def isFile( _self ):
		return False

	def isDirectory( _self ):
		return True

	def getFiles( _self ):
		return []



class SmbFile( SmbDirectory ):
	innerObj = None
	name     = None
	fullname = None


	def __init__( _self, host, sharedObj, path, connection=None, attributes=None ):
		#_self.innerObj = path
		#_self.name = path.name
		_self.fullname = 'smb://'+host+'/'+sharedObj+'/'+path
		print( 'FILE '+_self.fullname )

	def isFile( _self ):
		return True

	def isDirectory( _self ):
		return False

	def open( _self, mode='rb' ):
		return _self.innerObj.open( mode, buffering=(1024*1024) )




parser = argparse.ArgumentParser(description='Convert video files to MP4.')
parser.add_argument(
	'inputFile',
	metavar='input',
	#type=argparse.FileType(mode='rb', bufsize=8192),
	type=checkFilename,
	help='input filename')
parser.add_argument(
	'outputFile',
	metavar='output',
	nargs='?',
	#type=argparse.FileType(mode='wb', bufsize=8192),
	type=checkFilename,
	help='output filename')
scriptArgs = parser.parse_args()



inputFile = DirectoryManager.resolve( scriptArgs.inputFile )

if inputFile.isFile():
	if scriptArgs.outputFile is None:
		dotIdx = inputFile.fullname.rfind('.')
		if 0 >= dotIdx:
			scriptArgs.outputFile = 'output.mp4'
		else:
			scriptArgs.outputFile = inputFile.fullname[0:dotIdx] + '.mp4'

	outputFile = DirectoryManager.createFile( scriptArgs.outputFile )

	runffmpeg( inputFile, outputFile )

elif inputFile.isDirectory():
	inputDir = inputFile

	if scriptArgs.outputFile is None:
		scriptArgs.outputFile = '.'

	outputDir = DirectoryManager.createDirectory( scriptArgs.outputFile )


	for inputFile in inputDir.getFiles():
		print( inputFile.fullname )

		dotIdx = inputFile.name.rfind('.')
		if 0 >= dotIdx:
			outputFilename = 'output.mp4'
		else:
			outputFilename = inputFile.name[0:dotIdx] + '.mp4'

		outputFile = DirectoryManager.createFile( outputDir.fullname+'/'+outputFilename )

		runffmpeg( inputFile, outputFile )
