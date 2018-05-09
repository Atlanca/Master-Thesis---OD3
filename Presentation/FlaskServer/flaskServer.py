import json
from flask import Flask, request, send_from_directory, render_template, Markup
import httpQuery
import re

app = Flask(__name__, static_url_path="/static")

def diagramUriToFileName(diagramName):
    match = re.search('\\wigure_\\d\.\\d+', diagramName)
    finalString = re.sub('\.', '_', str(match.group(0)))
    return finalString

@app.route('/index')
def index():
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    
    explanationGenerator = httpQuery.ExplanationGenerator()
    explanationTemplates = httpQuery.ExplanationTemplates()
    
    structure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + 'purchase_products')
    explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + 'purchase_products', structure)

    diagramFilePaths = {diagram: 'static/images/' + diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
    print(diagramFilePaths)

    return render_template('childtemplate.html', 
                            tab_buttons=['Functional view', 'Logical view', 'Pattern view'],  
                            diagram_path='static/ClusteringGraph.js', 
                            diagram_file_paths=diagramFilePaths,
                            explanation=explanation,
                            structure=json.dumps(structure.toDict()))
                            
@app.route('/q2/logical/<feature>')
def q2_logical(feature):
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    
    explanationGenerator = httpQuery.ExplanationGenerator()
    explanationTemplates = httpQuery.ExplanationTemplates()

    functionalStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(baseUri + feature)

    logicalStructure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + feature)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, logicalStructure.entities))]


    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + feature, logicalStructure)


    diagramFilePaths = {diagram: 'static/images/' + diagramUriToFileName(diagram) + '.png' for entity in logicalStructure.entities for diagram in set(entity.diagrams)}
    print(diagramFilePaths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            diagram_file_paths=diagramFilePaths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional view', 'entity_structure': json.dumps(functionalStructure.toDict()), 'explanation': explanation, 'background': '#fff6f4'}, 
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Logical view', 'entity_structure': json.dumps(logicalStructure.toDict()), 'explanation': explanation, 'background': '#f4f6ff'}, 
                                        'pattern': {'tab_id':'pattern_view_tab', 'tab_name': 'Pattern view', 'entity_structure': json.dumps(patternStructure.toDict()), 'explanation': explanation, 'background': '#f4fffc'}
                                        })
                            