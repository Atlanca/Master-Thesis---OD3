import re

class Section:
    def __init__(self, sectionId, sectionTitle, entityType='', sectionTextContent=None, sectionSummary='', priority=0, sectionDiagrams=None, children=None):
        self.sectionId = sectionId.replace('.', '_')
        self.sectionTitle = sectionTitle
        self.entityType = entityType
        self.sectionSummary = self.formatToHTML(sectionSummary)
        if sectionTextContent:
            self.sectionTextContent = [(value[0], self.formatToHTML(value[1])) for value in sectionTextContent]
        else:
            self.sectionTextContent = []
        if sectionDiagrams:
            self.sectionDiagrams = sectionDiagrams
        else:
            self.sectionDiagrams = []
        self.priority = priority
        if children:
            self.children = children
        else:
            self.children = []
    
    def formatToHTML(self, text):
        text = re.sub('(\\n[ ]*)+','</p><p>', text)
        finalText = '<p>' + text + '</p>'
        return finalText

    def addChild(self, child):
        self.children.append(child)
        self.children.sort(key=lambda x: x['priority'], reverse=True)

    def toDict(self):
        return {'id': self.sectionId, 
                'title': self.sectionTitle, 
                'entityType': self.entityType,
                'textContent': self.sectionTextContent, 
                'summary': self.sectionSummary,
                'diagrams': self.sectionDiagrams,
                'priority': self.priority,
                'children': self.children}

class Template:
    def __init__(self, question, summaryText='', sections=None):
        self.summaryText = summaryText
        self.question = question
        if sections:
            self.sections = sections
        else:
            self.sections = []
    
    def addSection(self, section):
        self.sections.append(section)
        self.sections.sort(key=lambda x: x['priority'], reverse=True)
    
    def toDict(self):
        return {'question': self.question, 'summaryText': self.summaryText, 'sections': self.sections}

