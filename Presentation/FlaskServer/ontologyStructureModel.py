import sparqlQueryManager
import explanationHelper
import re

# A class for ontology entities
class Entity:
    def __init__(self, entityUri, baseURI = ''):
        if baseURI:
            baseUri = baseURI
        else:
            baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        ir = sparqlQueryManager.InformationRetriever()

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
        self.ir = sparqlQueryManager.InformationRetriever()
        self.entities = []
        self.relations = []
        self.structure = {}
        self.structure['relations'] = self.relations
        self.structure['entities'] = self.entities

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
                entitiesStr += explanationHelper.getNameFromUri(entity.uri) + ', '
            else:
                entitiesStr += explanationHelper.getNameFromUri(entity.uri)

        for index, relation in enumerate(self.relations):
            if index < relationsEnd:
                relationsStr += '(' + explanationHelper.getNameFromUri(relation.name) + ', ' 
                + explanationHelper.getNameFromUri(relation.source) + ', ' 
                + explanationHelper.getNameFromUri(relation.target) + ')' + ', '
            else:
                relationsStr += '(' + explanationHelper.getNameFromUri(relation.name) + ', ' 
                + explanationHelper.getNameFromUri(relation.source) + ', '
                + explanationHelper.getNameFromUri(relation.target) + ')'

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