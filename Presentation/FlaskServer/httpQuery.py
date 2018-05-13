import requests
import json
import re
import inflect

from SPARQLWrapper import SPARQLWrapper, JSON

# A class for ontology entities
class Entity:
    def __init__(self, entityUri, baseURI = ''):
        if baseURI:
            baseUri = baseURI
        else:
            baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        ir = InformationRetriever()

        self.uri = entityUri
        self.label = ir.getLabel(entityUri)
        self.type = ir.getTypeOfIndividual(entityUri)
        self.supertypes = ir.getSuperTypes(entityUri)
        self.dataTypeProperties = ir.getDataProperties(entityUri)
        self.diagrams = []

        for diagram in ir.getRelations(entityUri, baseUri + 'modeledIn', baseUri + 'Diagram'):
            self.diagrams.append(diagram[1])

    def __repr__(self):
        return "{PythonClass: Entity, Name: " + self.label + ", Type: " + self.type + "}"
    
    def toDict(self):
        return {'uri': self.uri, 'label': self.label, 'type': self.type, 'supertypes': self.supertypes,
                'dataTypeProperties': self.dataTypeProperties, 'diagrams': self.diagrams}

# Dummy entity
class DummyEntity(Entity):
    def __init__(self, id, label='', entityType='', supertypes=None):
        self.uri = 'dummy_' + id
        self.label = label
        if entityType:
            self.type = entityType
        else:
            self.type = self.uri + '_type'
        self.dataTypeProperties = []
        self.diagrams = []

        if supertypes:
            self.supertypes = supertypes
        else:
            self.supertypes = []
        
        if self.type and self.type not in self.supertypes:
            self.supertypes.append(self.type)

    def toDict(self):
        return {'uri': self.uri, 'label': self.label, 'type': self.type, 'supertypes': self.supertypes,
                'dataTypeProperties': self.dataTypeProperties, 'diagrams': self.diagrams}

# A class for ontology relations
class Relation:
    def __init__(self, name, source, target):
        self.name = name
        self.source = source
        self.target = target
    
    def toDict(self):
        return {'name': self.name, 'source': self.source, 'target': self.target}
    
    def __repr__(self):
        return  '{PythonClass: Relation, Name: ' + self.name + ', Source: ' + self.source + ', Target: ' + self.target + '}'

# Entity structure should be populated by entities first and then relations.
# Relations with sources/targets that do not already exist in the structure 
# will not be added.
class EntityStructure:
    def __init__(self):
        self.ir = InformationRetriever()
        self.entities = []
        self.relations = []
        self.structure = {}
        self.structure['relations'] = self.relations
        self.structure['entities'] = self.entities

    def getNameFromUri(self, uri):
        return (re.sub(".+#", '', uri))	

    def addEntity(self, entity):
        if isinstance(entity, str) and not self.hasEntity(entity):
            self.entities.append(Entity(entity))
        
        elif isinstance(entity, Entity) and not self.hasEntity(entity.uri):
            self.entities.append(entity)
    
    def addAllEntities(self, entityList):
        if isinstance(entityList, list):
            for e in entityList:
                self.addEntity(e)

    def addRelation(self, relation, source=None, target=None):
        if isinstance(relation, Relation):
            if self.hasEntity(relation.source) and self.hasEntity(relation.target) and not self.hasRelation(relation):
                self.relations.append(relation)
        
        elif isinstance(relation, str) and source and target: 
            self.addRelation(Relation(relation, source, target))

    def addOneToManyRelation(self, relationName, source, target):
        if isinstance(source, list) and isinstance(target, str):
            for s in source:
                if isinstance(s, str):
                    self.addRelation(relationName, s, target)
        elif isinstance(source, str) and isinstance(target, list):
            for t in target:
                if isinstance(t, str):
                    self.addRelation(relationName, source, t)
    
    def addAllRelations(self, relationList):
        if isinstance(relationList, list):
            for r in relationList:
                self.addRelation(r)

    def hasEntity(self, entityUri):
        for entity in self.entities:
            if entity.uri == entityUri:
                return True
        return False
    
    def hasRelation(self, relation):
        for r in self.relations:
            if relation.source == r.source and relation.target == r.target and relation.name == r.name:
                return True
        return False

    def __repr__(self):
        output = "{{entities: [{entities}], relations: [{relations}]}}"
        entitiesStr = ""
        relationsStr = ""
        entitiesEnd = len(self.entities)-1
        relationsEnd = len(self.relations)-1

        for index, entity in enumerate(self.entities):
            if index < entitiesEnd:
                entitiesStr += self.getNameFromUri(entity.uri) + ', '
            else:
                entitiesStr += self.getNameFromUri(entity.uri)

        for index, relation in enumerate(self.relations):
            if index < relationsEnd:
                relationsStr += '(' + self.getNameFromUri(relation.name) + ', ' + self.getNameFromUri(relation.source) + ', ' + self.getNameFromUri(relation.target) + ')' + ', '
            else:
                relationsStr += '(' + self.getNameFromUri(relation.name) + ', ' + self.getNameFromUri(relation.source) + ', ' + self.getNameFromUri(relation.target) + ')'
        return output.format(entities=entitiesStr, relations=relationsStr)

    def toDict(self):
        returnDict = {}
        returnDict['entities'] = []
        returnDict['relations'] = []
        for e in self.entities:
            returnDict['entities'].append(e.toDict())
        for r in self.relations:
            returnDict['relations'].append(r.toDict())
        return returnDict

