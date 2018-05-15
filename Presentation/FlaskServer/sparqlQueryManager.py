from SPARQLWrapper import SPARQLWrapper, JSON

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