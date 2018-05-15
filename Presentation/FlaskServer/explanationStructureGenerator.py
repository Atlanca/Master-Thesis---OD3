import sparqlQueryManager
import ontologyStructureModel
import re
import explanationHelper


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
    

    def getDevelopmentStructureOfArchitecture(self, architecturalPatternUri):
        es = ontologyStructureModel.EntityStructure()
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
        es = ontologyStructureModel.EntityStructure()
        es.addEntity(featureUri)
        for req in self.ir.getRelations(featureUri, self.baseUri + 'compriseOf', self.baseUri + 'FunctionalRequirement'):
            es.addEntity(req[1])
            es.addRelation('compriseOf', featureUri, req[1])
            for uc in self.ir.getRelations(req[1], self.baseUri + 'partOf', self.baseUri + 'UseCase'):
                es.addEntity(uc[1])
                es.addRelation('partOf', req[1], uc[1])
        return es
    
    def getLogicalBehaviorOfFeature(self, featureUri):
        es = ontologyStructureModel.EntityStructure()
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
        es = ontologyStructureModel.EntityStructure()
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
        es = ontologyStructureModel.EntityStructure()
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
        
        architectureEntity = ontologyStructureModel.DummyEntity('dummy_architecture_uri', 'ArchitectureLayer', entityType='ArchitectureLayer', supertypes=['ArchitecturePattern'])
        es.addEntity(architectureEntity)

        for relation in logical.relations:
            if relation.source not in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation)
            elif relation.source not in architectureFragmentUris and relation.target in architectureFragmentUris:
                es.addRelation(relation.name, relation.source, architectureEntity.uri)
            elif relation.source in architectureFragmentUris and relation.target not in architectureFragmentUris:
                es.addRelation(relation.name, architectureEntity.uri, relation.target)

        requirementEntity = ontologyStructureModel.DummyEntity('dummy_requirement_uri', 'Requirements', entityType='Requirement', supertypes=['Requirement'])
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