# A class for retrieving data from the ontology. It uses SparQL.
class InformationRetriever:
    def __init__(self, url=None):
        if not url:
            self.sparql = SPARQLWrapper('http://localhost:3030/Thesis')
    
    def query(self, query):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()

    def toQueryUri(self, uri):
        return '<' + uri + '>'

    #-----------------------------------------------------------------------------------------
    # 1. BASIC QUERY HELPER METHODS
    #-----------------------------------------------------------------------------------------

    
    def getSuperTypes(self, subjectUri):
        subjectUri = self.toQueryUri(subjectUri)
        query = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"\
                "SELECT * WHERE {{" \
                "{subjectUri} rdf:type ?supertype  ."\
                "FILTER (regex(str(?supertype), 'http://www.semanticweb.org/ontologies/snowflake')) }}"
        query = query.format(subjectUri=subjectUri)
        supertypes = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            if results:
                for r in results:
                    supertypes.append(r['supertype']['value'])
                return supertypes
        except:      
            return ''

    def getLabel(self, subjectUri):
        subjectUri = self.toQueryUri(subjectUri)
        query = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"\
                "SELECT ?label WHERE {{{subjectUri} rdfs:label ?label}}"
        query = query.format(subjectUri=subjectUri)
        
        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            if results:
                return results[0]['label']['value']
            else:
                return ''
        except:      
            return ''

    def getAllInverses(self):
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
                "SELECT DISTINCT ?pred1 ?pred2 WHERE {{?pred a owl:ObjectProperty . ?pred1 owl:inverseOf ?pred2}}"
        
        predicatePairs = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                predicatePairs.append((item['pred1']['value'], 
                                item['pred2']['value']))
        except:
            pass
        return predicatePairs

    def getAllObjectsAndRelations(self):
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
                "SELECT ?sub ?pred ?obj WHERE {{?pred a owl:ObjectProperty . ?sub ?pred ?obj}}"
        individuals = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                if("http://www.w3.org/2002/07/owl#" not in item['pred']['value']):
                    individuals.append((item['sub']['value'], 
                                        item['pred']['value'],
                                        item['obj']['value']))
        except:
            pass
        return individuals
    
    def getAllObjects(self):
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
                "SELECT DISTINCT ?sub WHERE {{?sub a owl:Thing . ?sub ?pred ?obj}}"
        individuals = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                individuals.append(item['sub']['value'])
        except:
            pass
        return individuals

    def getIndividualsByType(self, inputType):
        inputType = self.toQueryUri(inputType)
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
                "SELECT * WHERE {{?individual a {t} }}"
        query = query.format(t=inputType)
        individuals = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                individuals.append(item['individual']['value'])
        except:
            pass
        return individuals

    def checkRelation(self, sub, obj):
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#>"\
                "SELECT ?pred WHERE {{"\
                "?pred a owl:ObjectProperty . "\
                "{sub} ?pred {obj} }}"
        query = query.format(sub=sub, obj=obj)
        predicates = []
        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                predicates.append(item['pred']['value'])
        except:
            pass
        return predicates

    # getRelations() returns all predicates from the given subject to an object in a list.
    # useInversePred determines whether to use the given predicate or to use the inverse of it.
    # always returns a tuple in the following format: (predicate, object)
    def getRelations(self, sub, pred="", objType="", useInversePred=False):
        # 1. Starts with building up the query depending on input parameters
        sub = self.toQueryUri(sub)
        if pred:
            pred = self.toQueryUri(pred)
        if objType:
            objType = self.toQueryUri(objType)

        query ="PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
               "SELECT * WHERE {{ "\
               "{objectType} "\
               "{subject} {predicate} ?object "\
               "{predBind} "\
               "}}"
        predBind = ""
        b = ""

        if pred:
            if useInversePred:
                b = "^"
                predBind = ". {{SELECT ?predicate WHERE {{?predicate owl:inverseOf {predicate} }}}}" 
                predBind = predBind.format(predicate=pred)
            else:
                predBind = " . BIND({predicate} AS ?predicate)"
                predBind = predBind.format(predicate = pred)
            pred = "{prefix}{predicate}".format(prefix=b, predicate=pred)
        else:
            pred = "?predicate"
        if objType:
            objType = "?object a {object} . ".format(object=objType)

        # 2. Queries the server. If success create and return the list of results
        query = query.format(subject = sub, predicate = pred, objectType = objType, predBind = predBind)
        relationsList = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                val = (item['predicate']['value'],
                       item['object']['value'])
                relationsList.append(val)
        except:
            pass
        return relationsList

    # getTypeOfIndividual() queries the server
    # and returns the type of the given individual.
    def getTypeOfIndividual(self, individual):  
        individual = self.toQueryUri(individual)
        # 1. Starts with building up the query based on input parameters     
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "\
                "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "\
                "SELECT * {{ "\
                "{ind} rdf:type ?directType . "\
                "FILTER NOT EXISTS {{ "\
                "{ind} rdf:type ?type . "\
                "?type rdfs:subClassOf ?directType . "\
                "FILTER NOT EXISTS {{ ?type owl:equivalentClass ?directType }}}} . "\
                "FILTER (?directType != owl:NamedIndividual)}}"

        query = query.format(ind = individual)

        # 2. Queries the server, builds result and returns
        result = ""

        try:  
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            if results:
                result = results[0]['directType']['value']
            else:
                errorText = "The input individual {ind} does not exist in the ontology".format(ind=individual)
                raise BaseException(errorText)
        except:
            pass
        return result

    # getDataProperties queries the server for data properties of given individual
    # and returns a list of data-type properties of the individual
    def getDataProperties(self, individual):
        individual = self.toQueryUri(individual)
        # 1. Format query
        query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "SELECT * WHERE {{ "\
                "?predicate a owl:DatatypeProperty ."\
                "{subject} ?predicate ?object "\
                "}}"

        query = query.format(subject = individual)

        # 2. Query server, structure results and return list
        properties = []

        try:
            queryResult = self.query(query)
            results = queryResult['results']['bindings']
            for item in results:
                val = (item['predicate']['value'], 
                       item['object']['value'])
                properties.append(val)   
        except:
            pass
        return properties	

