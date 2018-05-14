import json
from flask import Flask, request, send_from_directory, render_template, Markup
import httpQuery
import re

app = Flask(__name__, static_url_path="/static")
baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
explanationGenerator = httpQuery.ExplanationGenerator()
explanationTemplates = httpQuery.ExplanationTemplates()


def diagramUriToFileName(diagramName):
    match = re.search('\\wigure_\\d\.\\d+', diagramName)
    finalString = re.sub('\.', '_', str(match.group(0)))
    return finalString

@app.route('/index')
def index():
        
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
                            
@app.route('/q2/<feature>')
def q2_logical(feature):

    functionalStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(baseUri + feature)
    func_explanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(baseUri + feature, functionalStructure)

    logicalStructure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + feature)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, logicalStructure.entities))]
    logic_explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + feature, logicalStructure)

    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    pattern_explanation = explanationTemplates.generatePatternFeatureImplementationSummary(baseUri + feature, patternStructure)

    diagramFilePaths = {diagram: 'static/images/' + diagramUriToFileName(diagram) + '.png' for entity in logicalStructure.entities for diagram in set(entity.diagrams)}
    print(diagramFilePaths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            diagram_file_paths=diagramFilePaths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional view', 'entity_structure': json.dumps(functionalStructure.toDict()), 'explanation': func_explanation, 'background': '#fff6f4'}, 
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Logical view', 'entity_structure': json.dumps(logicalStructure.toDict()), 'explanation': logic_explanation, 'background': '#f4f6ff'}, 
                                        'pattern': {'tab_id':'pattern_view_tab', 'tab_name': 'Pattern view', 'entity_structure': json.dumps(patternStructure.toDict()), 'explanation': pattern_explanation, 'background': '#f4fffc'}
                                        })
                            
@app.route('/q2/popup/diagram', methods=['POST'])
def q2_popup_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
    for figureUri in figureUriList:
        explanation[diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupImageDiagram.html', explanations=explanation)
                            
@app.route('/q2/popup/interactivediagram', methods=['POST'])
def q2_popup_interactive_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
    for figureUri in figureUriList:
        explanation[diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupInteractiveDiagram.html', explanations=explanation)