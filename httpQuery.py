import requests
import json
import re
import pprint

class SparqlQueryManager:
    def __init__(self, url):
        self.url = url

    def query(self, query):
        return requests.post(self.url, data = {'query': query})

class InformationRetriever:
    def __init__(self, url):
        self.queryManager = SparqlQueryManager('http://localhost:3030/Thesis/query')
    def getNameOfURI(self, uri):
        return (re.sub(".+#", '', uri))	
    
    #-----------------------------------------------------------------------------------------
    # 1. BASIC QUERY HELPER METHODS
    #-----------------------------------------------------------------------------------------

    # getRelations() returns all predicates from the given subject to an object in a list.
    # useInversePred determines whether to use the given predicate or to use the inverse of it.
    # always returns a tuple in the following format: (predicate, object)
    def getRelations(self, sub, pred="", objType="", useInversePred=False):
        
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
            result = self.getNameOfURI(results[0]['directType']['value'])
            
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
    def tripleStructure(self, subjectURI):
        implementationClasses = []
        for id in self.getRelations(subjectURI, 'realizedBy', 'ImplementationClass'):
            implementationClasses.append(id[1])
 
        return {'individualType': self.getTypeOfIndividual(subjectURI), 
                'individualObject': subjectURI, 
                'relatedImplClasses': implementationClasses}
 
    def tripleDescription(self, subjectURI):
        return {'individualType': self.getTypeOfIndividual(subjectURI), 
                'individualObject': subjectURI, 
                'description': self.getDataProperties(subjectURI)}

    def doubleStructure(self, subjectURI):
        return {'individualType': self.getTypeOfIndividual(subjectURI), 
                'individualObject': subjectURI}

    def uriStructure(self, subjectURI):
        return subjectURI

    #-----------------------------------------------------------------------------------------
    # 2.1 OTHER HELPER METHODS
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

    # getRecursive() recursively looks for all related objects in a nested structure (such as ClassPackage)
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
    def getRecursive(self, returnStructureFunc, subject, predicate, objectType, hierarchy = False):
        targetIndividuals = self.getRelations(sub=subject, pred=predicate, objType=objectType)  
        descriptions = []

        for ti in targetIndividuals:
            descriptions.append(returnStructureFunc(ti[1]))

        subjectTypeIndidviduals = self.getRelations(sub=subject, pred=predicate, objType=self.getTypeOfIndividual(subject))
         
        for si in subjectTypeIndidviduals:    
            slist = returnStructureFunc(si[1])
            if hierarchy:   
                slist['children'] = (self.getRecursive(returnStructureFunc, si[1], predicate, objectType, hierarchy))
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
            relations.append({'encapsulatingType': self.getTypeOfIndividual(cf[1]),
                            'encapsulatingObject': cf[1],
                            'components': self.getRelations(sub=cf[1], pred=pred, useInversePred=True)})
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
            relations = [self.tripleDescription(eo[1]) for eo in endObjects]
            for r in relations:
                directChildren = self.getRelations(r['individualObject'], pred=pred, useInversePred=True)
                r['children'] = []
                for dc in directChildren:
                    ds = self.doubleStructure(dc[1])
                    ds['children'] = self.getRecursive(self.tripleDescription, dc[1], 'compriseOf', 'ClassEntity', hierarchy=True)
                    r['children'].append(ds)
        else: 
            encapsulatingComponents = self.getRelations(architectureFragment, 'partOf')
            for ec in encapsulatingComponents:
                relations += (self.recursiveRelationsBy(ec[1], pred, objectType))
        return relations

    # recursiveEncapsulation() finds the nested structures from the given list of "architectureFragments"
    # to objects of the given "objectType" via the given predicate "pred". 
    # Returns a list of dictionaries representing this nested structures
    def recursiveEncapsulation(self, architectureFragments, pred, objectType = ""):
        relations = []
        for af in architectureFragments:
            endObjects = self.getRelations(af, pred, objectType)
            if endObjects:
                ds = self.doubleStructure(af)
                ds['parent'] = [self.doubleStructure(eo[1]) for eo in endObjects]
                relations.append(ds)
            else:
                encapsulatingComponents = [r[1] for r in self.getRelations(af, 'partOf')]
                ds = self.doubleStructure(af)
                ds['parent'] = self.recursiveEncapsulation(encapsulatingComponents, pred)
                relations.append(ds)
        return relations

    # getLeafParentHelper() is used to loop through the recursive structure returned by
    # recursiveEncapsulation() to get the leaf parent objects.
    def getLeafParentHelper(self, structure):
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
            return structure['individualObject']

    # findIntersectingEntities() finds the objects of "objType" related to
    # the given "components". Then returns a list of dictionaries which describe
    # which components are related to the same objects. 
    def findIntersectingEntities(self, architectureFragments, pred, objType):
        featureList = []
        pathToFeature = self.recursiveEncapsulation(architectureFragments, pred, objType)
        for item in pathToFeature:
            value = self.doubleStructure(item['individualObject'])
            value['relatedEntities'] = []
            value['relatedEntities'] += self.getLeafParentHelper(item)
            featureList.append(value)
        
        intersectingFeatures = {}
        tmpList = [(i,j) for i in featureList for j in i['relatedEntities']]

        for item in tmpList:
            intersectingFeatures[item[1]] = []
        
        for item in tmpList:
            intersectingFeatures[item[1]].append(item[0]['individualObject'])
 
        return intersectingFeatures

    #-----------------------------------------------------------------------------------------
    # METHODS THAT ANSWERS THE QUESTIONS
    #-----------------------------------------------------------------------------------------

    # Explains the role of a feature
    def explainFeatureRole(self, feature):
        featureCompriseOfRelations = self.getRelations(feature, pred="compriseOf")
        featureModeledInRelations = self.getRelations(feature, pred="modeledIn")
        featureDataProperties = [(feature, self.getDataProperties(feature))]
        requirementDataProperties = []
        diagramDataProperties = []
        useCaseDataProperties = []
        
        for fr in featureCompriseOfRelations:
            req = fr[1]
            requirementDataProperties.append((req, self.getDataProperties(req)))                        
            for rr in self.getRelations(req, pred="partOf", objType="UseCase"):
                    useCase = rr[1]
                    useCaseDataProperties.append((useCase, self.getDataProperties(useCase)))
                        
        for fmr in featureModeledInRelations:
            diagramDataProperties.append((fmr[1], self.getDataProperties(fmr[1])))
            
        return {'Feature':featureDataProperties, 
                'Requirement': requirementDataProperties, 
                'UseCase': useCaseDataProperties, 
                'Diagram': diagramDataProperties}

    # Explains the implementation of a feature
    def explainFeatureImplementation(self, feature):
        featureClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="ClassPackage")
        featureClasses = []
        for fp in featureClassPackages:
            featureClasses.append({ 'individualType': self.getTypeOfIndividual(fp[1]),
                                    'individualObject': fp[1],
                                    'description': self.getDataProperties(fp[1])})
            featureClasses += self.getRecursive(self.tripleDescription, fp[1], "compriseOf", "ClassEntity")
        return  featureClasses

    # Shows all implementation classes related to given feature
    def relatedImplementationClasses(self, feature):
        featureClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="ClassPackage")
        featureArchitecture = []

        implementationClasses = []
        for ic in self.getRelations(feature, 'realizedBy', 'ImplementationClass'):
            implementationClasses.append(ic[1])

        for fcp in featureClassPackages:
            featureArchitecture.append({'individualType': self.getTypeOfIndividual(fcp[1]),
                                        'individualObject': fcp[1], 
                                        'relatedImplClasses': implementationClasses,
                                        'children': self.getRecursive(self.tripleStructure, fcp[1], "compriseOf", "ClassEntity", True)})
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

    def relationsByDecision(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, "resultOf", "Decision")

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

