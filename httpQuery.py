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
    def getRelations(self, entity):
        #Get all relations from entity
        queryRF = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
				"PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "SELECT * WHERE {{ "\
				"?predicate a owl:ObjectProperty ."\
                "base:{subject} ?predicate ?object "\
                "}}"
				
		
        #Format strings
        queryRF = queryRF.format(subject = entity)

        queryResultRF = self.queryManager.query(queryRF)

        relationsList = []

        if queryResultRF.status_code == 200:
            results = queryResultRF.json()['results']['bindings']
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                relationsList.append(val)

                
        return relationsList
		
    def getDataProperties(self, entity):
        #Get the data properties of the entity
        query = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "PREFIX owl: <http://www.w3.org/2002/07/owl#> " \
                "SELECT * WHERE {{ "\
                "?predicate a owl:DatatypeProperty ."\
                "base:{subject} ?predicate ?object "\
                "}}"
        #Format strings
        query = query.format(subject = entity)

        queryResult = self.queryManager.query(query)

        properties = []

        if queryResult.status_code == 200:
            results = queryResult.json()['results']['bindings']
            for item in results:
                val = (self.getNameOfURI(item['predicate']['value']), self.getNameOfURI(item['object']['value']))
                properties.append(val)

                
        return properties	
        

        
    def explainFeatureRole(self, feature):
        featureRelations = [r for r in self.getRelations(feature) if "compriseOf" in r[0] or "modeledIn" in r[0]]
        featureDataProperties = [(feature, self.getDataProperties(feature))]
        requirementDataProperties = []
        diagramDataProperties = []
        useCaseDataProperties = []
        
        
        for fr in featureRelations:
            if "compriseOf" in fr[0]:
                requirementRelations = []
                frName = fr[1]
                requirementDataProperties.append((frName, self.getDataProperties(frName)))
                requirementRelations.append((frName, self.getRelations(frName)))
                
                for rr in self.getRelations(frName):
                    if "partOf" in rr[0] and feature not in rr[1]:
                        requirementName = rr[1]
                        useCaseDataProperties.append((requirementName, self.getDataProperties(requirementName)))
            else:
                diagramDataProperties.append((fr[1], self.getDataProperties(fr[1])))
            
        return {'Feature':featureDataProperties, 'Requirement': requirementDataProperties, 'UseCase': useCaseDataProperties, 'Diagram': diagramDataProperties}


    def explainFeatureImplementation(self, feature)
        featureReuirements = [r for r in self.getRelations(feature) if "compriseOf" in r[0]]
        
        for fr in featureReuirements:
            featureReuirements.append((frName, self.getRelations(fr[1])))

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
    finePrint(ir.getRelations(inp))
    finePrint(ir.getDataProperties(inp))
    #pprint.pprint(ir.explainFeatureRole(inp))
    #print('\n')
    #print('\n')
    #print(ir.explainFeatureRole(inp))
