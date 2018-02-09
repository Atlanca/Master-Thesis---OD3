import xml.etree.ElementTree as ET
import re

#An object that contains a title of the PDF.
#It is wrapped in an object since titles may be represented by
#multiple lines in the xml document.
class XmlTitle:
  def __init__(self, title):
    self.title = title
    self.start = None
    self.end = None
    self.currentText = ""
    
  def clear(self):
    self.start = None
    self.end= None
    self.currentText = ""

class XmlParser():
  def __init__(self, xmldoc):      
    self.root = ET.parse(xmldoc).getroot()
    self.pages = [page for page in self.root]
    self.contents = [content for page in self.pages for content in page]
    self.parent_map = {c:p for p in self.pages for c in p}

  #Restructures the text
  def restructureText(self, text):
    if text is None: return ''
    newStr = text
    newStr = newStr.replace("\n", '')
    newStr = newStr.replace("\xa0", '')
    newStr = newStr.replace("\t", '')
    newStr = newStr.strip().lower()
    newStr = re.sub('[\.]{2,}','',newStr)
    newStr = re.sub(' +', ' ', newStr)
    newStr = re.sub('‐', '', newStr)
    newStr = re.sub('\xad', '', newStr)
    return newStr
    
  #If the element is of type text but we cannot access it directly
  #we try to access the text within its childrens. 
  def getNestedText(self, xmlElement):
    if xmlElement.text is None:
      string = ""
      for element in xmlElement:
        string = string + self.getNestedText(element)
      return string
    else:
      return xmlElement.text
      
  #Returns an XmlTitle object
  #The title might be divided into multiple lines
  #If so, read all lines and return an XmlTitle object containing
  #the start xml element and the end xml element
  def getTitle(self, title):
    currentTitle = XmlTitle(title)
    for content in self.contents:
      #If content tag is 'text', then we get the text and restructure it
      #Otherwise just return an empty char
      if content.tag == "text": 
        line = self.restructureText(self.getNestedText(content) )
      else:
        line = ''
        
      #If we have a text, try to find the title
      if line != '':
        print(content.attrib["top"], repr(line))
        
        #If the line is the title, fill currentTitle and return it
        if line == currentTitle.title: 
          currentTitle.start = content
          currentTitle.end = content
          currentTitle.currentText = line
          return currentTitle
        
        #Otherwise we need to see if the title is fragmented into multiple lines
        if title.startswith(line):
          currentTitle.start = content
          currentTitle.currentText = currentTitle.currentText + line
          title = title[len(line):].strip()
        else:
          currentTitle.clear()
          title = currentTitle.title
          
        if currentTitle.currentText == currentTitle.title:
          currentTitle.end = content
          return currentTitle

  #Index can be found from page 8-10 
  def parseIndex(self, indexPages):
    for content in self.contents:
      if content.attrib == 'text':
        pass