#-----------------------------------------------------------------------------------------
# MAIN CLASS USED FOR TESTING
#-----------------------------------------------------------------------------------------

def finePrint(relations):    
    d = ""
    for r in relations:
        if("Description" in r[0]):
            d = r
        elif("NamedIndividual" not in r[1]):
            print(re.sub(".+#", '', r[0]) + ', ' + re.sub(".+#", '', r[1])) 
    if d != "":
        print(re.sub(".+#", '', d[0]) + ', ' + re.sub(".+#", '', d[1]))

#inp = ""
#while(inp != "exit"):
#inp = input("Input object to query: ")

ir = InformationRetriever('')
print("\n\nFeature role: purchase_products")
print(ir.explainFeatureRole("purchase_products"))

print("\n\nRelated implementation classes: purchase_products")
print(ir.relatedImplementationClasses("purchase_products"))

print("\n\nExplanation of implementation classes: purchase_products")
print(ir.explainFeatureImplementation("purchase_products"))

print("\n\nRelations by architectural role: CartForms")
print(ir.relationsByArchitecturalRole("CartForms"))

print("\n\nRelations by diagram: web_application_server_package_1")
print(ir.relationsByDiagram("web_application_server_package_1"))

print("\n\nIntersecting features of: CartForms, AddressForms, test1 and AddressForms")
print(ir.findIntersectingFeatures(['CartForms', 'AddressForms', 'test1', 'AddressForms']))