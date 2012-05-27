import markdown
import os
from tripy.utils.path import Path
import tifl.md.ext.latex


def convertFile(inputFile, webBase = ".", wikiLinkBase = None, outputFile=None):

	if not inputFile.exists():
		raise ValueError("File %s does not exist" % inputFile)

	f = inputFile.openFile("r")
	fileText = f.read()
	f.close()

	outputText, resourceList = convert(fileText, webBase, wikiLinkBase)

	if outputFile:
		f = outputFile.openFile("w")
		f.write(outputText)
		f.close()
		
	return outputText


def convert(text, webBase = ".", wikiLinkBase = None):

	# The text that we operate on and modify.  the original variable
	# will remain immutable
	currentText = text
	# Resources (if any) that are generated during this process.  This
	# can be other pages, images or other files
	resourceList = []
	
	currentText = markdown.markdown(currentText, ['wikilinks(base_url=/page/,end_url=.md)', tifl.md.ext.latex.MarkdownLatex()])

	return currentText, resourceList