class ExplanationGenerator:
    def __init__(self, baseUri = ''):
        self.ir = InformationRetriever()
        if baseUri:
            self.baseUri = baseUri
        else:
            self.baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        self.indirectUri = 'http://www.semanticweb.org/ontologies/snowflake/indirect#'
            
    def getNameFromUri(self, uri):
        return (re.sub(".+#", '', uri))	

    #WHAT IS THE ROLE OF THIS FEATURE?
    def getFeatureRole(self, featureUri):
        es = EntityStructure()
        es.addEntity(featureUri)
        requirements = [r[1] for r in self.ir.getRelations(featureUri, self.baseUri + 'compriseOf', self.baseUri+ 'Requirement')]
        es.addAllEntities(requirements)

        for r in requirements:
            usecases = [uc[1] for uc in self.ir.getRelations(r, self.baseUri + 'partOf', self.baseUri + 'UseCase')]
            userstories = [us[1] for us in self.ir.getRelations(r, self.baseUri + 'explainedBy', self.baseUri + 'UserStory')]
            
            es.addAllEntities(usecases)
            es.addAllEntities(userstories)
            es.addOneToManyRelation(self.baseUri + 'partOf', r, usecases)
            es.addOneToManyRelation(self.baseUri + 'explainedBy', r, userstories)
        return es
    
    #WHAT IS THE RATIONALE BEHIND THE CHOICE OF THIS ARCHITECTURE?
    def getRationaleOfArchitecture(self, architecturalPatternUri):
        es = EntityStructure()
        es.addEntity(architecturalPatternUri)
        for dc in self.ir.getRelations(architecturalPatternUri, self.baseUri + 'resultOf', self.baseUri + 'DesignOption'):
            es.addEntity(dc[1])
            es.addRelation('resultOf', architecturalPatternUri, dc[1])
            for rationale in self.ir.getRelations(dc[1], self.baseUri + 'basedOn'):
                es.addEntity(rationale[1])
                es.addRelation('basedOn', dc[1], rationale[1])
            for causes_dc in self.ir.getRelations(dc[1], self.baseUri + 'causedBy', self.baseUri + 'DesignOption'):
                es.addEntity(causes_dc[1])
                es.addRelation('causedBy', dc[1], causes_dc[1])
                for rationale in self.ir.getRelations(causes_dc[1], self.baseUri + 'basedOn'):
                    es.addEntity(rationale[1])
                    es.addRelation('basedOn', causes_dc[1], rationale[1])
            for pattern in self.ir.getRelations(dc[1], self.baseUri + 'resultsIn', self.baseUri + 'ArchitecturalPattern'):
                es.addEntity(pattern[1])
                es.addRelation('resultOf', pattern[1], dc[1])
        return es
    

    def getDevelopmentStructureOfArchitecture(self, architecturalPatternUri):
        es = EntityStructure()
        es.addEntity(architecturalPatternUri)
        for role in self.ir.getRelations(architecturalPatternUri, self.baseUri + 'compriseOf', self.baseUri + 'Role'):
            es.addEntity(role[1])
            es.addRelation('compriseOf', architecturalPatternUri, role[1])
            for devStruct in self.ir.getRelations(role[1], self.baseUri + 'roleImplementedBy', self.baseUri + 'DevelopmentStructure'):
                es.addEntity(devStruct[1])
                es.addRelation('roleImplementedBy', role[1], devStruct[1])
        return es

    #WHAT IS THE BEHAVIOR OF THIS FEATURE?
    def getFunctionalBehaviorOfFeature(self, featureUri):
        es = EntityStructure()
        es.addEntity(featureUri)
        for req in self.ir.getRelations(featureUri, self.baseUri + 'compriseOf', self.baseUri + 'FunctionalRequirement'):
            es.addEntity(req[1])
            es.addRelation('compriseOf', featureUri, req[1])
            for uc in self.ir.getRelations(req[1], self.baseUri + 'partOf', self.baseUri + 'UseCase'):
                es.addEntity(uc[1])
                es.addRelation('partOf', req[1], uc[1])
        return es
    
    def getLogicalBehaviorOfFeature(self, featureUri):
        es = EntityStructure()
        es.addEntity(featureUri)
        for logStruct in self.ir.getRelations(featureUri, self.indirectUri + 'indirectProvidedBy', self.baseUri + 'LogicalStructure'):
            es.addEntity(logStruct[1])
            es.addRelation('indirectProvidedBy', featureUri, logStruct[1])
            for logBehavior in self.ir.getRelations(logStruct[1], self.baseUri + 'expressedBy', self.baseUri + 'LogicalBehavior'):
                es.addEntity(logBehavior[1])
                es.addRelation('expressedBy', logStruct[1], logBehavior[1])
                for behaviorDiagram in self.ir.getRelations(logBehavior[1], self.baseUri + 'modeledIn', self.baseUri + 'Diagram'):
                    es.addEntity(behaviorDiagram[1])
                    es.addRelation('modeledIn', logBehavior[1], behaviorDiagram[1])
        return es

    def getDevelopmentBehaviorOfFeature(self, featureUri):
        es = EntityStructure()
        es.addEntity(featureUri)
        for devStruct in self.ir.getRelations(featureUri, self.indirectUri + 'indirectProvidedBy', self.baseUri + 'DevelopmentStructure'):
            es.addEntity(devStruct[1])
            es.addRelation('indirectProvidedBy', featureUri, devStruct[1])
            for devBehavior in self.ir.getRelations(devStruct[1], self.baseUri + 'expressedBy', self.baseUri + 'DevelopmentBehavior'):
                es.addEntity(devBehavior[1])
                es.addRelation('expressedBy', devStruct[1], devBehavior[1])
                for behaviorDiagram in self.ir.getRelations(devBehavior[1], self.baseUri + 'modeledIn', self.baseUri + 'Diagram'):
                    es.addEntity(behaviorDiagram[1])
                    es.addRelation('modeledIn', devBehavior[1], behaviorDiagram[1])
        return es

    #SameAs not working correctly, thing about how to solve this.
    def getUIBehaviorOfFeature(self, featureUri):
        es = EntityStructure()
        es.addEntity(featureUri)
        for UIStruct in self.ir.getRelations(featureUri, self.indirectUri + 'indirectProvidedBy', self.baseUri + 'UIStructure'):
            es.addEntity(UIStruct[1])
            es.addRelation('indirectProvidedBy', featureUri, UIStruct[1])
            for UIBehavior in self.ir.getRelations(UIStruct[1], self.baseUri + 'expressedBy', self.baseUri + 'UIBehavior'):
                es.addEntity(UIBehavior[1])
                es.addRelation('expressedBy', UIStruct[1], UIBehavior[1])
                for behaviorDiagram in self.ir.getRelations(UIBehavior[1], self.baseUri + 'modeledIn', self.baseUri + 'Diagram'):
                    es.addEntity(behaviorDiagram[1])
                    es.addRelation('modeledIn', UIBehavior[1], behaviorDiagram[1])
        return es

    #HOW IS THIS FEATURE MAPPED TO THE IMPLEMENTATION?

    def getLogicalFeatureToImplementationMap(self, featureUri):
        #Callbacks: 
        def callbackImplementedBy(es, s): 
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'implementedBy')
        def callbackCompriseOf(es, s): 
            self.addRecursiveEntitiesAndRelations(es,s, self.baseUri + 'compriseOf', callback=callbackImplementedBy)
            callbackImplementedBy(es, s)

        es = EntityStructure()
        es.addEntity(featureUri)
        for req in self.ir.getRelations(featureUri, self.baseUri + 'compriseOf', self.baseUri + 'Requirement'):
            es.addEntity(req[1])
            es.addRelation('compriseOf', featureUri, req[1])
            for logStruct in self.ir.getRelations(req[1], self.baseUri + 'satisfiedBy', self.baseUri + 'LogicalStructure'):
                es.addEntity(logStruct[1])
                es.addRelation('satisfiedBy', req[1], logStruct[1])
                self.addRecursiveEntitiesAndRelations(es, logStruct[1], self.baseUri + 'designedBy', callback=callbackCompriseOf)
        
        return es
    
    def getFunctionalFeatureToImplementationMap(self, featureUri):
        logical = self.getLogicalFeatureToImplementationMap(featureUri)

        es = EntityStructure()

        architectureFragmentUris = []
        requirementUris = []
        for entity in logical.entities:
            if self.baseUri + 'ArchitectureFragment' in entity.supertypes:
                architectureFragmentUris.append(entity.uri)
            elif self.baseUri + 'Requirement' in entity.supertypes:
                requirementUris.append(entity.uri)
            else:
                es.addEntity(entity)
        
        architectureEntity = DummyEntity('dummy_architecture_uri', 'ArchitectureLayer', entityType='ArchitectureLayer', supertypes=['ArchitecturePattern'])
        es.addEntity(architectureEntity)

        for relation in logical.relations:
            if relation.source not in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation)
            elif relation.source not in architectureFragmentUris and relation.target in architectureFragmentUris:
                es.addRelation(relation.name, relation.source, architectureEntity.uri)
            elif relation.source in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation.name, architectureEntity.uri, relation.target)

        requirementEntity = DummyEntity('dummy_requirement_uri', 'Requirements', entityType='Requirement', supertypes=['Requirement'])
        es.addEntity(requirementEntity)

        for relation in logical.relations:
            if relation.source not in requirementUris and relation.target not in requirementUris:
                es.addRelation(relation)
            elif relation.source not in requirementUris and relation.target in requirementUris:
                es.addRelation(relation.name, relation.source, requirementEntity.uri)
            elif relation.source in requirementUris and relation.target not in requirementUris:
                es.addRelation(relation.name, requirementEntity.uri, relation.target)
        
        for relation in logical.relations:
            if relation.source in architectureFragmentUris and relation.target in requirementUris:
                es.addRelation(relation.name, architectureEntity.uri, requirementEntity.uri)
            if relation.source in requirementUris and relation.target in architectureFragmentUris:
                es.addRelation(relation.name, requirementEntity.uri, architectureEntity.uri)

        return es

    def getImplementationToArchitecturalPatternMap(self, implementationUriList):
        def callBackArchitecturalPattern(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'partOf', self.baseUri + 'ArchitecturalPattern')

        def callbackPlaysRole(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'playsRole', self.baseUri + 'Role', callback=callBackArchitecturalPattern)
        
        es = EntityStructure()
        for i in implementationUriList:
            es.addEntity(i)
            for devStruct in self.ir.getRelations(i, self.baseUri + 'implements', self.baseUri + 'DevelopmentStructure'):
                es.addEntity(devStruct[1])
                es.addRelation('implements' , i, devStruct[1])
                self.addRecursiveEntitiesAndRelations(es, devStruct[1], self.baseUri + 'partOf', callback=callbackPlaysRole)
                self.addRecursiveEntitiesAndRelations(es, devStruct[1], self.baseUri + 'playsRole', self.baseUri + 'Role', callback=callBackArchitecturalPattern)
        return es

    #RecursiveAdd
    def addRecursiveEntitiesAndRelations(self, entityStructure, subjectUri, predicateUri, objectTypeUri='', callback=None):
        for o in self.ir.getRelations(subjectUri, predicateUri, objectTypeUri):
            entityStructure.addEntity(o[1])
            entityStructure.addRelation(self.getNameFromUri(predicateUri), subjectUri, o[1])
            self.addRecursiveEntitiesAndRelations(entityStructure, o[1], predicateUri, objectTypeUri, callback)
            if callback:
                callback(entityStructure, o[1])
        return entityStructure



    
