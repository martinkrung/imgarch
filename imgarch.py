#!/usr/bin/python

import os, glob
#from stat import *
from optparse import OptionParser

def setup_parser():
	#
	# create the command line parser
	#
	usage = """ """
	global parser
	parser = OptionParser(usage)
	parser.add_option("-r", "--recursion", dest="recursion", action="store_true", help=" recursion on folder deep")
	parser.add_option("-l", "--local", dest="local", action="store_true", help="local folder only")
	parser.add_option("-c", "--correctdate", dest="correctdate", action="store_true",  help=" ")
	parser.add_option("-s", "--shif", dest="shift",help="shift EXIF timestamp in h: e.g -1, 1 ")
	parser.add_option("-f", "--filedate", dest="filedate", action="store_true", help="Set Exif timestamp to file modification timestamp")
	parser.add_option("-e", "--exifdate", dest="exifdate", action="store_true", help="Set File Modification timestamp to Exif timestamp")
	parser.add_option("-m", "--mov", dest="mov", action="store_true", help="Set File Modification timestamp to File Name")

	parser.add_option("-b", "--beautify ", dest="beautify", action="store_true", help=" make nice names")
	
	
	global opt
	(opt, args) = parser.parse_args()
	print opt
	'''
	if len(args) != 1:
		parser.error("incorrect number of arguments, please specify the domain, e.g. mysite.com or sub.mysite.com, without www")
	
	# domain
	opt.domain = args[0]
	'''
	

