import re

def getNameFromUri(uri):
    return (re.sub(".+#", '', uri))	

def entitiesToListString(entities):
    entityListString = ''
    for index, e in enumerate(entities):
        if index < len(entities) - 1:
            entityListString +=  getNameOfEntity(e) + '\n'
        else:
            entityListString += getNameOfEntity(e)
    return entityListString

def getNameOfEntity(entity):
    if entity.label:
        return entity.label
    else: 
        return getNameFromUri(entity.uri)

def diagramUriToFileName(diagramName):
    match = re.search('\\wigure_\\d\.\\d+', diagramName)
    finalString = re.sub('\.', '_', str(match.group(0)))
    return finalString

def formatName(relationName):
    nameStr = ''
    nameStrList = []
    name = ''
    for index, s in enumerate(relationName):
        if s.isupper() and index is not 0:
            nameStrList.append(name)
            name = '' + s.lower()
        else:
            name += s
    if name:
        nameStrList.append(name)

    for index, s in enumerate(nameStrList):
        nameStr += s
        if index < len(nameStrList) - 1:
            nameStr += ' '

    return nameStr

def formatDiagramName(diagramName):
    diagramName = re.sub('figure_\d+.\d+_','', diagramName)
    diag_words = diagramName.split('_')
    first_char = diag_words[0][0]
    
    if first_char:
        diag_words[0] = diag_words[0].replace(first_char, first_char.upper(),1)
    
    finalName = ''
    for index, word in enumerate(diag_words):
        if(index < len(diag_words) - 1):
            finalName += word + ' '
        else:
            finalName += word
    return finalName

def formatListOfEntities(elist):
    elist = [e for e in elist if e]
    end = len(elist) - 1
    entityString = ''
    for index, item in enumerate(elist):
        if(item):
            entityString += str(len(item)) + ' ' + formatName(getNameFromUri(item[0].type))
            if len(item) > 1:
                entityString += 's'
            if index < end and index + 1 == end:
                entityString += ' and '
            elif index < end:
                entityString += ', '
    return entityString
        

def openText(url):
    template = ''
    with open(url, 'r') as myfile:
        template = myfile.read().replace('\n', '')
        template = template.replace('\\n', '\n')
    return template