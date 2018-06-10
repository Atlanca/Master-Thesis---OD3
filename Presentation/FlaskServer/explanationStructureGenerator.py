import sparqlQueryManager
import ontologyStructureModel
import re
import explanationHelper
import json
import copy


class ExplanationGenerator:
    def __init__(self, baseUri = ''):
        self.ir = sparqlQueryManager.InformationRetriever()
        if baseUri:
            self.baseUri = baseUri
        else:
            self.baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        self.indirectUri = 'http://www.semanticweb.org/ontologies/snowflake/indirect#'

    #WHAT IS THE ROLE OF THIS FEATURE?
    def getFeatureRole(self, featureUri):
        es = ontologyStructureModel.EntityStructure()
        es.addEntity(featureUri)
        requirements = [r[1] for r in self.ir.getRelations(featureUri, self.baseUri + 'compriseOf', self.baseUri+ 'Requirement')]
        es.addAllEntities(requirements)
        es.addOneToManyRelation('compriseOf', featureUri, requirements)

        for r in requirements:
            usecases = [uc[1] for uc in self.ir.getRelations(r, self.baseUri + 'partOf', self.baseUri + 'UseCase')]
            userstories = [us[1] for us in self.ir.getRelations(r, self.baseUri + 'explainedBy', self.baseUri + 'UserStory')]
            
            es.addAllEntities(usecases)
            es.addAllEntities(userstories)
            es.addOneToManyRelation('partOf', r, usecases)
            es.addOneToManyRelation('explainedBy', r, userstories)
        return es

    #WHAT IS THE RATIONALE BEHIND THE CHOICE OF THIS ARCHITECTURE?
    def getRationaleOfArchitecture(self, architecturalPatternUri):
        es = ontologyStructureModel.EntityStructure()
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
    

    def getDev(self, architecturalPatternUri):
        def callBackArchitecturalPattern(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'implementedBy', self.baseUri + 'ImplementationClass')

        def callbackDevStructure(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'compriseOf', self.baseUri + 'DevelopmentStructure', callback=callBackArchitecturalPattern)
        
        es = ontologyStructureModel.EntityStructure()
        es.addEntity(architecturalPatternUri)
        for role in self.ir.getRelations(architecturalPatternUri, self.baseUri + 'compriseOf', self.baseUri + 'Role'):
            es.addEntity(role[1])
            es.addRelation('compriseOf' , architecturalPatternUri, role[1])
            self.addRecursiveEntitiesAndRelations(es, role[1], self.baseUri + 'roleImplementedBy', callback=callbackDevStructure)
        return es
    
    def getPatternArchitecture(self):
        def callbackArchitectureFragment(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'compriseOf', self.baseUri + 'ArchitectureFragment', callback=callbackRole)
            # self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'partOf', self.baseUri + 'ArchitectureFragment', callback=callbackRole)        

        def callbackRole(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'roleImplementedBy', self.baseUri + 'ArchitectureFragment', callback=callbackArchitectureFragment)

        patterns = self.ir.getIndividualsByType(self.baseUri + 'ArchitecturalPattern')
        es = ontologyStructureModel.EntityStructure()
        
        for pattern in patterns:
            es.addEntity(pattern)
            self.addRecursiveEntitiesAndRelations(es, pattern, self.baseUri + 'compriseOf', self.baseUri + 'Role', callback=callbackRole)

        return es

    def getFunctionalView(self):
        def callbackUseCase(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'partOf', self.baseUri + 'UseCase')
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'explainedBy', self.baseUri + 'UserStory')
            # self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'performedBy', self.baseUri + 'Stakeholder')

        features = self.ir.getIndividualsByType(self.baseUri + 'Feature')
        es = ontologyStructureModel.EntityStructure()

        for feature in features:
            es.addEntity(feature)
            self.addRecursiveEntitiesAndRelations(es, feature, self.baseUri + 'compriseOf', self.baseUri + 'Requirement', callback=callbackUseCase)
        
        return es

    def getDesignOptions(self):
        def callbackArgConAss(es, s):
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'basedOn', self.baseUri + 'Argument')
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'basedOn', self.baseUri + 'Constraint')
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'basedOn', self.baseUri + 'Assumption')

        designOptions = self.ir.getIndividualsByType(self.baseUri + 'DesignOption')
        es = ontologyStructureModel.EntityStructure()

        for designOption in designOptions:
            es.addEntity(designOption)
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'dependsOn', self.baseUri + 'Requirement', callback=callbackArgConAss)
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'resultsIn', self.baseUri + 'ArchitectureFragment', callback=callbackArgConAss)
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'resultsIn', self.baseUri + 'ArchitecturalPattern', callback=callbackArgConAss)
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'resultsIn', self.baseUri + 'Technology', callback=callbackArgConAss)
            self.addRecursiveEntitiesAndRelations(es, designOption, self.baseUri + 'causes', self.baseUri + 'DesignOption', callback=callbackArgConAss)
        return es

    def getLogBehaviorOfFeature(self, featureUri, behaviorUri, structureUri):
        def callbackDiagram(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'modeledIn', self.baseUri + 'Diagram')

        def callbackBehavior(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, 'owl:sameAs', behaviorUri, callbackDiagram)
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'expressedBy', behaviorUri, callbackDiagram)
 
        def callbackStructure(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'satisfiedBy', structureUri, callback=callbackBehavior)

        es = ontologyStructureModel.EntityStructure()
        es.addEntity(featureUri)
        self.addRecursiveEntitiesAndRelations(es, featureUri, self.baseUri + 'compriseOf', self.baseUri + 'Requirement', callback=callbackStructure)

        return es

    def getFunctionalityOfSystem(self):
        def callbackRequirement(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'partOf', self.baseUri + 'UseCase')
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'explainedBy', self.baseUri + 'UserStory')

        es = ontologyStructureModel.EntityStructure()
        requirements = self.ir.getIndividualsByType(self.baseUri + 'Feature')

        for req in requirements:
            es.addEntity(req)
            self.addRecursiveEntitiesAndRelations(es, req, self.baseUri + 'compriseOf', self.baseUri + 'Requirement', callback=callbackRequirement)
        return es

    def getBehaviorOfFeature(self, featureUri, behaviorUri, structureUri):
        def callbackDiagram(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'modeledIn', self.baseUri + 'Diagram')

        def callbackBehavior(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, 'owl:sameAs', behaviorUri, callbackDiagram)
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'expressedBy', behaviorUri, callbackDiagram)
    
        def callbackStructure(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'designedBy', structureUri, callback=callbackBehavior)

        def callbackLogicalStructure(es, s):
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'satisfiedBy', self.baseUri + 'Logical', callback=callbackStructure)
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'satisfiedBy', structureUri, callback=callbackBehavior)

        es = ontologyStructureModel.EntityStructure()
        es.addEntity(featureUri)
        self.addRecursiveEntitiesAndRelations(es, featureUri, self.baseUri + 'compriseOf', self.baseUri + 'Requirement', callback=callbackLogicalStructure)
        self.addRecursiveEntitiesAndRelations(es, featureUri, self.baseUri + 'realizedBy', structureUri, callback=callbackStructure)

        return es


    def getLogicalBehaviorOfFeature(self, featureUri):
        return self.getLogBehaviorOfFeature(featureUri, self.baseUri + 'LogicalBehavior', self.baseUri + 'LogicalStructure')

    def getDevelopmentBehaviorOfFeature(self, featureUri):
        return self.getBehaviorOfFeature(featureUri, self.baseUri + 'DevelopmentBehavior', self.baseUri + 'DevelopmentStructure')
   
    def getUIBehaviorOfFeature(self, featureUri):
        return self.getBehaviorOfFeature(featureUri, self.baseUri + 'UIBehavior', self.baseUri + 'UIStructure')

    #HOW IS THIS FEATURE MAPPED TO THE IMPLEMENTATION?
    def getLogicalFeatureToImplementationMap(self, featureUri):
        #Callbacks: 
        def callbackImplementedBy(es, s): 
            self.addRecursiveEntitiesAndRelations(es, s, self.baseUri + 'implementedBy')
        def callbackCompriseOf(es, s): 
            self.addRecursiveEntitiesAndRelations(es,s, self.baseUri + 'compriseOf', callback=callbackImplementedBy)
            callbackImplementedBy(es, s)

        es = ontologyStructureModel.EntityStructure()
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

        es = ontologyStructureModel.EntityStructure()

        architectureFragmentUris = []
        requirementUris = []
        for entity in logical.entities:
            if self.baseUri + 'ArchitectureFragment' in entity.supertypes:
                architectureFragmentUris.append(entity.uri)
            elif self.baseUri + 'Requirement' in entity.supertypes:
                requirementUris.append(entity.uri)
            else:
                es.addEntity(entity)
        
        architectureEntity = ontologyStructureModel.DummyEntity('architecture_uri', 'ArchitectureLayer', supertypes=['ArchitectureFragment'])
        es.addEntity(architectureEntity)

        for relation in logical.relations:
            if relation.source not in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation)
            elif relation.source not in architectureFragmentUris and relation.target in architectureFragmentUris:
                es.addRelation(relation.name, relation.source, architectureEntity.uri)
            elif relation.source in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation.name, architectureEntity.uri, relation.target)

        requirementEntity = ontologyStructureModel.DummyEntity('requirement_uri', 'Requirements', supertypes=['Requirement'])
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
        
        es = ontologyStructureModel.EntityStructure()
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
            entityStructure.addRelation(explanationHelper.getNameFromUri(predicateUri), subjectUri, o[1])
            self.addRecursiveEntitiesAndRelations(entityStructure, o[1], predicateUri, objectTypeUri, callback)
            if callback:
                callback(entityStructure, o[1])
        return entityStructure

    # A depth-first algorithm that returns a list of all paths
    # from a start type to a target type.
    # If no paths are found, return an empty list
    def getMetaModelPath(self, metaModel, startType, targetType):
        # A list that keeps track of all types we have encountered so far
        encounteredTypes = []

        # A list that keeps track fo all paths we found to the target
        paths = []

        # Find all relations from startType
        relations = list(filter(lambda rel: rel['source'] == startType, metaModel['relations']))
        relations = metaModel['relations']
        # For each relation from startType, find path to target
        for rel in relations:
            paths += self.getMetaModelPathRecursive(metaModel, rel, targetType, encounteredTypes, [])

        # paths = [path for path in paths if not self.pathHasType(startType, path)]

        # for ontologyType in metaModel['types']:
        #     paths = self.filterShortestPath(startType, paths, ontologyType)

        return [metaModel['relations']]

    def filterShortestPath(self, paths, ontologyType):
        intersectingPaths = list(filter(lambda path: self.pathHasType(ontologyType, path), paths))
        otherPaths = [path for path in paths if path not in intersectingPaths]
        shortestPath = []
        shortestLen = 0
        
        for path in intersectingPaths:
            if shortestLen == 0:
                shortestLen = len(path)
                shortestPath.append(path)

            if len(path) < shortestLen:
                shortestPath = []
                shortestPath.append(path)
                shortestLen = len(path)
            elif len(path) == shortestLen:
                shortestPath.append(path)
        
        otherPaths += shortestPath
        return otherPaths
    
    def pathHasType(self, ontologyType, path):
        for index, relation in enumerate(path):
            if index > 0:
                if relation['source'] == ontologyType:
                    return True
        return False

    # This method is a recursive helper for getMetaModelPath()
    def getMetaModelPathRecursive(self, metaModel, currentRelation, targetType, encounteredTypes, currentPath):
        paths = []
        currentPath.append(currentRelation)
        # If the start type is same as the target, then we found a path. 
        if currentRelation['target'] == targetType:
            paths.append(currentPath)
            return paths

        encounteredTypes.append(currentRelation['target'])
        # Find outgoing relations from the startType
        # Of these relations, only pick the relations with targets 
        # we have not encountered yet.
        relations = list(filter(lambda rel: rel['source'] == currentRelation['target'], metaModel['relations']))
        relations = list(filter(lambda rel: rel['target'] not in encounteredTypes , relations))

        # Loop through all relations and recursively
        # try to find paths to target, once done return the paths
        for rel in relations:
            paths += (self.getMetaModelPathRecursive(metaModel, rel, targetType, encounteredTypes, copy.deepcopy(currentPath)))
              
        return paths        

    def getEntityPaths(self, startEntityUri, pathRelations):
        startType = self.ir.getTypeOfIndividual(startEntityUri)
        typeRelations = list(filter(lambda rel: rel['source'] == startType, pathRelations))
        difference = [rel for rel in pathRelations if rel not in typeRelations]
        print(difference)
        finalRelationsList = []
        for typeRelation in typeRelations:
            entityRel = self.ir.getRelations(startEntityUri, pred=typeRelation['property'], objType=typeRelation['target'])
            for er in entityRel:
                finalRelationsList.append({'source': startEntityUri, 'property': er[0], 'target': er[1]})
                finalRelationsList += self.getEntityPaths(er[1], difference)
        return finalRelationsList


    def loadMetaModel(self):
        metaModel = None
        with open('C:/Users/SAMSUNG/Documents/ThesisProject/MasterThesisCode/Master-Thesis---OD3/Presentation/FlaskServer/static/ontologyRelations.js', 'r') as f:
            metaModel = json.load(f)
        return metaModel

    def constructMetaModel(self):
        allObjectsAndRelations = self.ir.getAllObjectsAndRelations()
        es = ontologyStructureModel.EntityStructure()
        entityToUriMap = {}
        for item in allObjectsAndRelations:
            e1 = ontologyStructureModel.Entity(item[0])
            e2 = ontologyStructureModel.Entity(item[2])
            es.addEntity(e1)
            es.addEntity(e2)
            entityToUriMap[explanationHelper.getNameFromUri(item[0])] = e1
            entityToUriMap[explanationHelper.getNameFromUri(item[2])] = e2
            es.addRelation(item[1], item[0], item[2])
            
        duplicates = {}
        for item in es.entities:
            if not explanationHelper.getNameFromUri(item.uri) in list(duplicates.keys()):
                duplicates[explanationHelper.getNameFromUri(item.uri)] = 1
            else:
                print('We got a duplicate key!')
                break

        print(duplicates)

        types = set()
        for item in es.entities:
            types.add(item.type)
        
        types = list(types)
        print('Types:')
        print(types)

        def getEntityType(entityUri):
            return entityToUriMap[explanationHelper.getNameFromUri(entityUri)].type

        typeRelations = []
        for item in es.relations:
            typeRelations.append({'name': item.name, 'source': getEntityType(item.source), 'target': getEntityType(item.target)})
        
        typeRelations = [dict(s) for s in set(frozenset(d.items()) for d in typeRelations)]

        print('Type relations:')
        print(typeRelations)

        typesAndRelations = {'types': types, 'relations': typeRelations}

        with open('C:/Users/SAMSUNG/Documents/ThesisProject/MasterThesisCode/Master-Thesis---OD3/Presentation/FlaskServer/static/ontologyRelations.js', 'w') as f:
            f.write(json.dumps(typesAndRelations))
    