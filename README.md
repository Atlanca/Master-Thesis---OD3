# System Explanation Composer (SEC)

__by Alex Tao and Mahsa Roodbari__

For demonstration of the tool and more information about the developer questions and ontology, follow the link below.
https://software-explanation-composer.000webhostapp.com/

SEC consists of three major components. The first component is the ontology. The ontology serves as a database to model and store architectural knowledge. The ontology is hosted in an Apache Jena Fuseki Server to allow outside applications to fetch information from the ontology via SparQL queries (Apache Jena is not included in this repository). The second component is a set of common questions which developers frequently ask during development tasks which SEC is designed to answer. The third and last component is the explanation generator which makes use of all the previous components. The explanation generator queries the ontology to fetch links, entities, textual descriptions, etc. to present both textual and visual explanations for the developer questions.

![](system.png)

# Folder structure
This section describes the responsibilities of classes and where they are located. All code for SEC resides in: __Presentation\FlaskServer__.

## Back-end
All files for the back-end in found in __Presentation\FlaskServer__. The back-end handles querying data from ontology and building the explanations. To build explanations we do it in two parts, first we build a data structure that includes all entities, relationships and descriptions. Then we build section structures based on this data structure. These two structures are lastly passed on to the front-end for layouting and rendering.  

#### Main class:
- __flaskServer.py__ is used to run the server. It is also responsible for mapping the URLs to their actions.

#### Query
- __sparqlQueryManager.py__ is used to query entities and relationships from the ontology

#### Classes that build explanation
- __explanationStructureGenerator.py__ uses sparqlQueryManager to build structural explanations to questions
- __explanationTemplatingEngine.py__ builds summaries for each explanation.

#### Data structures
- __ontologySturctureModel.py__ consists of data structures used to store entities and relationships
- __sectionModel.py__ is used to store textual description sections

## Front-end
The front-end consists of two main parts, page layout (and logic) and graph builders. The layout lays the design of the website, and the graph builders build visualizations of given entities and relationships.

#### Page layout
All files for layout can be found in: __\Presentation\FlaskServer\templates__. Jinja is used as a templating engine to add logic into HTML and make them reusable. The three most important layout classes are:

- __baseExplanationTemplate.html__ this is the base layout template for all explanations.
- __childtemplate.html__ this extends baseExplanationTemplate.html and adds the textual descriptions to it
- __front-page-template.html__ is the front page

#### Page logic
All files for page logic is found in __Presentation\FlaskServer\static__.

- __explanationPageLogic.js__ is contains all logic for the page layout.
- __explanationFonts.js__ contains all colors used in the layout.

#### Page styling
All files for styling the page is found in __Presentation\FlaskServer\static\css__.

#### Graph builders
All files for building the interactive graph can be found in __Presentation\FlaskServer\static__. This folder is currently a bit messy, but I will name the javascript classes we use to generate the graphs, and the rest are libraries.

- __ClusteringGraph.js__ is used to generate interactive visualizations in explanations.
- __ExplanationComposer.js__ is used to generate the interactive diagram for the explanation composer feature.
- __graphHelper.js__ stores all helper functions used in the two above classes.
- __popup-graph.js__ stores some logic for popup.




