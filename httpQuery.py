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
    #Returns all relations to and from an entity in a list.
    #useInversePred determines whether to use the given predicate or to use the inverse of it.
    #Always return a tuple in the following format: (predicate, object)
    def getRelations(self, sub, pred="", objType="", useInversePred=False):
       #Get all relations from entity
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
            #This if clause makes sure we return the
            #predicate even if the predicate is given
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

        query = query.format(subject = sub, predicate = pred, objectType = objType, predBind = predBind)

        queryResultRF = self.queryManager.query(query)

        relationsList = []

        if queryResultRF.status_code == 200:
            results = queryResultRF.json()['results']['bindings']
            
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                relationsList.append(val)

        return relationsList
        
    def getTypeOfIndividual(self, individual):       
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

        queryResult = self.queryManager.query(query)

        result = ""
        if queryResult.status_code == 200:      
            results = queryResult.json()['results']['bindings']
            result = self.getNameOfURI(results[0]['directType']['value'])
            
        return result
                
    def getDataProperties(self, individual):
        #Get the data properties of the entity
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "SELECT * WHERE {{ "\
                "?predicate a owl:DatatypeProperty ."\
                "base:{subject} ?predicate ?object "\
                "}}"
        #Format strings
        query = query.format(subject = individual)

        queryResult = self.queryManager.query(query)

        properties = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                properties.append(val)
                      
        return properties	
        
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
        
    #Finds and returns all leaf individuals of type "objectType" 
    def findLeafIndividual(self, subject, predicate, objectType):
        subjectType = self.getTypeOfIndividual(subject)
        targetIndividuals = self.getRelations(sub=subject, pred=predicate, objType=objectType)  
        subjectTypeIndidviduals = self.getRelations(sub=subject, pred=predicate, objType=subjectType)
        for si in subjectTypeIndidviduals:            
            targetIndividuals += self.findLeafIndividual(si[1], predicate, objectType)
        return targetIndividuals

    #Recursively looks for objects type in recursive structures
    #Returns everything in a hierarchy if hierarchy is set to True
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
    
    #Methods used by getRecursiveWithHierarchy to control how the output is structured.
    #These methods may be removed later
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

    def getRelatedImplementationClasses(self, feature):
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

    #Explains the implementation
    def explainFeatureImplementation(self, feature):
        featureClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="ClassPackage")
        featureClasses = []
        for fp in featureClassPackages:
            featureClasses.append({ 'individualType': self.getTypeOfIndividual(fp[1]),
                                    'individualObject': fp[1],
                                    'description': self.getDataProperties(fp[1])})
            featureClasses += self.getRecursive(self.tripleDescription, fp[1], "compriseOf", "ClassEntity")
        return  featureClasses
            
    def relationsBy(self, architectureFragment, pred="", objectType=""):
        connectedEntities = self.getRelations(sub=architectureFragment, pred=pred, objType=objectType)
        relations = []
        for cf in connectedEntities:
            relations.append({'encapsulatingType': self.getTypeOfIndividual(cf[1]),
                            'encapsulatingObject': cf[1],
                            'components': self.getRelations(sub=cf[1], pred=pred, useInversePred=True)})
        return relations

    def recursiveRelationsBy(self, architectureFragment, pred, objectType):
        endObjects = self.getRelations(architectureFragment, pred, objectType)
        relations = []
        if endObjects:
            relations = [self.doubleStructure(eo[1]) for eo in endObjects]
            for r in relations:
                directChildren = self.getRelations(r['individualObject'], pred=pred, useInversePred=True)
                r['children'] = []
                for dc in directChildren:
                    ds = self.doubleStructure(dc[1])
                    ds['children'] = self.getRecursive(self.doubleStructure, dc[1], 'compriseOf', 'ClassEntity', hierarchy=True)
                    r['children'].append(ds)
        else: 
            encapsulatingComponents = self.getRelations(architectureFragment, 'partOf')
            for ec in encapsulatingComponents:
                relations += (self.recursiveRelationsBy(ec[1], pred, objectType))
        return relations

    def relationsByFeature(self, architectureFragment):
        return self.relationsBy(architectureFragment, 'provides', 'Feature')
    
    def relationsByEncapsulatingComponent(self, architectureFragment):
        return self.relationsBy(architectureFragment, pred='partOf')

    def relationsByArchitecturalRole(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, "playsRole", "Role")
    
    def relationsByRequirement(self, architectureFragment):
        return self.relationsBy(architectureFragment, pred='satisfies')
    
    def relationsByDecision(self, architectureFragment):
        return self.recursiveRelationsBy(architectureFragment, "resultOf", "Decision")

    def relationsByDiagram(self, architectureFragment):
        return self.relationsBy(architectureFragment, pred="modeledIn")

def finePrint(relations):    
    d = ""
    for r in relations:
        if("Description" in r[0]):
            d = r
        elif("NamedIndividual" not in r[1]):
            print(re.sub(".+#", '', r[0]) + ', ' + re.sub(".+#", '', r[1])) 
    if d != "":
        print(re.sub(".+#", '', d[0]) + ', ' + re.sub(".+#", '', d[1]))

inp = ""
ir = InformationRetriever('')
while(inp != "exit"):
    inp = input("Input object to query: ")
    #finePrint(ir.getRelations(inp))
    #finePrint(ir.getDataProperties(inp))
    #print('\n')
    #print(ir.explainFeatureRole(inp))
    #print(ir.getTypeOfIndividual(inp))
    #print(ir.getRecursiveWithHierarchy(ir.doubleStructure, inp, 'compriseOf', 'ClassEntity'))
    #print(ir.getRelatedImplementationClasses(inp))
    #print(ir.explainFeatureImplementation(inp))
    #print(ir.relationsBy(inp, 'partOf', 'ClassPackage'))
    print(ir.relationsByArchitecturalRole(inp))