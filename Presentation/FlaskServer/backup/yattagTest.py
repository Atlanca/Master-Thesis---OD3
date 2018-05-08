from yattag import Doc
import httpQuery
import json
import re

class htmlBuilder:
    def __init__(self, featureRoleData=None, relImpClassesData=None, architectureData=None):
        self.featureRoleData = featureRoleData
        self.relImpClassesData = relImpClassesData
        self.architectureData = architectureData
        self.hideButtonId = 0
        self.ir = httpQuery.InformationRetriever()

    # ---------------------------------------------------------------------------------
    # Tab helper components
    # ---------------------------------------------------------------------------------

    def tabs(self, tabname, tabid):
        doc, tag, text, line = Doc().ttl()
        line('button', tabname, klass='w3-bar-item w3-button tablink', onclick="openTab(event, '%s')" % tabid)
        return doc.getvalue()

    
    def tabViewTitle(self, tabViewId, intext, content):
        doc, tag, text, line = Doc().ttl()
        #UNDER THIS
        with tag('div', id=tabViewId, klass="tab", style="display:block"):
            with tag('div', klass="w3-container w3-amber"):
                doc.asis(intext)
            for c in content:
                doc.asis(c)
        return doc.getvalue()

    # ---------------------------------------------------------------------------------
    # Explanation view
    # ---------------------------------------------------------------------------------

    #The main explanation view component
    def explanationView(self):
        doc, tag, text, line = Doc().ttl()
        doc.asis(self.tabViewTitle('explanation', '', [#self.featureRoleExplanation('featureRole', 'featureRoleData', self.featureRoleData), 
                                                #self.relatedImplementationClassesExplanation('relImpClasses', 'relImpClassesData', self.relImpClassesData),
                                                #self.relatedImplementationClassesExplanation('architecture', 'architectureData', self.architectureData, title='Relations by architectural role'),
                                                #self.relatedImplementationClassesExplanation('rel3', title='Relations by diagram'),
                                                #self.relatedImplementationClassesExplanation('rel4', title='Intersecting features'),
                                                #self.relatedImplementationClassesExplanation('rel5', title='Summary')
                                                ]))
        
        line('script','document.getElementById("explanation").style.display = "none";')
        return doc.getvalue()

    def featureRoleExplanation(self, id, dataname, datastructure):
        doc, tag, text, line = Doc().ttl()
        self.hideButtonId += 1
        doc.asis(self.explanationTitle('Feature role', id, self.hideButtonId))
        with tag('div', id=id, style="display:block"):
            with tag('div', klass="w3-container w3-margin-top w3-margin-bottom"):
                with tag('div', klass="w3-border"):
                    with tag('div', klass="w3-white w3-padding", style="height:700px;"):
                        line('svg', '', id="graph_%s" % id, width="700", style="height:100%;width:100%;")
                        line('script', 'featureRoleGenerateGraph("graph_%s", %s)' % (id, dataname))
                    with tag('div', klass="w3-center w3-sand w3-padding"):
                        doc.asis('Relationship diagram showing entites related to feature role')
           
            for key in datastructure:
                doc.asis(self.explanationSection(key, key.upper(), self.sectionRowFactory(datastructure[key])))
        return doc.getvalue()

    def relatedImplementationClassesExplanation(self, id, dataname, datastructure = {}, title = 'Related implementation classes'):
        doc, tag, text, line = Doc().ttl()

        resultList = []
        for d in datastructure:
            self.recursiveSectionRowDictFactory(d, resultList)

        resultDict = {}
        for r in resultList:
            if r[1]['type'] not in resultDict.keys():
                resultDict[r[1]['type']] = []
            resultDict[r[1]['type']].append(r)

        self.hideButtonId += 1
        doc.asis(self.explanationTitle(title))
        with tag('div', style="display:block"):
            with tag('div', klass="w3-container w3-margin-top w3-margin-bottom"):
                with tag('div', klass="w3-border"):
                    with tag('div', klass="w3-white w3-padding", style="height:700px;"):
                        line('svg', '', id="graph_" + id, width="700", style="height:100%;width:100%;")
                        line('script', 'relationGenerateGraph("graph_%s", %s)' % (id, dataname))
                    with tag('div', klass="w3-center w3-sand w3-padding"):
                        doc.asis('Relationship diagram showing entites related to feature role')
            with tag('div', klass="w3-container w3-amber"):
                line('h4','FULL DESCRIPTION')
                line('button','Show', id=self.hideButtonId, klass='w3-button', onclick='hideView("%s", "%s")' % (id, self.hideButtonId))
            with tag('div', id=id):
                for key in resultDict:
                    doc.asis(self.explanationSection(key, key.upper(), self.sectionRowFactory(resultDict[key])))
        return doc.getvalue()

    def recursiveSectionRowDictFactory(self, dataDict, resultList):
        resultList.append(dataDict)
        if 'children' in dataDict[1].keys():
            for d in dataDict[1]['children']:
                self.recursiveSectionRowDictFactory(d, resultList)
        if 'implClasses' in dataDict[1].keys():
            for i in dataDict[1]['implClasses']:
                self.recursiveSectionRowDictFactory(i, resultList)

    def relationsByArchitecturalRoleExplanation(self):
        pass

    # Helpers for explanation view
    def explanationTitle(self, title, hideId=None, buttonId=None):
        doc, tag, text, line = Doc().ttl()
        with tag('div', klass="w3-border-bottom w3-border-deep-orange w3-container w3-amber"):
            with tag('div', style="float:left;"):
                doc.asis('<p><h3>%s</h3></p>' % title)
            if buttonId:
                with tag('button', id='%s' % buttonId, klass="w3-button w3-orange w3-margin", style="float:right; width:100px", onclick="hideView('%s', '%s')" % (hideId, buttonId)):
                    text('show')
        return doc.getvalue()

    def explanationSection(self, sectionId, sectionName, content):
        doc, tag, text, line = Doc().ttl()
        with tag('div', id=sectionId, klass="w3-border-top w3-border-amber"):
            with tag('div', klass='w3-khaki w3-padding'):
                line('h4', sectionName)
            doc.asis(content)
        return doc.getvalue()

    def emptySectionColumnItem(self, marginRight = False):
        doc, tag, text, line = Doc().ttl()
        c = "w3-border"
        if marginRight:
            c += " w3-margin-right"
        line('div', '', klass=c, style="flex:1;width:100px;")
        return doc.getvalue()

    def sectionRowFactory(self, columnList, rowSize=2):
        doc, tag, text, line = Doc().ttl()
        clist = []
        rlist = []
        counter = 0

        for column in columnList:
            counter += 1
            if 'dataTypeProperties' in column[1].keys():
                clist.append(self.sectionColumnItem(column[1]['object'], column[1]['dataTypeProperties'], True))
            else:
                clist.append(self.sectionColumnItem(column[1]['object'], marginRight = True))
            if counter%rowSize == 0:
                rlist.append(self.sectionRow(clist))
                clist.clear()
        if clist:
            while counter%rowSize != 0:
                counter += 1
                clist.append(self.emptySectionColumnItem(True))

        rlist.append(self.sectionRow(clist))

        for r in rlist:
            doc.asis(r)

        return doc.getvalue()

    def sectionRow(self, columnList):
        doc, tag, text, line = Doc().ttl()
        with tag('div', klass="w3-margin", style="display:flex;"):
            for c in columnList:
                doc.asis(c)
        return doc.getvalue()

    def sectionColumnItem(self, columnName, dataNameValuePairList = None, marginRight=False):
        doc, tag, text, line = Doc().ttl()

        c = "w3-border w3-white"
        if marginRight:
            c += " w3-margin-right"
        
        with tag('div', id=columnName, klass=c, style= "flex:1;width:100px;"):
            with tag('div', klass='w3-container w3-sand'):
                line('h5', columnName, klass="w3-margin-top", style='float:left')
                with tag('div', style='float:right', klass="w3-margin-bottom w3-margin-top w3-dropdown-hover"):
                    with tag('button', klass="w3-button w3-border"):
                        line('i','', klass="fa fa-caret-down")
                    with tag('div', klass="w3-dropdown-content w3-bar-block w3-card-4"):
                        line('button', 'Explain component', klass='w3-bar-item w3-button')
                        line('button', 'Explain relations', klass='w3-bar-item w3-button')
                        line('button', 'Explain architecture', klass='w3-button w3-bar-item')
        
                
            if dataNameValuePairList:
                with tag('div', klass="w3-container"):
                    for c in dataNameValuePairList:
                        line('p', '%s: %s' % (c[0], c[1]))
            else:
                with tag('div', klass="w3-display-container", style="height:200px;"):
                    with tag('div', klass="w3-display-middle"):
                        with tag('b'):
                            line('h3', 'No data properties', klass="w3-text-light-grey")
        return doc.getvalue()

    # ---------------------------------------------------------------------------------
    # Search view
    # ---------------------------------------------------------------------------------

    # Main normal search view component
    def normalSearchView(self):
        doc, tag, text, line = Doc().ttl()
        with tag('div', id="normalSearch", klass='searchView'):
            with tag('div', id='searchbar', klass='w3-container w3-amber'):
                with tag('p'):
                    doc.stag('input', klass="w3-input w3-border w3-sand", name="first", type="text", style='width:90%; float:left;')
                    line('button', 'Search', klass="w3-button w3-orange w3-border", onclick="showSearch()", style="width:10%;")
            
            with tag('div', id='resultsContainer', klass="", style='display:none'):
                with tag('div', klass='w3-container w3-white w3-border w3-margin'):
                    with tag('p', klass="w3-opacity"):
                        line('i','Results: Found 10 matches')
                with tag('div', klass='w3-container w3-white w3-border w3-margin'):
                    with tag('ul', klass='w3-ul'):
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
                        doc.asis(self.searchResultLi('some type','some name','Random description'))
        return doc.getvalue()

    # Main explanation search view component
    def explanationSearchView(self):
        doc, tag, text, line = Doc().ttl()
        with tag('div', id='expSearch', klass='searchView', style='display:none;'):
            with tag('div', id='searchbar', klass='w3-container w3-amber'):
                with tag('p'):
                    inputNames = ['featureRoleExplanation_input', 'architectureRole_input', 'designOption_input']
                    
                    with tag('div', klass="w3-container w3-khaki"):
                        line('h4', 'Explain feature role')
                        doc.stag('input', id=inputNames[0], klass="w3-input w3-border w3-sand", name="architectureFragment", type="text", style='width:90%; float:left;')
                        line('button', 'Search', klass="w3-button w3-orange w3-border w3-margin-bottom", onclick="openTab(event, 'explanation'); requestFeatureExplanation('%s');" % inputNames[0], style="width:10%;")
                        
                        line('h4', 'Show the entities with the same architectural roles')
                        doc.stag('input', id=inputNames[1], klass="w3-input w3-border w3-sand", name="architectureFragment", type="text", style='width:90%; float:left;')
                        line('button', 'Search', klass="w3-button w3-orange w3-border w3-margin-bottom", onclick="openTab(event, 'explanation'); requestArchitectureRoleExplanation('%s');" % inputNames[1], style="width:10%;")

                        line('h4', 'Show the entities with the same design options')
                        doc.stag('input', id=inputNames[2], klass="w3-input w3-border w3-sand", name="architectureFragment", type="text", style='width:90%; float:left;')
                        line('button', 'Search', klass="w3-button w3-orange w3-border w3-margin-bottom", onclick="openTab(event, 'explanation'); requestDesignOptionExplanation('%s');" % inputNames[2], style="width:10%;")


        return doc.getvalue()

    # Helpers for search
    def searchResultLi(self, intype, name, description):
        doc, tag, text, line = Doc().ttl()
        with tag('li'):
            with tag('div', style="width:20%;float:left;margin-right:10%;"):
                doc.asis('<p>Type: %s <br /> Name: %s </p>' % (intype, name))
            with tag('div'):
                line('p', description)
        return doc.getvalue()

    # Drop down component for search
    def searchDropdown(self, name, inputtext):
        doc, tag, text, line = Doc().ttl()
        line('button', inputtext, style="width:200px;text-align:left", klass="w3-bar-item w3-button", onclick="switchSearchView('%s', '%s')" % (name, inputtext))
        return doc.getvalue()

    def dropDown(self):
        doc, tag, text, line = Doc().ttl()
        with tag('div', klass="w3-dropdown-hover w3-amber w3-margin-top"):
            with tag('h3'):
                with tag('div', id="searchLabel", style="float:left;"):
                    text("Normal search")
                doc.asis("&nbsp&nbsp")
                line('i','', klass="fa fa-caret-down")
            with tag('div', klass="w3-dropdown-content w3-bar-block w3-card-4"):
                doc.asis(self.searchDropdown('normalSearch','Normal search'))
                doc.asis(self.searchDropdown('expSearch', 'Explanation'))
        return doc.getvalue()

    # ---------------------------------------------------------------------------------
    # Views
    # ---------------------------------------------------------------------------------
    def searchView(self):
        doc, tag, text, line = Doc().ttl()
        doc.asis(self.tabViewTitle('search', self.dropDown(), [self.normalSearchView(), self.explanationSearchView()]))
        return doc.getvalue()

    # -------------------------------------------------------------------------------------
    # Main HTML component
    # -------------------------------------------------------------------------------------

    # def createSideDescription(self, individual):
    #     doc, tag, text, line = Doc().ttl()
    #     qs = self.ir.pentaStructure(None, individual)
    #     with tag('div', id='sideDescriptionContent', klass="w3-border-left w3-container", style=''):
    #         with tag('div', klass='w3-margin-top', style='height:15%;width:100%;'):
    #             with tag('h3', style=""):
    #                 text(qs[1]['object'])
    #                 line('button', 'X', klass="w3-orange w3-button w3-margin-right", style="padding:0px 15px 0px 15px;position:absolute; right:0")
    #         with tag('div', klass='w3-border w3-border-orange w3-container w3-light-grey w3-margin-bottom', style=''):
    #             with tag('div', klass='w3-border-bottom w3-border-orange'):
    #                 line('h4', 'Type')
    #             line('p', qs[1]['type'])

    #         for dataTypeProperty in qs[1]['dataTypeProperties']:
    #             with tag('div', klass='w3-border w3-border-orange w3-container w3-light-grey w3-margin-bottom', style=''):
    #                 with tag('div', klass='w3-border-bottom w3-border-orange'):
    #                     line('h4', dataTypeProperty[0])
    #                 line('p', dataTypeProperty[1])
            
    #         with tag('div', klass='w3-border w3-border-orange w3-container w3-light-grey w3-margin-bottom', style=''):
    #             with tag('div', klass='w3-border-bottom w3-border-orange'):
    #                 line('h4', 'Rationale')
    #             for rationale in qs[1]['rationale']:
    #                 line('h5', self.ir.getTypeOfIndividual(rationale))
    #                 for r in self.ir.getDataProperties(rationale):
    #                     line('p', r[0])
    #                     line('p', r[1])

    #         for diagram in qs[1]['diagrams']:
    #             with tag('div', klass='w3-border w3-border-orange w3-container w3-light-grey w3-margin-bottom', style=''):
    #                 with tag('div', klass='w3-border-bottom w3-border-orange'):
    #                     line('h4', 'Diagram')
    #                 doc.stag('img', klass="w3-margin-top", src='static/images/'+ self.placeholderImage(diagram) +'.png', style='width:100%')
    #                 line('p', diagram)
    #                 for d in self.ir.getDataProperties(diagram):
    #                     line('p', d[0] + ':')
    #                     line('p', d[1])
                
    #     return doc.getvalue()

    def placeholderImage(self, diagramName):
        print("dname:" + str(diagramName))
        match = re.search('\\wigure_\\d\.\\d+', diagramName)
        finalString = re.sub('\.', '_', str(match.group(0)))
        return finalString.lower()

    def main(self):
        doc, tag, text, line = Doc().ttl()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            doc.asis('<meta name="viewport" content="width=device-width, initial-scale=1">')
            doc.asis('<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">')
            doc.asis('<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">')
            doc.asis('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">')
            doc.asis('<link rel="stylesheet" href="static/css/relationGraph.css"')

            
            with tag('head'):
                line('script','', src="https://d3js.org/d3.v5.min.js", charset="utf-8")
                line('script','', src="https://dagrejs.github.io/project/dagre-d3/latest/dagre-d3.js")
                line('script','', src="https://unpkg.com/tippy.js@2.5.0/dist/tippy.all.min.js")
                line('script','', src="https://code.jquery.com/jquery-3.1.1.min.js")
                line('script','', type = "text/javascript", src="static/tinycolor.js")
                line('script','', type = "text/javascript", src="static/helperJs.js")
                line('script','', type = "text/javascript", src="static/relationGraph.js")
                line('script','', type = "text/javascript", src="static/featureRoleGraph.js")

            with tag('style'):
                doc.asis('html { overflow-y: scroll; }')
            
            with tag('body'):

                #The design of the outmost container component
                with tag('div', style="display:flex"):

                    with tag('div', klass="w3-light-grey", style="flex: 2;"):
                        # Build up the tabs
                        with tag('div', klass="w3-bar w3-light-grey"):
                            doc.asis(self.tabs('Search','search'))
                            doc.asis(self.tabs('Explanation','explanation'))
                            doc.asis(self.tabs('History', 'history'))
                                
                        # All tab views
                        doc.asis(self.searchView())
                        doc.asis(self.explanationView())

                    with tag('div', klass="w3-amber w3-card-4 w3-border-left w3-border-orange", style="flex:1"):
                        with tag('div', klass="w3-bar w3-light-grey"):
                            doc.asis(self.tabs('Full explanation','fullExplanation'))
                            doc.asis(self.tabs('Selected component','component'))
                        line('div','', id='sideDescription')
                        
        return doc.getvalue()