class imgarch:
	
	def __init__(self):
		self.format = '%Y%m%d-%H%M%S'
		self.suffixmv = ('MOV','mov', 'avi', 'AVI', 'MTS')
		self.suffixjpg = ('JPG','jpg', 'THM', 'thm','CR2', 'cr2')

		self.pair = {}
		
	def paring(self):
		for f in os.listdir('.'):
			if f.lower().endswith('jpg'):
				'''lock for movie'''
				bn = f.split('.')[0]
				for suffix in self.suffixmv:
					mvn = '%s.%s'  %(bn, suffix)
					if	os.path.isfile(mvn):
						self.pair[f] = mvn

		print self.pair

	def shiftExifTime(self, h):
		h = int(h)
		tool = "jhead"
		if tool != "jhead":
			if h > 0:
				h =   '%s%i'  %('+=', abs(h))
			else:
				h =   '%s%i'  %('-=', abs(h))
		else:
			if h > 0:
				h =   '%s%i'  %('+', abs(h))
				
		print h
		files = os.listdir('.')
		files.sort()
		for f in files:
			if f.split('.')[1] in self.suffixjpg:
				if not self.sameTime(f):
					if tool != "jhead":
						stdout = self.getCommandOutput('exiftool -s  -DateTimeOriginal%s  %s'  %(h, f) )
					else:
						stdout = self.getCommandOutput('jhead -ta%s  %s'  %(h, f) )
					print stdout
					self.sameTime(f)
					
	def setFileTs2ExifTs(self):
		'''Set Exif time to file modification time'''
		files = os.listdir('.')
		files.sort()
		for f in files:
			print f
			if f.split('.')[1] in self.suffixjpg:
				if not self.sameTime(f):
					stdout = self.getCommandOutput('jhead -dsft %s '  %(f) )
					self.showTime(f)

	def setExifTs2FileTs(self):
		''' Set file modification time to Exif time'''
		files = os.listdir('.')
		files.sort()
		for f in files:
			print f
			if f.split('.')[1] in self.suffixjpg:
				if not self.sameTime(f):
					stdout = self.getCommandOutput('jhead -ft %s '  %(f) )
					self.showTime(f)

				
	def checkTimestamp(self, mode = 'light'):
			files = os.listdir('.')
			files.sort()
			match = False
			if mode == 'light':
				light = True
			else:
				light = False
			
			for f in files:
				if os.path.isfile(f) and f.split('.')[1] in self.suffixjpg:
					'''if not the same'''
					if not self.sameTime(f):
						if light:
							print "false"
							return False
						else:
							match = True						
			if match:
				return False
			else:
				return True

	def sameTime(self, f):
				datetimeoriginal, filemodifydate = self.getTime(f)
				''' houre shift '''
				if datetimeoriginal[0:13] != filemodifydate[0:13]:
					self.printTime( f, datetimeoriginal, filemodifydate)
					return False
				else:
					return True

	'''helper def'''
	def getTime(self, f):
			stdout = self.getCommandOutput('exiftool -s -DateTimeOriginal %s'  %(f) )
			datetimeoriginal =  stdout.split(':', 1)[1].strip()
			stdout = self.getCommandOutput('exiftool -s -FileModifyDate %s'  %(f) )
			filemodifydate = stdout.split(':', 1)[1].split('+')[0].strip()
			return (datetimeoriginal, filemodifydate)

	def showTime(self, f):
			datetimeoriginal, filemodifydate = self.getTime(f)
			self.printTime( f, datetimeoriginal, filemodifydate)
			
	def printTime(self, f, datetimeoriginal, filemodifydate):
			print ''
			print '%s: filedate (%s)'   %(f, filemodifydate)
			print '%s: exifdate (%s)'   %(f, datetimeoriginal)

	def renameMov(self):
			
		for n in glob.glob('*.MOV'):
			suffix = n.split('.')[1].lower()
			filename = self.getCommandOutput('date -r %s +%s'  % (n, self.format) ).strip()
			filename = '%s.%s'  % (filename, suffix)
			print '%s --> %s'   %(n, filename)
			os.rename(n, filename)

		for n in glob.glob('*.THM'):
			stdout = self.getCommandOutput('jhead -n%s %s' % (self.format, n))
			print stdout
			original = stdout.split('-->')[0].strip()
			target = stdout.split('-->')[1].strip()
			target.split('.')[0]
			
			if	os.path.isfile(original.split('.')[0]+'.MOV'):		
				os.rename(original.split('.')[0]+'.MOV', target.split('.')[0]+'.mov')
			if	os.path.isfile(original.split('.')[0]+'.AVI'):		
				os.rename(original.split('.')[0]+'.AVI', target.split('.')[0]+'.avi')
			
	def renameJpg(self):
				stdout = self.getCommandOutput('jhead -n%s %s' % (self.format, '*'))
				print stdout

	def renameCr2(self):
				for f in glob.glob('*.CR2'):
					stdout = self.getCommandOutput('exiftool -s -DateTimeOriginal %s'  %(f) )
					base =  stdout.split(':',1)[1].strip().replace(':','').replace(' ','-')
					suffix = f.split('.')[1].lower()
					target = '%s.%s' %(base, suffix)
					if	not os.path.isfile(target):
						print  '%s --> %s' %(f,target)
						os.rename(f, target)
					else:
						print  'file  %s exists' %(target)
						
        def getCommandOutput(self,command):
        	child = os.popen(command)
        	data = child.read( )
        	err = child.close( )
        	if err:
        		raise RuntimeError, '%s failed with exit code %d' % (command, err)
        		data = str(data)
        		data = data.strip( )
        		
                return data
                
#mvr.mov()
#mvr.jpg()

#mvr.datecheck()
#mvr.paring()

def main():
	
	setup_parser()
	ia = imgarch()

	ia.renameCr2()
	if opt.shift:
		ia.shiftExifTime(opt.shift)
		exit
		
	if opt.beautify:
		ia.renameMov()
		ia.renameJpg()
		exit

	if opt.mov:
		ia.renameMov()
		exit	

	if opt.filedate:
		print opt.filedate
		ia.setFileTs2ExifTs()
		exit

	if opt.exifdate:
		print opt.exifdate
		ia.setExifTs2FileTs()
		exit

	if opt.recursion:
		for f in os.listdir('.'):
			if os.path.isdir(f):
				os.chdir(f)
				print "enter %s" %(f)
					
				if not ia.checkTimestamp('light'):
					print "folder has some dateshiftr %s" %(f)
		
				os.chdir('../')
	if opt.local:
		if not ia.checkTimestamp('deep'):
			print "folder has some dateshiftr %s" %(os.getcwd())

if __name__ == "__main__":
    main()
			

