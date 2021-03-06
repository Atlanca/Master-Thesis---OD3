import requests
import json
import re
import pprint

# TODO: Rationale does not take alternatives into account.
# TODO: Some repeated code. Refactor
# TODO: Comment the last three methods
# TODO: Test with working reasoner
# TODO: Find out how to explain how the technology is used in the system
# TODO: Perhaps find a way to explain the system based on the relations of the objects

class SparqlQueryManager:
    def __init__(self, url):
        self.url = url

    def query(self, query):
        return requests.post(self.url, data = {'query': query})

#Structure class
class entityStructure:
    def __init__(self):
        self.ir = InformationRetriever()
        self.entities = []
        self.relations = []
        self.flatStructure = {}
    
    def addEntity(self, entityUri):
        
        diagrams = []
        rationale = []

        for diagram in self.ir.getRelations(entityUri, 'modeledIn', 'Diagram'):
            diagrams.append(diagram[1])

        for r in self.ir.getRelations(entityUri, 'basedOn'):
            rationale.append(r[1])

        self.entities.append({'type': self.ir.getTypeOfIndividual(entityUri), 
                              'uri': entityUri,
                              'name': self.ir.getNameOfURI(entityUri),
                              'dataTypeProperties': self.ir.getDataProperties(entityUri),
                              'diagrams': diagrams,
                              'rationale': rationale})

    def addRelation(self, relationName, source, target):
        self.relations.append({'name': relationName, 
                               'source:': source, 
                               'target':target})

    def hasEntity(self, entityUri):
        pass


    def getStructure(self):
        self.flatStructure['entities'] = self.entities
        self.flatStructure['relations'] = self.relations
        return self.flatStructure
    
