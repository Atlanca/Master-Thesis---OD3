import json
from flask import Flask, request, send_from_directory, render_template, Markup
import explanationTemplatingEngine
import explanationStructureGenerator
import explanationHelper
import sparqlQueryManager
import ontologyStructureModel
import re

app = Flask(__name__, static_url_path="/static")
baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
explanationGenerator = explanationStructureGenerator.ExplanationGenerator()
explanationTemplates = explanationTemplatingEngine.ExplanationTemplates()    
queryManager = sparqlQueryManager.InformationRetriever()  


@app.route('/index/<pattern>')
def index(pattern):
    # print(explanationGenerator.getDev(baseUri + 'thin_client_MVC'))
   
    functionalStructure = explanationGenerator.getDev(baseUri + pattern)
    func_explanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(baseUri + pattern, functionalStructure)

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in functionalStructure.entities for diagram in set(entity.diagrams)}


    return render_template('childtemplate.html', 
                            diagram_path='static/FeatureRoleGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional view', 'entity_structure': json.dumps(functionalStructure.toDict()), 'explanation': func_explanation, 'background': '#fff6f4'}})

@app.route('/query/getrelations', methods=['POST'])
def getRelations():
    subject = request.form.get('subjectUri', '')
    relationType = request.form.get('relationUri', '')
    objectType = request.form.get('objectTypeUri', '')

    if subject:
        relations = [{'relationUri': pair[0], 'entity': ontologyStructureModel.Entity(pair[1]).toDict()} for pair in queryManager.getRelations(subject, relationType, objectType)]
        return json.dumps(relations)
    return ''

@app.route('/query/getobjectpropertyrelations', methods=['POST'])
def getObjectPropertyRelations():
    subject = request.form.get('subjectUri', '')
    if subject:
        relations = [{'relationUri': pair[0], 'entityUri': pair[1]} for pair in queryManager.getObjectPropertyRelations(subject)]
        return json.dumps(relations)
    return ''

@app.route('/query/getentity', methods=['POST'])
def getEntity():
    entity = request.form.get('entityUri', '')

    if entity:
        entityDict = ontologyStructureModel.Entity(entity).toDict()
        return json.dumps(entityDict)
    return ''

@app.route('/query/findpathto', methods=['POST'])
def findPathTo():
    startType = request.form.get('startType', '')
    targetType = request.form.get('targetType', '')
    metaModel = explanationGenerator.loadMetaModel()
    if startType and targetType:
        paths = explanationGenerator.getMetaModelPath(metaModel, startType, targetType)
        return json.dumps(paths)
    return ''

@app.route('/getOntology')
def getOntology():
    relations = queryManager.getAllTypeRelations()
    types = queryManager.getAllOntologyTypes()

    return json.dumps({'types': types, 'relations': relations})

@app.route('/getDirectSuperClass', methods=['POST'])
def getDirectSuperClass():
    klass = request.form.get('type', '')
    if klass:
        return json.dumps(queryManager.getDirectSuperClass(klass))
    else:
        return ''

@app.route('/getEntitiesByPath', methods=['POST'])
def getEntitiesByPath():
   
    # startEntity = request.form.get('startEntity', '')
    # print(startEntity)
    startEntity = baseUri + 'Cart'
    print(request.form)
    startType = request.form.get('startType', '')
    relations = request.form.get('relations', '')
    relations = json.loads(relations)
    print(relations)

    startEntities = queryManager.getIndividualsByType(startType)
    
    paths = []
    
    if startEntities and relations:
        for startEntity in startEntities:
            paths += explanationGenerator.getEntityPaths(startEntity, relations)
    
    if paths:
        with open('path.js', 'w') as f:
            f.write('paths =' + json.dumps(paths))
        return json.dumps(paths)
    return ''

    # startEntity = baseUri + 'purchase_products'
    # relations = [{'source': baseUri + 'Feature', 'property': baseUri + 'compriseOf', 'target': baseUri + 'Requirement'},
    #             {'source': baseUri + 'FunctionalRequirement', 'property': baseUri + 'partOf', 'target': baseUri + 'UseCase'},
    #             {'source': baseUri + 'Feature', 'property': baseUri + 'modeledIn', 'target': baseUri + 'Diagram'}]

@app.route('/getDirectSuperClassParentMap', methods=['POST'])
def getDirectSuperClassParentMap():
    classes = request.form.getlist('types[]')
    if classes:
        parentMap = {}
        for c in classes:
            parent = queryManager.getDirectSuperClass(c)
            parentMap[explanationHelper.getNameFromUri(c)] = {'child': c, 'parent': parent}
        return json.dumps(parentMap)
    return ''


@app.route('/q1/<feature>')
def q1(feature):
    structure = explanationGenerator.getFeatureRole(baseUri + feature)
    explanation = explanationTemplates.generateFeatureRoleSummary(baseUri + feature, structure)

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
    return render_template('childtemplate.html', 
                            diagram_path='static/FeatureRoleGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'feature_role_tab', 'tab_name': 'Feature role', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation, 'background': '#fff6f4'}})

@app.route('/q2/<feature>')
def q2(feature):

    functionalStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(baseUri + feature)
    func_explanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(baseUri + feature, functionalStructure)

    logicalStructure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + feature)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, logicalStructure.entities))]
    logic_explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + feature, logicalStructure)

    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    pattern_explanation = explanationTemplates.generatePatternFeatureImplementationSummary(baseUri + feature, patternStructure)

    allEntities = []
    allEntities += logicalStructure.entities
    allEntities += functionalStructure.entities
    allEntities += patternStructure.entities

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional view', 'entity_structure': json.dumps(functionalStructure.toDict()), 'explanation': func_explanation, 'background': '#fff6f4'}, 
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Logical view', 'entity_structure': json.dumps(logicalStructure.toDict()), 'explanation': logic_explanation, 'background': '#f4f6ff'}, 
                                        'pattern': {'tab_id':'pattern_view_tab', 'tab_name': 'Pattern view', 'entity_structure': json.dumps(patternStructure.toDict()), 'explanation': pattern_explanation, 'background': '#f4fffc'}
                                        })
                            
@app.route('/popup/diagram', methods=['POST'])
def q2_popup_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
    for figureUri in figureUriList:
        explanation[explanationHelper.diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + explanationHelper.diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupImageDiagram.html', explanations=explanation)
                            
@app.route('/popup/interactivediagram', methods=['POST'])
def q2_popup_interactive_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
    for figureUri in figureUriList:
        explanation[explanationHelper.diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + explanationHelper.diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupInteractiveDiagram.html', explanations=explanation)

@app.route('/q4/<architecturalPattern>')
def q4(architecturalPattern):
    architecturalStructure = explanationGenerator.getRationaleOfArchitecture(baseUri + architecturalPattern)
    func_explanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(baseUri + architecturalPattern, architecturalStructure)

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in architecturalStructure.entities for diagram in set(entity.diagrams)}


    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional view', 'entity_structure': json.dumps(architecturalStructure.toDict()), 'explanation': func_explanation, 'background': '#fff6f4'}})

@app.route('/savegraph', methods=['POST'])
def saveOntology():
    graphData = request.form.get('graphData')
    with open('static/ontologyGraph.txt', 'w') as f:
        f.write(graphData)
    return 'success!'

@app.route('/loadgraph')
def loadOntology():
    graphData = ''
    with open('static/ontologyGraph.txt', 'r') as f:
        graphData = f.read()

    return graphData