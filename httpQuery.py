import requests
import json
import re

class SparqlQueryManager:
    def __init__(self, url):
        self.url = url

    def query(self, query):
        return requests.post(self.url, data = {'query': query})

class InformationRetriever:
    def __init__(self, url):
        self.queryManager = SparqlQueryManager('http://localhost:3030/AKOntology/query')

    #Returns all relations to and from an entity in a list.
    #The relation, entity and a string 'to' or 'from' are returned in a tuple. 
    #If the relation is returned first, then another entity has a relation to this entity. (to)
    #If the relation is returned second, then this entity is has a relation to another entity. (from)
    def getRelations(self, entity):
        #Get all relations from entity
        queryRF = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "SELECT * WHERE {{ "\
                "?predicate a owl:ObjectProperty ."\
                "base:{subject} ?predicate ?object "\
                "}}"
        #Get all reations to entity
        queryRT = "PREFIX base:<http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> "\
                "SELECT * WHERE {{ "\
                "?subject ?predicate base:{object} "\
                "}}"

        #Format strings
        queryRF = queryRF.format(subject = entity)
        queryRT = queryRT.format(object = entity)

        queryResultRF = self.queryManager.query(queryRF)
        queryResultRT = self.queryManager.query(queryRT)

        relationsList = []



        if queryResultRF.status_code == 200:
            results = queryResultRF.json()['results']['bindings']
            for item in results:
                val = (item['predicate']['value'], item['object']['value'], 'from')
                relationsList.append(val)

        if queryResultRT.status_code == 200:
            results = queryResultRT.json()['results']['bindings']
            for item in results:
                val = (item['subject']['value'], item['predicate']['value'], 'to')
                relationsList.append(val)
        
        return relationsList
        
    def explainRole(self, feature):
        featureRelations = [r for r in self.getRelations(feature) if "compriseOf" in r[0] or "modeledIn" in r[0]]
        print(featureRelations)
        return featureRelations


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
    finePrint(ir.explainRole(inp))
    print('\n')
