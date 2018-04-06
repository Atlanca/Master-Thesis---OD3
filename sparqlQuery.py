from owlready2 import *
import owlready2
owlready2.JAVA_EXE = "C:\\Program Files\\Java\\jdk1.8.0_121\\bin\\java.exe"

onto = get_ontology("file://rootontologyV3.owl").load()
sync_reasoner(default_world)
graph = default_world.as_rdflib_graph()

def getAllRelations(individual):
    relationsQuery = """\
PREFIX base: <http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> \
SELECT ?p \
WHERE {{ \
base:{individual} ?p ?o \
}}""".format(individual=individual)

    relationsResult = list(graph.query(relationsQuery))
    for r in relationsResult:
        print(r)

def testa(relation):
    relationsQuery = """\
PREFIX base: <http://www.semanticweb.org/mahsaro/ontologies/2018/2/untitled-ontology-5#> \
SELECT ?s \
WHERE {{ \
?s base:{relation} ?o \
}}""".format(relation=relation)

    relationsResult = list(graph.query(relationsQuery))
    for r in relationsResult:
        print(r)   
testa("partOf")
#getAllRelations("choice_three_tier_client_server_1")