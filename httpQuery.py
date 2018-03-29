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
    #The relation, entity and a string 'to' or 'from' are returned in a tuple. 
    #If the relation is returned first, then another entity has a relation to this entity. (to)
    #If the relation is returned second, then this entity is has a relation to another entity. (from)
    def getRelations(self, sub, pred="", objType=""):
       #Get all relations from entity
       
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
               "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
               "SELECT * WHERE {{ "\
               "{objectType} "\
               "base:{subject} {predicate} ?object "\
               "{predBind} "\
               "}}"
        predBind = ""
        if pred:
            pred = "base:{predicate}".format(predicate=pred)
            predBind = " . BIND(base:{predicate} AS ?predicate)".format(predicate = pred)
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
                

        
    # def getSpecificEntityRelations(self, subject, predicate, object):
        # #Get all relations from entity
        # queryRF = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
				# "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                # "SELECT * WHERE {{ "\
				# "?predicate a base:{predicate} ."\
                # "?object a  base:{object} ."\
                # "base:{subject} ?predicate ?object "\
                # "}}"
				
		
        # #Format strings
        # queryRF = queryRF.format(subject = individual, object = entity)

        # queryResultRF = self.queryManager.query(queryRF)

        # relationsList = []

        # if queryResultRF.status_code == 200:
            # results = queryResultRF.json()['results']['bindings']
            # for item in results:
                # val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                # relationsList.append(val)

                
        # return relationsList
		
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
            
        return {'Feature':featureDataProperties, 'Requirement': requirementDataProperties, 'UseCase': useCaseDataProperties, 'Diagram': diagramDataProperties}
        
    def findLeafIndividual(self, subject, predicate, objectType):
        subjectType = self.getTypeOfIndividual(subject)
        targetIndividuals = self.getRelations(sub=subject, pred=predicate, objType=objectType)  
        subjectTypeIndidviduals = self.getRelations(sub=subject, pred=predicate, objType=subjectType)
        for si in subjectTypeIndidviduals:            
            targetIndividuals += self.findLeafIndividual(si[1], predicate, objectType)
        return targetIndividuals



    def explainFeatureImplementation(self, feature):
        featureClassPackages = self.getRelations(sub=feature, pred="realizedBy", objType="ClassPackage")
        
        featureClasses = []
        for fp in featureClassPackages:
            featureClasses += self.findLeafIndividual(fp[1], "compriseOf", "ClassEntity")

        return  featureClasses
            
        

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
    print(ir.explainFeatureImplementation(inp))