class Section:
    def __init__(self, sectionId, sectionTitle, entityType='', sectionTextContent=None, sectionSummary='', priority=0, sectionDiagrams=None, children=None):
        self.sectionId = sectionId
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


class ExplanationTemplates:

    def __init__(self):
        self.baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        self.informationRetriever = InformationRetriever()
        self.pluralEngine = inflect.engine()

    # HELPERS
    def getNameFromUri(self, uri):
        return (re.sub(".+#", '', uri))	

    def entitiesToListString(self, entities):
        entityListString = ''
        for index, e in enumerate(entities):
            if index < len(entities) - 1:
                entityListString +=  self.getNameOfEntity(e) + '\n'
            else:
                entityListString += self.getNameOfEntity(e)
        return entityListString
    
    def getNameOfEntity(self, entity):
        if entity.label:
            return entity.label
        else: 
            return self.getNameFromUri(entity.uri)

    def diagramUriToFileName(self, diagramName):
        match = re.search('\\wigure_\\d\.\\d+', diagramName)
        finalString = re.sub('\.', '_', str(match.group(0)))
        return finalString

    def formatName(self, relationName):
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
    
    def formatDiagramName(self, diagramName):
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
    
    def formatListOfEntities(self, elist):
        elist = [e for e in elist if e]
        end = len(elist) - 1
        entityString = ''
        for index, item in enumerate(elist):
            if(item):
                entityString += str(len(item)) + ' ' + self.formatName(self.getNameFromUri(item[0].type))
                if len(item) > 1:
                    entityString += 's'
                if index < end and index + 1 == end:
                    entityString += ' and '
                elif index < end:
                    entityString += ', '
        return entityString
            

    def openText(self, url):
        template = ''
        with open(url, 'r') as myfile:
            template = myfile.read().replace('\n', '')
            template = template.replace('\\n', '\n')
        return template

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
            entity = Entity(entityUri)
            entityType = self.getNameFromUri(entity.type)
            
            if entityType not in list(entityTypes.keys()):
                entityTypes[entityType] = []
            
            entityTypes[entityType].append(entity)

        text = ''
        for index, entityType in enumerate(entityTypes):
            size = str(len(entityTypes[entityType]))
            text += size + ' ' + self.pluralEngine.plural(self.formatName(entityType), size)
            if index < len(entityTypes) - 2:
                text += ', '
            elif index == len(entityTypes) - 2:
                text += 'and'

        return text

    def createSection(self, entityList, id, title, summary='', priority=1):
        section = Section(id, title, sectionSummary=summary, priority=priority)

        for entity in entityList:
            diagrams = []
            for diagram in entity.diagrams:
                caption = self.informationRetriever.getRelations(diagram, self.baseUri + 'Caption')
                if caption:
                    caption = caption[0][1]

                diagrams.append({'uri': diagram, 'caption': caption})

            entitySection = Section(self.getNameFromUri(entity.uri), 
                                    self.getNameOfEntity(entity),
                                    entityType=self.getNameFromUri(entity.type),
                                    sectionSummary='This section shortly describes the ' + self.formatName(self.getNameFromUri(entity.type)) + ' ' + self.getNameOfEntity(entity) + '.', 
                                    sectionTextContent=[(self.getNameFromUri(content[0]), content[1]) for content in entity.dataTypeProperties], 
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

                overviewDiagrams[diagram] = {'name': self.formatDiagramName(self.getNameFromUri(diagram)), 'description' : overviewDiagramDescription, 'caption': overviewDiagramCaption}
        return overviewDiagrams

    # EXPLANATIONS
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

        template = self.openText('static/explanationTemplates/LogicalViewImplementation.txt')
        summary = template.format(main_entity=self.getNameOfEntity(main_entity), 
                                    rel_feat_req=rel_feat_req, rel_logic_dev=rel_logic_dev,
                                    rel_req_logic=rel_req_logic, rel_dev_impl=rel_dev_impl,
                                    nbr_req=len(requirements), nbr_logic=len(logical))

        question = self.getQuestion(summary)
        expTemplate = Template(question, summary)
        
        #Logical section
        sectionLogicalOverview = 'This section describes each entity of the Logical view '\
                                 'that are related to the feature Purchase products.'
        
        logicalSection = self.createSection(logical, 'logical_section', 'Logical entities',
                               summary=sectionLogicalOverview, priority=3)

        overviewDiagrams = self.getOverviewDiagrams(structure, 'LogicalStructure')
        
        overviewIdCounter = 0
        for key, value in overviewDiagrams.items():
            dummySection = Section('overview' + str(overviewIdCounter), value['name'], sectionSummary=value['description'], sectionDiagrams=[{'uri': key, 'caption': value['caption']}])
            overviewIdCounter += 1
        overviewSectionSummary = 'This section presents and describes diagrams that encapsulate all of the logical entities found in this explanation.'
        overviewSection = Section('logical_overview', 'Overview', sectionSummary=overviewSectionSummary, priority=99)
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

        template = self.openText('static/explanationTemplates/FunctionalViewImplementation.txt')
        summary = template.format(main_entity=self.getNameOfEntity(mainEntity), nbr_requirements=len(req), nbr_implementation=len(impl))
        question = self.getQuestion(summary)

        sectionImplOverview = 'This section shows all implementation classes related to {main_entity}.'
        sectionImplOverview = sectionImplOverview.format(main_entity=self.getNameOfEntity(mainEntity))
        implSection = self.createSection(impl, 'impl_section', 'Implementation classes',
                               summary=sectionImplOverview, priority=3)

        expTemplate = Template(question, summary)
        expTemplate.addSection(implSection.toDict())

        return expTemplate
        
    def generatePatternFeatureImplementationSummary(self, mainEntityUri, structure):
        
        mainEntity = Entity(mainEntityUri)
        impl = list(filter(lambda e: e.type == self.baseUri + 'ImplementationClass', structure.entities))
        role = list(filter(lambda e: e.type == self.baseUri + 'Role', structure.entities))
        arch = list(filter(lambda e: e.type == self.baseUri + 'ArchitecturalPattern', structure.entities))
        dev = list(filter(lambda e: self.baseUri + 'DevelopmentStructure' in e.supertypes, structure.entities))

        template = self.openText('static/explanationTemplates/PatternViewImplementation.txt')
        summary = template.format(main_entity=self.getNameOfEntity(mainEntity), nbr_impl=len(impl), nbr_dev=len(dev),
                                  nbr_role=len(role), nbr_arch_patt=len(arch))
        question = self.getQuestion(summary)

        sectionImplOverview = 'This section shows all implementation classes related to {main_entity}.'
        sectionImplOverview = sectionImplOverview.format(main_entity=self.getNameOfEntity(mainEntity))
        
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

        expTemplate = Template(question, summary)
        expTemplate.addSection(implSection.toDict())
        expTemplate.addSection(roleSection.toDict())
        expTemplate.addSection(archSection.toDict())
        expTemplate.addSection(devSection.toDict())

        return expTemplate

    def generatePopupFigureDescription(self, figureUri):
        figureEntity = Entity(figureUri)
        
        template = self.openText('static/explanationTemplates/FigureSummary.txt')
        
        relatedEntityUris = [entity[1] for entity in self.informationRetriever.getRelations(figureUri, self.baseUri + 'models')]
        summary = template.format(classes=self.classesToText(relatedEntityUris))
        question = {'sub': 'View diagrams','orginial': ''}


        figureid = 'popup_' + self.diagramUriToFileName(self.getNameFromUri(figureUri)) 
        figuretitle = self.getNameOfEntity(figureEntity)
        figureSummary = ''

        entityid = 'popup_entity_overview_' + self.diagramUriToFileName(self.getNameFromUri(figureUri)) 
        entitySummary = 'This section shows short descriptions of each entity illustrated the diagram.'

        relatedEntities = [Entity(e) for e in relatedEntityUris]
        figureSection = Section(figureid, figuretitle, figureSummary, priority=5,
                        sectionTextContent=[(self.getNameFromUri(content[0]), content[1]) for content in figureEntity.dataTypeProperties])
        entitySection = self.createSection(relatedEntities, entityid, 'Entities related to diagram', entitySummary)

        template = Template(question, summary)
        template.addSection(figureSection.toDict())
        template.addSection(entitySection.toDict())

        return template

def testing():
    ir = InformationRetriever()
    eg = ExplanationGenerator()
    et = ExplanationTemplates()
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    # implementation = ir.getIndividualsByType(baseUri + 'ImplementationClass')
    # es = eg.getLogicalFeatureToImplementationMap(baseUri + 'purchase_products')
    # es = eg.getFunctionalFeatureToImplementationMap(baseUri + 'purchase_products')
    # exp = et.generateLogicalFeatureImplementationSummary(baseUri + 'purchase_products', es)
    # es = eg.getImplementationToArchitecturalPatternMap(implementation)
    #es = eg.getRationaleOfArchitecture(baseUri + 'thin_client_MVC')
    # print(exp)
    #s = ir.getSuperTypes(baseUri + 'Server_Model_CartForms')
    #print(s)
    #es = None
    #print(es)
    #print(et.generatePatternSummary2(baseUri + 'choice_mixed_client_MVC', es))
    # return es
    su = et.generatePopupFigureDescription(baseUri + 'figure_3.10_class_diagram_of_the_system')
    # test = [baseUri + 'Cart', baseUri + 'Order']
    # pred = [r[1] for r in ir.getRelations(sub = baseUri + 'figure_3.10_class_diagram_of_the_system')]
    # print(set(test)<set(pred))
    print(su.toDict())
    return su.summaryText

def writeToFile(inputData):
    f = open('../ExperimentationGraphs/static/explanationData.js', 'w') 
    f.truncate(0)
    f.write("ontologyData = " + json.dumps(inputData))
    f.close()

# data = testing()
# writeToFile(data.toDict())