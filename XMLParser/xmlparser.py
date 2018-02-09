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

class XmlContent:
  def __init__(self, xmlTitle):
    self.xmlTitle = xmlTitle
    self.content = None
    
class XmlIndexTitle:
  def __init__(self, title, pageNumber):
    self.title = title
    self.childrenTitles = None
    self.pageNumber = pageNumber

#This class is used to parse the xml document
#The constructor requires an input document
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
      if content.tag == "text": 
        line = self.restructureText(self.getNestedText(content) )
      else:
        line = ''
        
      #If we have a text, try to find the title
      if line != '':
        print(self.parent_map[content].attrib["number"], content.attrib["top"], repr(line))
        
        #If the line is the title, we are done. Fill currentTitle and return it
        if line == currentTitle.title: 
          currentTitle.start = content
          currentTitle.end = content
          currentTitle.currentText = line
          return currentTitle
        
        #We also try to assemble the title, from the assumption that the
        #title may be fragmented into multiple lines. 
        if title.startswith(line):
          currentTitle.start = content
          currentTitle.currentText = currentTitle.currentText + line
          title = title[len(line):].strip()
        else:
        #This can be more effective. Now it clears too many times
          currentTitle.clear()
          title = currentTitle.title
        
        #If we have successfully assembled the title, return the title
        if currentTitle.currentText == currentTitle.title:
          currentTitle.end = content
          return currentTitle

  def getContentByTitle(self, title):
    content = XmlContent(self.getTitle(title))
    
    
  #Input the index pages, outputs a list of titles 
  #In this case index pages are 8-10 (SnowflakeThesis.xml)
  def parseIndex(self, pageStart, pageEnd):
    indexContent = [content for indexPage in self.pages[pageStart:pageEnd] for content in indexPage]
    prevLineTop = 0
    prevLine = ''
    titles = []
    for content in indexContent:
      if content.tag == "text":
        line = self.restructureText(self.getNestedText(content))
        if line != '':
          #If content is on the same line as the previous one,
          #merge them. Otherwise reset prevLine
          if content.attrib["top"] == prevLineTop:
            prevLine = prevLine + ' ' + line
           # print(prevLine)
            
          elif prevLine is not '':
            
            #Try to match the title and pagenumber. If either of them is missing
            #then we know it's not an index element so we dont add it to our titles list
            pageNbrMatch = re.compile('([\d]+)$')
           
            title = re.sub('[\d]+$', '', prevLine).strip()
            pageNumber = pageNbrMatch.search(prevLine.strip())
            prevLine = line
            
            if title is not '' and pageNumber is not None:
              indexTitle = XmlIndexTitle(title, pageNumber.group())
              titles.append(indexTitle) 
          
          else:
            prevLine = line
            
          prevLineTop = content.attrib["top"]
          
    for title in titles:
      print(title.title, title.pageNumber)
    return titles

    
    
