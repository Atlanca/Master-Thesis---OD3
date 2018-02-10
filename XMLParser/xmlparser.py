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
    self.children = []
    
  def clear(self):
    self.start = None
    self.end= None

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
    newStr = re.sub('[\.]{2,}','',newStr)
    newStr = re.sub(' +', ' ', newStr)
    newStr = re.sub('‐', '', newStr)
    newStr = re.sub('\xad', '', newStr)
    if newStr is ' ':
      newStr = ''
    return newStr
    
  #If the element is of type text but we cannot access it directly
  #we try to access the text within its childrens. 
  def getNestedText(self, xmlElement):
    iterator = xmlElement.itertext()
    text = ''
    
    for e in iterator:
      text += e
      
    return text
  #Returns an XmlTitle object
  #The title might be divided into multiple lines
  #If so, read all lines and return an XmlTitle object containing
  #the start xml element and the end xml element
  def getTitle(self, title):
    currentTitle = XmlTitle(title)
    for content in self.contents:
      #If content tag is 'text', then we get the text and restructure it
      if content.tag == "text": 
        line = self.restructureText(self.getNestedText(content)).lower()
      else:
        line = ''
        
      #If we have a text, try to find the title
      if line != '':
        #print(self.parent_map[content].attrib["number"], content.attrib["top"], repr(line))
        
        #If the line is the title, we are done. Fill currentTitle and return it
        if line == currentTitle.title: 
          currentTitle.start = content
          currentTitle.end = content
          return currentTitle
        
        #We also try to assemble the title, from the assumption that the
        #title may be fragmented into multiple lines. 
        if title.startswith(line):
          if currentTitle.start == None: 
            currentTitle.start = content
            
          currentText = currentText + line
          title = title[len(line):]
        else:
        #This can be more effective. Now it clears too many times
          currentTitle.clear()
          currentText = ''
          title = currentTitle.title
        
        #If we have successfully assembled the title, return the title
        if currentText == currentTitle.title:
          currentTitle.end = content
          return currentTitle
    #If none of the above works, we did not find anything
    #try adding a space at the end of the title and see if we can find it
    return self.getTitle(title + ' ')

  def getContentByTitle(self, title):
    content = XmlContent(self.getTitle(title))
    
  #Try to match the title and pagenumber. If either of them is missing
  #then we know it's not an index element so we dont add it to our titles list
  def tryToAdd(self, titles, prevLine):
    pageNbrMatch = re.compile('([\d]+)$')
           
    title = re.sub('[\d ]+$', '', prevLine).strip()
    pageNumber = pageNbrMatch.search(prevLine.strip())
    
    if title is not '' and pageNumber is not None:
      indexTitle = XmlIndexTitle(title, pageNumber.group())
      titles.append(indexTitle) 
    
  #Input the index pages, outputs a list of titles 
  #In this case index pages are 8-10 (SnowflakeThesis.xml)
  def parseIndex(self, pageStart, pageEnd):
    indexContent = [content for indexPage in self.pages[pageStart:pageEnd] for content in indexPage]
    prevLineTop = 0
    prevLine = ''
    titles = []
    for i in range(0,len(indexContent)):
      content = indexContent[i]
      if content.tag == "text":
        line = self.restructureText(self.getNestedText(content)).lower()
        if line != '':
          #If content is on the same line as the previous one,
          #merge them. Otherwise reset prevLine
          if content.attrib["top"] == prevLineTop:
            prevLine = prevLine + ' ' + line
          elif prevLine is not '':
            self.tryToAdd(titles, prevLine)
            prevLine = line
          else:
            prevLine = line
            
          prevLineTop = content.attrib["top"]
          
    #Attempt to add title one last time to add the last entry
    self.tryToAdd(titles, prevLine)
    
    return titles
    
  #Creates a title hierarchy
  def createTitleHierarchy(self, titles):
    mainChapters = []
    chapterDict = {}
    cnMatch = re.compile('^(\d|\.)+')
    pcnMatch = re.compile('(.+(?=\.))')
    
    for title in titles:
      match = cnMatch.match(title.title)
      if match is not None:
        chapterNumber = match.group().strip()
        chapterDict[chapterNumber] = title
        
        #If the chapter number is only a single digit
        #we know it's a main chapter. Otherwise we let the
        #parent chapter reference this chapter
        if len(chapterNumber) is 1:
          mainChapters.append(title)
        else:
          match = pcnMatch.match(chapterNumber)
          if match is not None:
            chapterDict[match.group().strip()].children.append(title)
            
      #If the titles have no numbers attached, they are main chapters
      else:
        mainChapters.append(title)
    
    return mainChapters

  def printNestedTitles(self, titles):
    for title in titles:
      print(title.title)
      if title.children:
        self.printNestedTitles(title.children)
  
  #1. Gathers all the chapters from the index page
  #2. Constructs all titles (with reference to the exact location in the xml document)
  #3. Creates a hierarchy of the titles based on their numbering
  #Pages 8-10 are index in this case
  def getTitles(self, indexStartPage, indexEndPage):
    indexTitles = self.parseIndex(indexStartPage, indexEndPage)
    xmlTitles = [self.getTitle(title.title) for title in indexTitles]
    xmlTitles = self.createTitleHierarchy(xmlTitles)
    return xmlTitles
  
  #Returns all xml elements between two chapters. 
  #Or if endTitle is not defined, between one chapter and the end of the document
  def getChapterContent(self, startTitle, endTitle = None):
    pageStart = int(self.parent_map[startTitle.start].attrib["number"])
 
    if endTitle is not None:
      pageEnd  = int(self.parent_map[endTitle.start].attrib["number"])
      pages = self.pages[pageStart-1:pageEnd]
    else:
      pages = self.pages[pageStart-1:]
    pageContent = [content for page in pages for content in page]
    chapterContent = []
    belongsToChapter = False
    
    for content in pageContent:
      if content == startTitle.start:
        belongsToChapter = True
        chapterContent.append(content)
      elif endTitle is not None and content == endTitle.start:
        belongsToChapter = False
      elif belongsToChapter:
        chapterContent.append(content)

    #for val in chapterContent:
      #print(self.getNestedText(val))
    return chapterContent
  
  #This is almsot the same as restructureText().
  #Will have to see what kind of merges we can do later.
  def restructureToReadable(self, text):
    if text is None: return ''
    newStr = text
    newStr = newStr.replace("◆", '\n')
    newStr = newStr.replace("\xa0", '')
    newStr = newStr.replace("➔", '\n')
    newStr = newStr.replace("\t", '')
    newStr = re.sub('[\.]{2,}','',newStr)
    newStr = re.sub(' +', ' ', newStr)
    newStr = re.sub('‐', '', newStr)
    newStr = re.sub('\xad', '', newStr)
    if newStr is ' ': newStr = '\n'
    return newStr
  
  def xmlToString(self, chapterContent):
    restructuredTexts = [] 
    previousContent = None
    for content in chapterContent:
      rText = self.restructureToReadable(self.getNestedText(content))
      #Checks the difference in the vertical position of the texts
      #if the difference is higher than 30, we know that the texts are 
      #of two different paragraphs
      if previousContent is not None and previousContent.tag == "text" and content.tag == "text":
        topDiff = int(content.attrib["top"]) - int(previousContent.attrib["top"])
        if topDiff > 30:
          print(topDiff)
          rText = '\n\n' + rText
          
      if content.tag == "text" and int(content.attrib["top"]) > 1088:
        rText = ''
        restructuredTexts[-1] = re.sub('[\n]+$', '', restructuredTexts[-1])
      #Once done with the processing, add the current line into a list 
      #containing all other lines
      if rText:
        restructuredTexts.append(rText)
      previousContent = content
    
    #Here we merge the list into a single string
    textString = ''
    for text in restructuredTexts:
      textString += text
   
    textString = re.sub('(\n ){3,}', '\n\n', textString)
    textString = re.sub('[\n]{3,}', '\n\n', textString)
    return textString
      