class InformationRetriever:
    def __init__(self, url=None):
        self.queryManager = SparqlQueryManager('http://localhost:3030/Thesis/query')
    def getNameOfURI(self, uri):
        return (re.sub(".+#", '', uri))	


    #-----------------------------------------------------------------------------------------
    # 1. BASIC QUERY HELPER METHODS
    #-----------------------------------------------------------------------------------------

    def getAllInverses(self):
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
        "SELECT DISTINCT ?pred1 ?pred2 WHERE {{?pred a owl:ObjectProperty . ?pred1 owl:inverseOf ?pred2}}"
        queryResult = self.queryManager.query(query)
        predicatePairs = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                predicatePairs.append((self.getNameOfURI(item['pred1']['value']), 
                                self.getNameOfURI(item['pred2']['value']),
                                ))
        return predicatePairs

    def getAllObjectsAndRelations(self):
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
        "SELECT ?sub ?pred ?obj WHERE {{?pred a owl:ObjectProperty . ?sub ?pred ?obj}}"
        queryResult = self.queryManager.query(query)
        individuals = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                if("http://www.w3.org/2002/07/owl#" not in item['pred']['value']):
                    individuals.append((self.getNameOfURI(item['sub']['value']), 
                                    self.getNameOfURI(item['pred']['value']),
                                    self.getNameOfURI(item['obj']['value'])
                                    ))
        return individuals
    
    def getAllObjects(self):
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
        "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
        "SELECT DISTINCT ?sub WHERE {{?sub a owl:Thing . ?sub ?pred ?obj}}"
        queryResult = self.queryManager.query(query)
        individuals = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                individuals.append(self.getNameOfURI(item['sub']['value']))
        return individuals

    def getIndividualsByType(self, inputType):
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "PREFIX owl: <http://www.w3.org/2002/07/owl#> "\
                "SELECT * WHERE {{?individual a base:{t} }}"
        query = query.format(t=inputType)
        queryResult = self.queryManager.query(query)
        individuals = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                individuals.append(self.getNameOfURI(item['individual']['value']))
        return individuals
                
    # getRelations() returns all predicates from the given subject to an object in a list.
    # useInversePred determines whether to use the given predicate or to use the inverse of it.
    # always returns a tuple in the following format: (predicate, object)
    def getRelations(self, sub, pred="", objType="", useInversePred=False):
        originalPred = pred
        originalObjType = objType
        # 1. Starts with building up the query depending on input parameters
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
               "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
               "SELECT * WHERE {{ "\
               "{objectType} "\
               "base:{subject} {predicate} ?object "\
               "{predBind} "\
               "}}"
        predBind = ""
        b = "base:"

        if pred:
            if useInversePred:
                b = "^base:"
                predBind = ". {{SELECT ?predicate WHERE {{?predicate owl:inverseOf base:{predicate} }}}}" 
                predBind = predBind.format(predicate=pred)
            else:
                predBind = " . BIND(base:{predicate} AS ?predicate)"
                predBind = predBind.format(predicate = pred)
            pred = "{base}{predicate}".format(base=b, predicate=pred)
        else:
            pred = "?predicate"
        if objType:
            objType = "?object a base:{object} . ".format(object=objType)

        # 2. Queries the server. If success create and return the list of results
        query = query.format(subject = sub, predicate = pred, objectType = objType, predBind = predBind)
        queryResult = self.queryManager.query(query)
        relationsList = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                relationsList.append(val)

        return relationsList

    # getTypeOfIndividual() queries the server
    # and returns the type of the given individual.
    def getTypeOfIndividual(self, individual):  
        # 1. Starts with building up the query based on input parameters     
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
               "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
               "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "\
               "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "\
               "SELECT * {{ "\
               "base:{ind} rdf:type ?directType . "\
               "FILTER NOT EXISTS {{ "\
               "base:{ind} rdf:type ?type . "\
               "?type rdfs:subClassOf ?directType . "\
               "FILTER NOT EXISTS {{ ?type owl:equivalentClass ?directType }}}} . "\
               "FILTER (?directType != owl:NamedIndividual)}}"

        query = query.format(ind = individual)

        # 2. Queries the server, builds result and returns
        queryResult = self.queryManager.query(query)
        result = ""

        if queryResult.status_code == 200:     
            results = queryResult.json()['results']['bindings']
            if results:
                result = self.getNameOfURI(results[0]['directType']['value'])
            else:
                errorText = "The input individual {ind} does not exist in the ontology".format(ind=individual)
                raise BaseException(errorText)
        return result

    # getDataProperties queries the server for data properties of given individual
    # and returns a list of data-type properties of the individual
    def getDataProperties(self, individual):
        # 1. Format query
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "SELECT * WHERE {{ "\
                "?predicate a owl:DatatypeProperty ."\
                "base:{subject} ?predicate ?object "\
                "}}"

        query = query.format(subject = individual)

        # 2. Query server, structure results and return list
        queryResult = self.queryManager.query(query)
        properties = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                properties.append(val)     
        return properties	

    #-----------------------------------------------------------------------------------------
    # 2. HELPER METHODS
    #-----------------------------------------------------------------------------------------   

    #-----------------------------------------------------------------------------------------
    # 2.1 METHODS FOR STRUCTURING DATA
    #-----------------------------------------------------------------------------------------   
    def pentaStructure(self, subjectPredicate, subjectURI):
        diagrams = []
        rationale = []
        for diagram in self.getRelations(subjectURI, 'modeledIn', 'Diagram'):
            diagrams.append(diagram[1])
        for r in self.getRelations(subjectURI, 'basedOn'):
            rationale.append(r[1])
        td = self.tripleDescription(subjectPredicate, subjectURI)
        td[1]['diagrams'] = diagrams
        td[1]['rationale'] = rationale
        print(td)
        return td 
    
    def tripleStructure(self, subjectPredicate, subjectURI):
        implementationClasses = []
        for id in self.getRelations(subjectURI, 'realizedBy', 'ImplementationClass'):
            implementationClasses.append(id[1])
 
        return (subjectPredicate, {'type': self.getTypeOfIndividual(subjectURI), 
                'object': subjectURI, 
                'implClasses': implementationClasses})
 
    def tripleDescription(self, subjectPredicate, subjectURI):
        return (subjectPredicate, {'type': self.getTypeOfIndividual(subjectURI), 
                'object': subjectURI, 
                'dataTypeProperties': self.getDataProperties(subjectURI)})

    def doubleStructure(self, subjectPredicate, subjectURI):
        return (subjectPredicate, {'type': self.getTypeOfIndividual(subjectURI), 
                'object': subjectURI})

    def uriStructure(self, subjectURI):
        return subjectURI

    #-----------------------------------------------------------------------------------------
    # 2.2 OTHER HELPER METHODS
    #-----------------------------------------------------------------------------------------   

    # findLeafIndividual() recursively finds and returns all leaf individuals of type "objectType"
    # in a nested structure. 
    # Parameters:
    #   subject: The item we start the search from
    #   predicate: The predicate relation from the subject to the objectType
    #   objectType: The type of the leaf object instances
    def findLeafIndividual(self, subject, predicate, objectType):
        subjectType = self.getTypeOfIndividual(subject)
        leaves = self.getRelations(sub=subject, pred=predicate, objType=objectType)  
        subjectTypeIndidviduals = self.getRelations(sub=subject, pred=predicate, objType=subjectType)
        for si in subjectTypeIndidviduals:            
            leaves += self.findLeafIndividual(si[1], predicate, objectType)
        return leaves

    # getRecursive() recursively looks for all related objects in a nested structure (such as DevelopmentClassPackage)
    # returns all nested objects of the same type as the given subject and all objects of type
    # objectType. 
    # Parameters:
    #   returnStructureFunc: This is a callback function, used to determine the structure of the output
    #   subject: The item we start the search from
    #   predicate: The predicate relation from the subject to the objectType
    #   objectType: The type of the object instances we are looking for
    #   hierarchy: If this is set to True, the structure of the return will be a nested list. It will
    #              contain information about the hierarchy of the components. Otherwise all components
    #              will be returned in a flat list.
    def getRecursive(self, returnStructureFunc, subject, predicate, objectType = "", hierarchy = False):
        targetIndividuals = self.getRelations(sub=subject, pred=predicate, objType=objectType)  
        descriptions = []

        # for ti in targetIndividuals:
        #         descriptions.append(returnStructureFunc(ti[0], ti[1]))

        subjectTypeIndidviduals = self.getRelations(sub=subject, pred=predicate)
        
        for si in subjectTypeIndidviduals:    
            slist = returnStructureFunc(si[0], si[1])
            if hierarchy:   
                slist[1]['children'] = self.getRecursive(returnStructureFunc, si[1], predicate, objectType, hierarchy)
            else:
                descriptions += self.getRecursive(returnStructureFunc, si[1], predicate, objectType, hierarchy)
            descriptions.append(slist)
        return descriptions
   
    # relationsBy() looks for the direct encapsulating objects of type objectType to an architecture fragment
    # returns a list of dictionaries which contain the encapsulating object and its child-components
    # if none is found, an empty list is returned
    # Parameters:
    #   architectureFragment: is the item we start from
    #   pred: is the predicate leading to the encapsulating object
    #   objectType: is the type of the encapsulating object
    def relationsBy(self, architectureFragment, pred="", objectType=""):
        connectedEntities = self.getRelations(sub=architectureFragment, pred=pred, objType=objectType)
        relations = []
        for cf in connectedEntities:
            relations.append({'type': self.getTypeOfIndividual(cf[1]),
                            'object': cf[1],
                            'components': [self.doubleStructure(item[0], item[1]) for item in self.getRelations(sub=cf[1], pred=pred, useInversePred=True)]
                            })
        return relations

    # recursiveRelationsBy() finds all architecture fragments that are related to the same object of type objectType.
    # returns a list of nested dictionaries. The dictionaries contain architecture fragments that are related to the same 
    # object.
    # Parameters:
    #   architectureFragment: is the object we start from
    #   pred: is the predicate leading to the encapsulating entity 
    #   objectType: is the type of the encapsulating entity
    def recursiveRelationsBy(self, architectureFragment, pred, objectType):
        endObjects = self.getRelations(architectureFragment, pred, objectType)
        relations = []
        if endObjects:
            relations = [self.tripleDescription(eo[0], eo[1]) for eo in endObjects]
            for r in relations:
                directChildren = self.getRelations(r[1]['object'], pred=pred, useInversePred=True)
                r[1]['children'] = []
                for dc in directChildren:
                    ds = self.tripleDescription(dc[0], dc[1])
                    ds[1]['children'] = self.getRecursive(self.tripleDescription, dc[1], 'compriseOf', hierarchy=True)
                    r[1]['children'].append(ds)
        else: 
            encapsulatingComponents = self.getRelations(architectureFragment, 'partOf')
            for ec in encapsulatingComponents:
                relations += (self.recursiveRelationsBy(ec[1], pred, objectType))
        return relations

    # recursiveEncapsulation() finds the nested structures from the given "architectureFragment"
    # to objects of the given "objectType" via the given predicate "pred". 
    # Returns a list of dictionaries representing this nested structures
    def recursiveEncapsulation(self, architectureFragment, pred, objectType = ""):
        
        endObjects = self.getRelations(architectureFragment, pred, objectType)
        ds = self.doubleStructure(None, architectureFragment)
        ds[1]['parent'] = []
        if endObjects:
            ds[1]['parent'] = [self.doubleStructure(eo[0], eo[1]) for eo in endObjects]
            relations = (ds)
        else:
            encapsulatingComponents = [r[1] for r in self.getRelations(architectureFragment, 'partOf')]
            for ec in encapsulatingComponents:
                ds[1]['parent'].append(self.recursiveEncapsulation(ec, pred))
                relations = (ds)
        return relations

    # getLeafParentHelper() is used to loop through the recursive structure returned by
    # recursiveEncapsulation() to get the leaf parent objects.
    def getLeafParentHelper(self, structure):
        if isinstance(structure, tuple):
            structure = structure[1]
        if 'parent' in list(structure.keys()):
            leaves = []
            for p in structure['parent']:
                leaf = self.getLeafParentHelper(p)
                if not isinstance(leaf, str):
                    leaves += leaf
                else:
                    leaves.append(leaf)
                return leaves
        else:
            return structure['object']

    # findIntersectingEntities() finds the objects of "objType" related to
    # the given "components". Then returns a list of dictionaries which describe
    # which components are related to the same objects. 
    def findIntersectingEntities(self, architectureFragments, pred, objType):
        featureList = []
        pathToFeature = []
        for af in architectureFragments:
            pathToFeature.append(self.recursiveEncapsulation(af, pred, objType))
        for item in pathToFeature:
            value = self.doubleStructure(None, item[1]['object'])
            value[1]['relatedEntities'] = []
            value[1]['relatedEntities'] += self.getLeafParentHelper(item[1])
            featureList.append(value)
        
        intersectingFeatures = {}
        tmpList = [(i,j) for i in featureList for j in i[1]['relatedEntities']]

        for item in tmpList:
            intersectingFeatures[item[1]] = []
        
        for item in tmpList:
            ds = self.doubleStructure(item[0][0], item[0][1]['object'])
            if ds not in intersectingFeatures[item[1]]:
                intersectingFeatures[item[1]].append(ds)

        return intersectingFeatures

    #A helper method for locationInArchitecture
    def addLeafToRecursiveStructure(self, structure, key):
        keys = list(structure[1].keys())
        if key in keys:
            for s in structure[1][key]:
                self.addLeafToRecursiveStructure(s, key)
        else:
            structure[1][key] = []
            leaves = self.getRelations(structure[1]['object'], pred='partOf', objType='ArchitecturalPattern')
            for leaf in leaves:
                structure[1][key].append(self.doubleStructure('partOf', leaf))
        return structure

    #-----------------------------------------------------------------------------------------
    # METHODS THAT ANSWERS THE QUESTIONS
    #-----------------------------------------------------------------------------------------

    # Explains the role of a feature
    def explainFeatureRole(self, feature):
        featureCompriseOfRelations = self.getRelations(feature, pred="compriseOf")
        featureModeledInRelations = self.getRelations(feature, pred="modeledIn")
        featureDataProperties = [self.tripleDescription(None, feature)]
        requirementDataProperties = []
        diagramDataProperties = []
        useCaseDataProperties = []
        
        for fr in featureCompriseOfRelations:
            requirementDataProperties.append(self.tripleDescription(fr[0], fr[1]))                        
            for rr in self.getRelations(fr[1], pred="partOf", objType="UseCase"):
                if(self.tripleDescription(rr[0], rr[1]) not in useCaseDataProperties):
                    useCaseDataProperties.append(self.tripleDescription(rr[0], rr[1]))
                        
        for fmr in featureModeledInRelations:
            diagramDataProperties.append(self.tripleDescription(fmr[0], fmr[1]))
            
        return {'Feature': featureDataProperties, 
                'Requirement': requirementDataProperties, 
                'UseCase': useCaseDataProperties, 
                'Diagram': diagramDataProperties}

    # Explains the implementation of a feature
    def explainFeatureImplementation(self, feature):
        featureDevelopmentClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="DevelopmentClassPackage")
        featureClasses = []
        for fp in featureDevelopmentClassPackages:
            featureClasses.append(self.tripleDescription(fp[0], fp[1]))
            featureClasses += self.getRecursive(self.tripleDescription, fp[1], "compriseOf", "DevelopmentClassEntity")
        return  featureClasses

    # Shows all implementation classes related to given feature
    def relatedImplementationClasses(self, feature):
        featureDevelopmentClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="DevelopmentClassPackage")
        featureDs = self.doubleStructure(None, feature)
        featureDs[1]['implClasses'] = []
        featureDs[1]['children'] = []
        featureArchitecture = []

        implementationClasses = []
        for ic in self.getRelations(feature, 'realizedBy', 'ImplementationClass'):
            implementationClasses.append(ic[1])

        for fcp in featureDevelopmentClassPackages:
            ds = self.doubleStructure(fcp[0], fcp[1])
            ds[1]['implClasses'] = implementationClasses
            ds[1]['children'] = self.getRecursive(self.tripleStructure, fcp[1], 'compriseOf', "DevelopmentClassEntity", True)
            featureDs[1]['children'].append(ds)
        featureArchitecture.append(featureDs)
        return featureArchitecture

    # The methods below finds all architecture fragments that are related to
    # the same object as the given architecture fragment.
    def relationsByFeature(self, architectureFragment):
        return self.relationsBy(architectureFragment, 'provides', 'Feature')
    
    def relationsByEncapsulatingComponent(self, architectureFragment):
        return self.relationsBy(architectureFragment, pred='partOf')

    def relationsByArchitecturalRole(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, "playsRole", "Role")
    
    def relationsByNonFunctionalRequirement(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, 'satisfies', 'Non-functionalRequirement')
    
    def relationsByFunctionalRequirement(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, 'satisfies', 'FunctionalRequirement')

    def relationsByDesignOption(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, "resultOf", "DesignOption")

    def relationsByDiagram(self, architectureFragment):
        return self.relationsBy(architectureFragment, pred="modeledIn")

    # From a given set of architecture fragments, these methods find
    # which architecture fragments are related to the same objects
    def findIntersectingFeatures(self, architectureFragments):
        return self.findIntersectingEntities(architectureFragments, 'provides', 'Feature')
    
    def findIntersectingFunctionalRequirements(self, architectureFragments):
        return self.findIntersectingEntities(architectureFragments, 'satisfies', 'FunctionalRequirement')

    def findIntersectingNonFunctionalRequirements(self, architectureFragments):
        return self.findIntersectingEntities(architectureFragments, 'satisfies', 'Non-functionalRequirement')

    # From any architectural fragment
    def getArchitecture(self, architectureFragment):
        role = self.recursiveEncapsulation(architectureFragment, 'playsRole', 'Role')
        leafParents = self.getLeafParentHelper(role)
        relations = []
        for lp in leafParents:
            relations += self.getRelations(lp, pred='partOf', objType='ArchitecturalPattern')
        return [self.tripleDescription(r[0], r[1]) for r in relations]
    
    def locationInArchitecture(self, architectureFragment):
        role = self.recursiveEncapsulation(architectureFragment, 'playsRole', 'Role')
        test = self.addLeafToRecursiveStructure(role, 'parent')
        return test

    def rationaleOfArchitecture(self, architecture):
        decisionsList = []
        if self.getTypeOfIndividual(architecture) == 'ArchitecturalPattern':
            decisions = self.getRelations(architecture, pred='resultOf', objType='DesignOption')
            for d in decisions:
                rationale = self.getRelations(d[1], pred='compriseOf')
                rationaleList = []
                for r in rationale:
                    item = self.tripleDescription(r[0], r[1])
                    rationaleList.append(item)
                ds = self.doubleStructure(d[0], d[1])
                ds[1]['rationale'] = rationaleList
                decisionsList.append(ds)
        return decisionsList

    def getAllTechnologies(self):
        return self.getIndividualsByType('Technology')

    def getRationaleOfTechnology(self, technology):
        technologyList = []
        if self.getTypeOfIndividual(technology) == 'Technology':
            decisions = self.getRelations(technology, pred='compriseOf')
            for d in decisions:
               ds = self.doubleStructure(d[0], d[1])
               ds[1]['rationale'] = self.getDataProperties(d[1])
               technologyList.append(ds)
        return technologyList

    def getDescriptionOfTechnology(self, technology):
        if self.getTypeOfIndividual(technology) == 'Technology':
            return self.tripleDescription(None, technology)

    def getArchitectureByTechnology(self, technology):
        if self.getTypeOfIndividual(technology) == 'Technology':
            arch = self.getRelations(technology, pred='resultsIn')
            ds = self.doubleStructure(None, technology)
            ds[1]['relatedComponents'] = [self.doubleStructure(a[0], a[1]) for a in arch]
            return ds
        return None

#-----------------------------------------------------------------------------------------
# MAIN CLASS USED FOR TESTING
#-----------------------------------------------------------------------------------------

# ir = InformationRetriever('')

# objectStructure = []
# objects = ir.getAllObjects()
# for obj in objects:
#     objStructure = {'type':ir.getTypeOfIndividual(obj), 
#                     'object': obj, 
#                     'dataTypeProperties': ir.getDataProperties(obj)
#                     }
#     objectStructure.append(objStructure)

# allInverseRelations = ir.getAllInverses()

# inverses = []
# for relation in allInverseRelations:
#     if(relation[1] not in inverses):
#         inverses.append(relation[0])

# relations = ir.getAllObjectsAndRelations()

# f = open('explanationData.js', 'w') 
# f.truncate(0)
# f.write("allObjects = " + json.dumps(objectStructure))
# f.write("; allRelations = " + json.dumps(relations))
# f.write("; allInverseRelations = " + json.dumps(inverses))
# f.close()
