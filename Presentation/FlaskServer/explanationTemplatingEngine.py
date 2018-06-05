import requests, json, re, inflect
import ontologyStructureModel, sparqlQueryManager, sectionModel
import explanationStructureGenerator, explanationHelper

class ExplanationTemplates:
    def __init__(self):
        self.baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        self.informationRetriever = sparqlQueryManager.InformationRetriever()
        self.pluralEngine = inflect.engine()

    def getQuestion(self, summary):
        firstMatch = re.search('<!--[ ]*{[ ]*question:.*?}[ ]*-->', summary)
        question = ''
        question2 = ''
        
        if firstMatch:
            question = firstMatch.group(0)
            question = re.sub('<!--[ ]*{[ ]*question:[ ]*', '', question)
            question = re.sub('[ ]*}[ ]*-->', '', question)

        secondMatch = re.search('<!--[ ]*{[ ]*original question:.*?}[ ]*-->', summary)

        if secondMatch:
            question2 = secondMatch.group(0)
            question2 = re.sub('<!--[ ]*{[ ]*original question:[ ]*', '', question2)
            question2 = re.sub('[ ]*}[ ]*-->', '', question2)

        return {'original': question2, 'sub': question}

    def classesToText(self, entities):
        entityTypes = {}
        for entityUri in entities:
            entity = ontologyStructureModel.Entity(entityUri)
            entityType = explanationHelper.getNameFromUri(entity.type)
            
            if entityType not in list(entityTypes.keys()):
                entityTypes[entityType] = []
            
            entityTypes[entityType].append(entity)

        text = ''
        for index, entityType in enumerate(entityTypes):
            size = str(len(entityTypes[entityType]))
            text += size + ' ' + self.pluralEngine.plural(explanationHelper.formatName(entityType), size)
            if index < len(entityTypes) - 2:
                text += ', '
            elif index == len(entityTypes) - 2:
                text += 'and'

        return text

    def createSection(self, entityList, id, title, summary='', priority=1):
        section = sectionModel.Section(id, title, sectionSummary=summary, priority=priority)

        for entity in entityList:
            diagrams = []
            for diagram in entity.diagrams:
                caption = self.informationRetriever.getRelations(diagram, self.baseUri + 'Caption')
                if caption:
                    caption = caption[0][1]

                diagrams.append({'uri': diagram, 'caption': caption})

            entitySection = sectionModel.Section(explanationHelper.getNameFromUri(entity.uri), 
                                    explanationHelper.getNameOfEntity(entity),
                                    entityType=explanationHelper.getNameFromUri(entity.type),
                                    sectionSummary='This section shortly describes the ' + explanationHelper.formatName(explanationHelper.getNameFromUri(entity.type)) + ' ' + explanationHelper.getNameOfEntity(entity) + '.', 
                                    sectionTextContent=[(explanationHelper.getNameFromUri(content[0]), content[1]) for content in entity.dataTypeProperties], 
                                    sectionDiagrams=diagrams)
            section.addChild(entitySection.toDict())
        return section

    def getOverviewDiagrams(self, structure, overviewGroup):
        logical = [l.uri for l in list(filter(lambda e: self.baseUri + overviewGroup in e.supertypes, structure.entities))]
        diagrams = [d[1] for d in self.informationRetriever.getRelations(sub=logical[0], objType=self.baseUri + 'Diagram')]

        overviewDiagrams = {}
        for diagram in diagrams:
            fullDiagramRelations =  self.informationRetriever.getRelations(sub=diagram)
            diagramRelations = [dr[1] for dr in fullDiagramRelations]
            if set(logical) < set(diagramRelations):
                overviewDiagramDescription = [description[1] for description in fullDiagramRelations if '#Description' in description[0]][0]
                overviewDiagramCaption = [caption[1] for caption in fullDiagramRelations if '#Caption' in caption[0]][0]

                overviewDiagrams[diagram] = {'name': explanationHelper.formatDiagramName(explanationHelper.getNameFromUri(diagram)), 'description' : overviewDiagramDescription, 'caption': overviewDiagramCaption}
        return overviewDiagrams

    # ----------------------------------------------------------------------------------------
    # EXPLANATIONS
    # ----------------------------------------------------------------------------------------
   
    def generateFeatureRoleSummary(self, featureUri, structure):
        feature_entity = [entity for entity in structure.entities if entity.uri == featureUri][0]
        requirements = list(filter(lambda e: e.type == self.baseUri + 'FunctionalRequirement', structure.entities))
        use_cases = list(filter(lambda e: e.type == self.baseUri + 'UseCase', structure.entities))
        user_stories = list(filter(lambda e: e.type == self.baseUri + 'UserStory', structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/FeatureRole.txt')

        summary = template.format(feature_name=explanationHelper.getNameOfEntity(feature_entity))

        question = self.getQuestion(summary)

        expTemplate = sectionModel.Template(question, summary)

        #Requirements section
        sectionReqOverview = 'This section contain the descriptions of the functional requirements'
        expTemplate.addSection(self.createSection(requirements, 'requirements_section', 'Requirement entities', 
                               summary=sectionReqOverview, priority=1).toDict())
       
        #Use cases section
        sectionUCOverview = 'This section contain descriptions of the the use cases.'
        expTemplate.addSection(self.createSection(use_cases, 'use_case_section', 'Use case entities', 
                               summary=sectionUCOverview, priority=2).toDict())
        
        #User story section
        sectionUSOverview = 'This section contain descriptions of the the user stories.'
        expTemplate.addSection(self.createSection(user_stories, 'user_story_section', 'User story entities', 
                               summary=sectionUSOverview, priority=3).toDict())

        return expTemplate.toDict()


    # HOW IS THIS FEAURE MAPPED TO THE IMPLEMENTATION?
    def generateLogicalFeatureImplementationSummary(self, mainEntityUri, structure):
        # Setup the summary
        main_entity = [entity for entity in structure.entities if entity.uri == mainEntityUri][0]
        requirements = list(filter(lambda e: e.type == self.baseUri + 'FunctionalRequirement', structure.entities))
        logical = list(filter(lambda e: self.baseUri + 'LogicalStructure' in e.supertypes, structure.entities))

        rel_feat_req = 'comprises of'
        rel_req_logic = 'satisfied by'
        rel_logic_dev = 'designed by'
        rel_dev_impl = 'implemented by'

        template = explanationHelper.openText('static/explanationTemplates/LogicalViewImplementation.txt')
        summary = template.format(main_entity=explanationHelper.getNameOfEntity(main_entity), 
                                    rel_feat_req=rel_feat_req, rel_logic_dev=rel_logic_dev,
                                    rel_req_logic=rel_req_logic, rel_dev_impl=rel_dev_impl,
                                    nbr_req=len(requirements), nbr_logic=len(logical))

        question = self.getQuestion(summary)
        expTemplate = sectionModel.Template(question, summary)
        
        #Logical section
        sectionLogicalOverview = 'This section describes each entity of the Logical view '\
                                 'that are related to the feature Purchase products.'
        
        logicalSection = self.createSection(logical, 'logical_section', 'Logical entities',
                               summary=sectionLogicalOverview, priority=3)

        overviewDiagrams = self.getOverviewDiagrams(structure, 'LogicalStructure')
        
        overviewIdCounter = 0
        for key, value in overviewDiagrams.items():
            dummySection = sectionModel.Section('overview' + str(overviewIdCounter), value['name'], sectionSummary=value['description'], sectionDiagrams=[{'uri': key, 'caption': value['caption']}])
            overviewIdCounter += 1
        overviewSectionSummary = 'This section presents and describes diagrams that encapsulate all of the logical entities found in this explanation.'
        overviewSection = sectionModel.Section('logical_overview', 'Overview', sectionSummary=overviewSectionSummary, priority=99)
        overviewSection.addChild(dummySection.toDict())
        logicalSection.addChild(overviewSection
        .toDict())

        expTemplate.addSection(logicalSection.toDict())

        #Requirements section
        sectionReqOverview = 'This section describes each functional requirement that '\
                             'are part of the feature Purchase products.'
        expTemplate.addSection(self.createSection(requirements, 'requirements_section', 'Requirement entities', 
                               summary=sectionReqOverview, priority=2).toDict())

        #Feature section
        sectionFeatureOverview = 'This section describes the feature Purchase Products'
        expTemplate.addSection(self.createSection([main_entity], 'feature_section', 'Feature',
                               summary=sectionFeatureOverview, priority=1).toDict())
       
        return expTemplate.toDict()
        
    def generateFunctionalFeatureImplementationSummary(self, mainEntityUri, structure):
        
        mainEntity = [entity for entity in structure.entities if entity.uri == mainEntityUri][0]
        req = list(filter(lambda e: e.type == self.baseUri + 'FunctionalRequirement', structure.entities))
        impl = list(filter(lambda e: self.baseUri + 'ImplementationClass' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/FunctionalViewImplementation.txt')
        summary = template.format(main_entity=explanationHelper.getNameOfEntity(mainEntity), nbr_requirements=len(req), nbr_implementation=len(impl))
        question = self.getQuestion(summary)

        sectionImplOverview = 'This section shows all implementation classes related to {main_entity}.'
        sectionImplOverview = sectionImplOverview.format(main_entity=explanationHelper.getNameOfEntity(mainEntity))
        implSection = self.createSection(impl, 'impl_section', 'Implementation classes',
                               summary=sectionImplOverview, priority=3)

        expTemplate = sectionModel.Template(question, summary)
        expTemplate.addSection(implSection.toDict())

        return expTemplate
        
    def generatePatternFeatureImplementationSummary(self, mainEntityUri, structure):
        
        mainEntity = ontologyStructureModel.Entity(mainEntityUri)
        impl = list(filter(lambda e: e.type == self.baseUri + 'ImplementationClass', structure.entities))
        role = list(filter(lambda e: e.type == self.baseUri + 'Role', structure.entities))
        arch = list(filter(lambda e: e.type == self.baseUri + 'ArchitecturalPattern', structure.entities))
        dev = list(filter(lambda e: self.baseUri + 'DevelopmentStructure' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/PatternViewImplementation.txt')
        summary = template.format(main_entity=explanationHelper.getNameOfEntity(mainEntity), nbr_impl=len(impl), nbr_dev=len(dev),
                                  nbr_role=len(role), nbr_arch_patt=len(arch))
        question = self.getQuestion(summary)

        sectionImplOverview = 'This section shows all implementation classes related to {main_entity}.'
        sectionImplOverview = sectionImplOverview.format(main_entity=explanationHelper.getNameOfEntity(mainEntity))
        
        implSection = self.createSection(impl, 'impl_section', 'Implementation classes',
                               summary=sectionImplOverview, priority=1)
        
        sectionRoleOverview = 'This section shows all architectural pattern roles that are implemented by the implementation classes'
        roleSection = self.createSection(role, 'role_section', 'Pattern roles',
                               summary=sectionRoleOverview, priority=3)
        
        sectionDevOverview = 'This section shows all development entities related to the implementation classes.'
        devSection = self.createSection(dev, 'dev_section', 'Development entities',
                               summary=sectionDevOverview, priority=2)
        
        sectionArchOverview = 'This section shows all architectural patterns related to the pattern roles and implementation classes.'
        archSection = self.createSection(arch, 'arch_section', 'Architectural patterns',
                               summary=sectionArchOverview, priority=4)

        expTemplate = sectionModel.Template(question, summary)
        expTemplate.addSection(implSection.toDict())
        expTemplate.addSection(roleSection.toDict())
        expTemplate.addSection(archSection.toDict())
        expTemplate.addSection(devSection.toDict())

        return expTemplate

    def generatePopupFigureDescription(self, figureUri):
        figureEntity = ontologyStructureModel.Entity(figureUri)
        
        template = explanationHelper.openText('static/explanationTemplates/FigureSummary.txt')
        
        relatedEntityUris = [entity[1] for entity in self.informationRetriever.getRelations(figureUri, self.baseUri + 'models')]
        summary = template.format(classes=self.classesToText(relatedEntityUris))
        question = {'sub': 'View diagrams','orginial': ''}


        figureid = 'popup_' + explanationHelper.diagramUriToFileName(explanationHelper.getNameFromUri(figureUri)) 
        figuretitle = explanationHelper.getNameOfEntity(figureEntity)
        figureSummary = ''

        entityid = 'popup_entity_overview_' + explanationHelper.diagramUriToFileName(explanationHelper.getNameFromUri(figureUri)) 
        entitySummary = 'This section shows short descriptions of each entity illustrated the diagram.'

        relatedEntities = [ontologyStructureModel.Entity(e) for e in relatedEntityUris]
        figureSection = sectionModel.Section(figureid, figuretitle, figureSummary, priority=5,
                        sectionTextContent=[(explanationHelper.getNameFromUri(content[0]), content[1]) for content in figureEntity.dataTypeProperties])
        entitySection = self.createSection(relatedEntities, entityid, 'Entities related to diagram', entitySummary)

        template = sectionModel.Template(question, summary)
        template.addSection(figureSection.toDict())
        template.addSection(entitySection.toDict())

        return template

def testing():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    es = eg.getLogicalFeatureToImplementationMap(baseUri + 'purchase_products')
    # es = [explanationHelper.formatName(explanationHelper.getNameFromUri(uri)) for uri in ir.getIndividualsByType(baseUri + 'Logical')]
    
    # f = open('LogicalClassDiagramText.txt', 'r')
    # text = f.read()
    # f.close()
    
    # es = ['product', 'order', 'cart']
    # for entity in es:
    #     text = re.sub(r'('+ entity +'(s*)(es)*)', r'<font color="#68aeff">\1</font>', text, flags=re.IGNORECASE)
    # print(text)
    return es

def testAutomaticFindPath():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    # es = eg.constructMetaModel()
    es = eg.loadMetaModel()
    paths = eg.getMetaModelPath(es, baseUri + 'Feature', baseUri + 'FunctionalRequirement')
    for path in paths:
        print('_______________START______________')
        for rel in path:
            print('source:' + explanationHelper.getNameFromUri(rel['source']))
            print('name:' + explanationHelper.getNameFromUri(rel['name']))
            print('target:' + explanationHelper.getNameFromUri(rel['target']))
            print('_____')
    


def testGetAllObjectsAndRelations():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    es = ir.getAllObjectsAndRelations()
    return es

def testGetAllTypes():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#' 
    print(ir.getAllOntologyTypes())

def testGetTypeRelations():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#' 
    print(ir.getTypeRelation(baseUri + 'ArchitectureFragment'))

def testGetAllTypeRelations():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#' 
    print(ir.getAllTypeRelations())

def testGetDirectSuperClass():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    print(ir.getDirectSuperClass(baseUri + 'Technology'))

# def writeToFile(inputData):
#     f = open('../ExperimentationGraphs/static/explanationData.js', 'w') 
#     f.truncate(0)
#     f.write("ontologyData = " + json.dumps(inputData))
#     f.close()

def writeToFile(inputData):
    f = open('../ExperimentationGraphs/static/Test.txt', 'w') 
    f.truncate(0)
    f.write(inputData)
    f.close()

testGetDirectSuperClass()