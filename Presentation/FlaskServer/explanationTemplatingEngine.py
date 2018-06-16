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

    def getEntityFont(self, entityUri):
        words = [word.lower() for word in re.findall('[A-Z][^A-Z]*', explanationHelper.getNameFromUri(entityUri))]
        entityFont = '-'.join(words) + '-font'
        return entityFont

    def styledName(self, text, fontType='', entityType=''):
        if entityType:
            entitySupertypes = self.informationRetriever.getSuperClasses(entityType)
        else:
            entitySupertypes = self.informationRetriever.getSuperClasses(text)
        
        eType = entityType
        if entitySupertypes:
            if self.baseUri + 'DevelopmentStructure' in entitySupertypes:
                eType = 'DevelopmentStructure' 

            elif self.baseUri + 'DevelopmentBehavior' in entitySupertypes:
                eType = 'DevelopmentBehavior' 

            elif self.baseUri + 'LogicalStructure' in entitySupertypes:
                eType = 'LogicalStructure' 

            elif self.baseUri + 'LogicalBehavior' in entitySupertypes:
                eType = 'LogicalBehavior' 

            elif self.baseUri + 'UIStructure' in entitySupertypes:
                eType = 'UIStructure' 

            elif self.baseUri + 'UIBehavior' in entitySupertypes:
                eType = 'UIBehavior' 

            elif self.baseUri + 'PhysicalStructure' in entitySupertypes:
                eType = 'PhysicalStructure' 

        name = '<span class="{fontType} {entityFontName}">{textName}</span>'
        if entityType:
            name = name.format(fontType=fontType, entityFontName=self.getEntityFont(eType), textName=text)
        else:
            name = name.format(fontType=fontType, entityFontName=self.getEntityFont(text), textName=explanationHelper.getNameFromUri(text))
        return name

    def sectionSummary(self, typeUri):
        name = self.styledName(self.pluralEngine.plural(explanationHelper.formatName(explanationHelper.getNameFromUri(typeUri)), 2), 'class-font', entityType=typeUri)
        summary = 'This section lists the {name} and their descriptions'
        summary = summary.format(name=name)
        return summary

    def classesToText(self, entities):

        def addEntityType(entity, entityType, entityTypes):
            if entityType not in list(entityTypes.keys()):
                entityTypes[entityType] = []
                
            entityTypes[entityType].append(entity)

        entityTypes = {}
        for entity in entities:
            entityType = explanationHelper.getNameFromUri(entity.type)
            if entityType and not 'dummy' in entityType:
                addEntityType(entity, entityType, entityTypes)

        text = ''
        for index, entityType in enumerate(entityTypes):
            size = str(len(entityTypes[entityType]))
            text += self.styledName(size + ' ' + self.pluralEngine.plural(explanationHelper.formatName(entityType), size), 'class-font', self.baseUri + entityType)
            
            if index < len(entityTypes) - 2:
                text += ', '
            elif index == len(entityTypes) - 2:
                text += ' and '

        return text

    def createSection(self, entityList, id, title, summary='', priority=1):
        if entityList and not summary:
            section = sectionModel.Section(id, title, sectionSummary=self.sectionSummary(entityList[0].type), priority=priority)
        else:
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
                                    sectionSummary='', 
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

        summary = template.format(no_style_feature_name=explanationHelper.getNameOfEntity(feature_entity),
                                    feature_name=self.styledName(explanationHelper.getNameOfEntity(feature_entity), 'class-font', feature_entity.type),
                                    path=self.classesToText(structure.entities))

        question = self.getQuestion(summary)

        expTemplate = sectionModel.Template(question, summary)

        #Features section
        expTemplate.addSection(self.createSection([feature_entity], 'features_section', 'Feature', 
                               summary='', priority=3).toDict())

        #Requirements section
        expTemplate.addSection(self.createSection(requirements, 'requirements_section', 'FunctionalRequirement', 
                               summary='', priority=3).toDict())
       
        #Use cases section
        expTemplate.addSection(self.createSection(use_cases, 'use_case_section', 'UseCase', 
                               summary='', priority=2).toDict())
        
        #User story section
        expTemplate.addSection(self.createSection(user_stories, 'user_story_section', 'UserStory', 
                               summary='', priority=1).toDict())

        return expTemplate.toDict()

    def generateBehaviorSummary(self, featureUri, structure, viewType):
        if viewType == 'logical':
            structureTypeUri = 'LogicalStructure'
            behaviorTypeUri = 'LogicalBehavior'
            viewTypeUri = 'Logical'
        elif viewType == 'development':
            structureTypeUri = 'DevelopmentStructure'
            behaviorTypeUri = 'DevelopmentBehavior'
            viewTypeUri = 'Development'
        elif viewType == 'ui':
            structureTypeUri = 'UIStructure'
            behaviorTypeUri = 'UIBehavior'
            viewTypeUri = 'UI'
        else:
            return {}

        feature_entity = [entity for entity in structure.entities if entity.uri == featureUri][0]
        requirements =  list(filter(lambda e: e.type == self.baseUri + 'FunctionalRequirement', structure.entities))
        structures =  list(filter(lambda e: self.baseUri + structureTypeUri in e.supertypes, structure.entities))
        behavior =  list(filter(lambda e: self.baseUri + behaviorTypeUri in e.supertypes, structure.entities))
        diagrams = list(filter(lambda e: e.type == self.baseUri + 'Diagram', structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/BehaviorOfFeature.txt')

        summary = template.format(feature_name=self.styledName(explanationHelper.getNameOfEntity(feature_entity), 'entity-font', entityType=feature_entity.type),
                                    no_style_feature_name=explanationHelper.getNameOfEntity(feature_entity),
                                    point_of_view=self.styledName(viewType + ' point of view', 'class-font', entityType=self.baseUri + viewTypeUri), 
                                    path=self.classesToText(structure.entities))

        question = self.getQuestion(summary)

        expTemplate = sectionModel.Template(question, summary)

        #Requirements section
        sectionReqOverview = ''
        expTemplate.addSection(self.createSection(requirements, 'requirements_section', 'Requirement entities', 
                               summary=sectionReqOverview, priority=4).toDict())
        #Requirements section
        sectionStructOverview = ''
        expTemplate.addSection(self.createSection(structures, 'structures_section', 'Structure entities', 
                               summary=sectionStructOverview, priority=3).toDict())
        #Requirements section
        sectionBehOverview = ''
        expTemplate.addSection(self.createSection(behavior, 'behavior_section', 'Behavior entities', 
                               summary=sectionBehOverview, priority=2).toDict())
        #Requirements section
        sectionDiaOverview = ''
        expTemplate.addSection(self.createSection(diagrams, 'diagram_section', 'Diagram entities', 
                               summary=sectionDiaOverview, priority=1).toDict())

        return expTemplate.toDict()
       

    def generateRationaleSummary(self, pattern, structure):
        pattern_entity = [entity for entity in structure.entities if entity.uri == pattern][0]
        designOptions = list(filter(lambda e: self.baseUri + 'DesignOption' in e.supertypes, structure.entities))
        arguments = list(filter(lambda e: e.type == self.baseUri + 'Argument', structure.entities))
        assumptions = list(filter(lambda e: e.type == self.baseUri + 'Assumption', structure.entities))
        constraints = list(filter(lambda e: e.type == self.baseUri + 'Constraint', structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/RationaleOfArchitecture.txt')

        summary = template.format(no_style_arch_patt=explanationHelper.getNameOfEntity(pattern_entity),
                                    arch_patt=self.styledName(explanationHelper.getNameOfEntity(pattern_entity), 'class-font', pattern_entity.type),
                                    path=self.classesToText(structure.entities)
                                    )
        question = self.getQuestion(summary)

        expTemplate = sectionModel.Template(question, summary)

        #Choice section
        sectionDOOverview = ''
        expTemplate.addSection(self.createSection(designOptions, 'design_option_section', 'Design option entities', 
                               summary=sectionDOOverview, priority=4).toDict())
       
        #Arguments section
        sectionArgOverview = ''
        expTemplate.addSection(self.createSection(arguments, 'arguments_section', 'Argument entities', 
                               summary=sectionArgOverview, priority=3).toDict())
        
        #Constraint section
        sectionConOverview = ''
        expTemplate.addSection(self.createSection(constraints, 'constraint_section', 'Constraint entities', 
                               summary=sectionConOverview, priority=2).toDict())
        #Assumption section
        sectionAssOverview = ''
        expTemplate.addSection(self.createSection(assumptions, 'assumption_section', 'Assumption entities', 
                               summary=sectionAssOverview, priority=1).toDict())

        return expTemplate.toDict()
        
    # HOW IS THIS FEAURE MAPPED TO THE IMPLEMENTATION?
    # Detailed - Feature to implementation mapping
    def generateLogicalFeatureImplementationSummary(self, mainEntityUri, structure):
        # Setup the summary
        main_entity = [entity for entity in structure.entities if entity.uri == mainEntityUri][0]
        requirements = list(filter(lambda e: e.type == self.baseUri + 'FunctionalRequirement', structure.entities))
        logicalClasses = list(filter(lambda e: self.baseUri + 'LogicalClass' in e.supertypes, structure.entities))
        developmentClasses = list(filter(lambda e: self.baseUri + 'DevelopmentClass' in e.supertypes, structure.entities))
        developmentClassPackages = list(filter(lambda e: self.baseUri + 'DevelopmentClassPackage' in e.supertypes, structure.entities))
        developmentPackages = list(filter(lambda e: self.baseUri + 'Package' in e.supertypes, structure.entities))
        implementation = list(filter(lambda e: self.baseUri + 'ImplementationClass' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/LogicalViewImplementation.txt')
        entityName = explanationHelper.getNameOfEntity(main_entity)
        summary = template.format(no_style_feature_name=entityName,
                                  feature_name=self.styledName(explanationHelper.getNameOfEntity(main_entity), 'entity-font', entityType=main_entity.type), 
                                  target_type_name=self.styledName('implementation', 'class-font', entityType=self.baseUri + 'ImplementationClass'), 
                                  path_inbetween=self.classesToText(structure.entities))
        

        question = self.getQuestion(summary)
        expTemplate = sectionModel.Template(question, summary)
        
        #Logical section      
        logicalSection = self.createSection(logicalClasses, 'logical_section', 'Logical classes',
                               summary=self.sectionSummary(logicalClasses[0].type), priority=3)

        overviewDiagrams = self.getOverviewDiagrams(structure, 'LogicalStructure')
        
        overviewIdCounter = 0
        for key, value in overviewDiagrams.items():
            dummySection = sectionModel.Section('overview' + str(overviewIdCounter), value['name'], sectionSummary=value['description'], sectionDiagrams=[{'uri': key, 'caption': value['caption']}])
            overviewIdCounter += 1
        overviewSectionSummary = 'This section presents and describes diagrams that encapsulate all of the logical classes found in this explanation.'
        overviewSection = sectionModel.Section('logical_overview', 'Overview', sectionSummary=overviewSectionSummary, priority=99)
        overviewSection.addChild(dummySection.toDict())
        logicalSection.addChild(overviewSection
        .toDict())

        expTemplate.addSection(logicalSection.toDict())

        #Implementation section
        expTemplate.addSection(self.createSection(implementation, 'implementation_section', 'Implementation classes', 
                               summary=self.sectionSummary(implementation[0].type), priority=1).toDict())
        if developmentClasses:
            #Development structure section
            expTemplate.addSection(self.createSection(developmentClasses, 'developmentClass_section', 'Development classes', 
                                summary=self.sectionSummary(developmentClasses[0].type), priority=2).toDict())
        if developmentClassPackages:
            #Development structure section
            expTemplate.addSection(self.createSection(developmentClassPackages, 'developmentClassPackage_section', 'Development class packages', 
                                summary=self.sectionSummary(developmentClassPackages[0].type), priority=2).toDict())
        if developmentPackages:
            #Development structure section
            expTemplate.addSection(self.createSection(developmentPackages, 'developmentPackage_section', 'Development packages', 
                                summary=self.sectionSummary(developmentPackages[0].type), priority=2).toDict())

        #Requirements section
        expTemplate.addSection(self.createSection(requirements, 'requirements_section', 'Functional requirements', 
                               summary=self.sectionSummary(requirements[0].type), priority=4).toDict())

        #Feature section
        expTemplate.addSection(self.createSection([main_entity], 'feature_section', 'Feature',
                               summary=self.sectionSummary(main_entity.type), priority=5).toDict())
       
        return expTemplate.toDict()
        
    def generateSystemFunctionalitySummary(self, structure):      

        features = list(filter(lambda e: self.baseUri + 'Feature' in e.supertypes, structure.entities))
        funcreqs = list(filter(lambda e: self.baseUri + 'FunctionalRequirement' in e.supertypes, structure.entities))
        userstories = list(filter(lambda e: self.baseUri + 'UserStory' in e.supertypes, structure.entities))
        usecases = list(filter(lambda e: self.baseUri + 'UseCase' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/SystemFunctionality.txt')
        summary = template.format(path=self.classesToText(structure.entities))
        question = self.getQuestion(summary)
  
        expTemplate = sectionModel.Template(question, summary)

        #Feature section
        expTemplate.addSection(self.createSection(features, 'feature_section', 'Feature',
                               summary='', priority=5).toDict())

        #Fuctional requirements section
        expTemplate.addSection(self.createSection(funcreqs, 'func_req_section', 'Functional Requirements',
                               summary='', priority=3).toDict())

        #User story section
        expTemplate.addSection(self.createSection(userstories, 'user_story_section', 'User stories',
                               summary='', priority=3).toDict())

        #Use case section
        expTemplate.addSection(self.createSection(usecases, 'use_case_section', 'Use cases',
                               summary='', priority=3).toDict())


        return expTemplate

    # Overview - Feature to implementation mapping
    def generateFunctionalFeatureImplementationSummary(self, mainEntityUri, structure):      
        mainEntity = [entity for entity in structure.entities if entity.uri == mainEntityUri][0]
        impl = list(filter(lambda e: self.baseUri + 'ImplementationClass' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/FunctionalViewImplementation.txt')
        summary = template.format(feature_name=self.styledName(explanationHelper.getNameOfEntity(mainEntity), 'class-font', mainEntity.type),
                                  no_style_feature_name=explanationHelper.getNameOfEntity(mainEntity),
                                  path=self.classesToText(structure.entities)
                                  )
        question = self.getQuestion(summary)
  
        expTemplate = sectionModel.Template(question, summary)

        #Feature section
        sectionFeatureOverview = ''
        expTemplate.addSection(self.createSection([mainEntity], 'feature_section', 'Feature',
                               summary=sectionFeatureOverview, priority=5).toDict())

        #Implmentation section
        sectionImplOverview = ''
        sectionImplOverview = sectionImplOverview.format(main_entity=explanationHelper.getNameOfEntity(mainEntity))
        expTemplate.addSection(self.createSection(impl, 'impl_section', 'Implementation classes',
                               summary=sectionImplOverview, priority=3).toDict())


        return expTemplate
        
    # Pattern - Feature to implementation mapping
    def generatePatternFeatureImplementationSummary(self, mainEntityUri, structure):
        
        mainEntity = ontologyStructureModel.Entity(mainEntityUri)
        impl = list(filter(lambda e: e.type == self.baseUri + 'ImplementationClass', structure.entities))
        role = list(filter(lambda e: e.type == self.baseUri + 'Role', structure.entities))
        arch = list(filter(lambda e: e.type == self.baseUri + 'ArchitecturalPattern', structure.entities))
        developmentClasses = list(filter(lambda e: self.baseUri + 'DevelopmentClass' in e.supertypes, structure.entities))
        developmentClassPackages = list(filter(lambda e: self.baseUri + 'DevelopmentClassPackage' in e.supertypes, structure.entities))
        developmentPackages = list(filter(lambda e: self.baseUri + 'DevelopmentPackage' in e.supertypes, structure.entities))

        template = explanationHelper.openText('static/explanationTemplates/PatternViewImplementation.txt')
        summary = template.format(impl_class=self.styledName('Implementation classes','class-font', self.baseUri + 'ImplementationClass'),
                                  arch_patt=self.styledName('Architectural patterns', 'class-font', self.baseUri + 'ArchitecturalPattern'),
                                  path_inbetween=self.classesToText(structure.entities)
                                  )
        question = self.getQuestion(summary)

        sectionImplOverview = ''
        sectionImplOverview = sectionImplOverview.format(main_entity=explanationHelper.getNameOfEntity(mainEntity))
        
        expTemplate = sectionModel.Template(question, summary)

        implSection = self.createSection(impl, 'impl_section', 'Implementation classes',
                               summary=sectionImplOverview, priority=4)
        
        if developmentClasses:
            expTemplate.addSection(self.createSection(developmentClasses, 'developmentClass_section', 'Development classes', 
                                summary=self.sectionSummary(developmentClasses[0].type), priority=2).toDict())
        if developmentClassPackages:
            expTemplate.addSection(self.createSection(developmentClassPackages, 'developmentClassPackage_section', 'Development class packages', 
                                summary=self.sectionSummary(developmentClassPackages[0].type), priority=2).toDict())
        if developmentPackages:
            expTemplate.addSection(self.createSection(developmentPackages, 'developmentPackage_section', 'Development packages', 
                                summary=self.sectionSummary(developmentPackages[0].type), priority=2).toDict())


        sectionRoleOverview = ''
        roleSection = self.createSection(role, 'role_section', 'Roles',
                               summary=sectionRoleOverview, priority=2)
        
        sectionArchOverview = ''
        archSection = self.createSection(arch, 'arch_section', 'Architectural patterns',
                               summary=sectionArchOverview, priority=1)

        expTemplate.addSection(implSection.toDict())
        expTemplate.addSection(roleSection.toDict())
        expTemplate.addSection(archSection.toDict())

        return expTemplate

    def generatePopupFigureDescription(self, figureUri):
        figureEntity = ontologyStructureModel.Entity(figureUri)
        
        template = explanationHelper.openText('static/explanationTemplates/FigureSummary.txt')
        
        relatedEntityUris = [ontologyStructureModel.Entity(entity[1]) for entity in self.informationRetriever.getRelations(figureUri, self.baseUri + 'models')]
        summary = template.format(classes=self.classesToText(relatedEntityUris))
        question = {'sub': 'View diagrams','orginial': ''}


        figureid = 'popup_' + explanationHelper.diagramUriToFileName(explanationHelper.getNameFromUri(figureUri)) 
        figuretitle = explanationHelper.getNameOfEntity(figureEntity)
        figureSummary = ''

        entityid = 'popup_entity_overview_' + explanationHelper.diagramUriToFileName(explanationHelper.getNameFromUri(figureUri)) 
        entitySummary = ''

        # relatedEntities = [ontologyStructureModel.Entity(e) for e in relatedEntityUris]
        relatedEntities = relatedEntityUris
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

def testGetBehavior():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    print(ir.getBehavior(baseUri + 'UIStructure', baseUri + 'UIBehavior'))

def testGetLogicalBehavior():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    print(eg.getDevelopmentBehaviorOfFeature(baseUri + 'purchase_products'))

def testSameAs():
    ir = sparqlQueryManager.InformationRetriever()
    eg = explanationStructureGenerator.ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    print(ir.getRelations(baseUri + 'UI_ProductsDetail', 'owl:sameAs', baseUri + 'UIBehavior'))

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

# testGetDirectSuperClass()
# testGetBehavior()
# testGetLogicalBehavior()
# testSameAs()
# eg = explanationStructureGenerator.ExplanationGenerator()
# eg.constructMetaModel()
# print('ding!')