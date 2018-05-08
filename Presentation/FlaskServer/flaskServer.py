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
                            
@app.route('/test/<feature>')
def test(feature):
    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    
    explanationGenerator = httpQuery.ExplanationGenerator()
    explanationTemplates = httpQuery.ExplanationTemplates()
    
    structure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + feature)
    explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + feature, structure)

    diagramFilePaths = {diagram: 'static/images/' + diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
    print(diagramFilePaths)

    return render_template('childtemplate.html', 
                            tab_buttons=[{'id':'functional_view_tab', 'name': 'Functional view'}, 
                                        {'id':'logical_view_tab', 'name': 'Logical view'}, 
                                        {'id':'pattern_view_tab', 'name': 'Pattern view'}],  
                            diagram_path='static/ClusteringGraph.js', 
                            diagram_file_paths=diagramFilePaths,
                            explanation=explanation,
                            structure=json.dumps(structure.toDict()))
                            
