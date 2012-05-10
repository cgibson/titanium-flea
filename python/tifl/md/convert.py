import markdown
import os
from tripy.utils.path import Path

# These are specifically ordered
ruleDict = {
	   "latex" : lambda text: _convertLatex(text),
	   "code" : lambda text: _convertCode(text),
	   "markdown" : lambda text: _convertMarkdown(text)
	   }


def convertFile(inputFile, outputFile=None, rules=["markdown"],
		webBase = ".", wikiLinkBase = None):

	if not inputFile.exists():
		raise ValueError("File %s does not exist" % inputFile)

	f = inputFile.open("r")
	fileText = f.read()
	f.close()

	outputText, resourceList = convert(fileText, rules, webBase, wikiLinkBase)

	if outputFile:
		f = open(outputFile, "w")
		f.write(outputText)
		f.close()
		return outputFile
	else:
		return outputText


def convert(text, rules=["markdown"], webBase = ".", wikiLinkBase = None):

	# The text that we operate on and modify.  the original variable
	# will remain immutable
	currentText = text
	# Resources (if any) that are generated during this process.  This
	# can be other pages, images or other files
	resourceList = []
	
	# we loop through the rule dict in order
	for rule,func in ruleDict.iteritems():
		if rule in rules:
			# Run the given rule against the text and add any
			# resources that were generated due to the conversion
			currentText, newResources = func(currentText)
			resourceList.extend(newResources)

	return currentText, resourceList


def _convertLatex(text):
	raise ValueError("Unimplemented")
	return text, []


def _convertCodeSnippets(text):
	raise ValueError("Unimplemented")
	return text, []


def _convertMarkdown(text):
	outputText = markdown.markdown(text, ['wikilinks(base_url=/page/,end_url=.md)'])
	return outputText, []
