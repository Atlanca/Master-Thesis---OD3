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


@app.route('/index')
def index():
    return render_template('front-page-template.html')

@app.route('/query/getentitiesbytype', methods=['POST'])
def getEntitiesByType():
    typeUri = request.form.get('typeUri', '')

    if typeUri:
        return json.dumps(queryManager.getIndividualsByType(typeUri))
    return ''

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
    startEntity = baseUri + 'Cart'
    startType = request.form.get('startType', '')
    relations = request.form.get('relations', '')
    relations = json.loads(relations)

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
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'feature_role_tab', 'tab_name': 'Feature role', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation, 'background': '#fff6f4'}})

@app.route('/q2/<feature>')
def q2(feature):

    overviewStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(baseUri + feature)
    overview_explanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(baseUri + feature, overviewStructure)

    detailedStructure = explanationGenerator.getLogicalFeatureToImplementationMap(baseUri + feature)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]
    detailed_explanation = explanationTemplates.generateLogicalFeatureImplementationSummary(baseUri + feature, detailedStructure)

    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    pattern_explanation = explanationTemplates.generatePatternFeatureImplementationSummary(baseUri + feature, patternStructure)

    allEntities = []
    allEntities += detailedStructure.entities
    allEntities += overviewStructure.entities
    allEntities += patternStructure.entities

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'overview': {'tab_id':'overview_view_tab', 'tab_name': 'Overview', 'entity_structure': json.dumps(overviewStructure.toDict()), 'explanation': overview_explanation}, 
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Detailed view', 'entity_structure': json.dumps(detailedStructure.toDict()), 'explanation': detailed_explanation}, 
                                        'pattern': {'tab_id':'pattern_view_tab', 'tab_name': 'Pattern view', 'entity_structure': json.dumps(patternStructure.toDict()), 'explanation': pattern_explanation}
                                        })

@app.route('/q3/<feature>')
def q3(feature):
    funcBehaviorStructure = explanationGenerator.getFunctionalBehaviorOfFeature(baseUri + feature)
    devBehaviorStructure = explanationGenerator.getDevelopmentBehaviorOfFeature(baseUri + feature)
    logBehaviorStructure = explanationGenerator.getLogicalBehaviorOfFeature(baseUri + feature)
    UIBehaviorStructure = explanationGenerator.getUIBehaviorOfFeature(baseUri + feature)

    func_explanation = explanationTemplates.generateFunctionalBehaviorSummary(baseUri + feature, funcBehaviorStructure)
    ui_explanation = explanationTemplates.generateBehaviorSummary(baseUri + feature, UIBehaviorStructure, 'ui')
    development_explanation = explanationTemplates.generateBehaviorSummary(baseUri + feature, devBehaviorStructure, 'development')
    logical_explanation = explanationTemplates.generateBehaviorSummary(baseUri + feature, logBehaviorStructure, 'logical')

    allEntities = funcBehaviorStructure.entities + devBehaviorStructure.entities + logBehaviorStructure.entities + UIBehaviorStructure.entities
    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}


    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional viewpoint', 'entity_structure': json.dumps(funcBehaviorStructure.toDict()), 'explanation': func_explanation},
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Logical viewpoint', 'entity_structure': json.dumps(logBehaviorStructure.toDict()), 'explanation': logical_explanation},
                                        'development': {'tab_id':'development_view_tab', 'tab_name': 'Development viewpoint', 'entity_structure': json.dumps(devBehaviorStructure.toDict()), 'explanation': development_explanation},
                                        'ui': {'tab_id':'ui_view_tab', 'tab_name': 'UI viewpoint', 'entity_structure': json.dumps(UIBehaviorStructure.toDict()), 'explanation': ui_explanation}
                                        })
@app.route('/q5/')
def q5():
    structure = explanationGenerator.getFunctionalityOfSystem()
    explanation = explanationTemplates.generateSystemFunctionalitySummary(structure)
    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'System functionality', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation, 'background': '#fff6f4'},
                                        })  

@app.route('/q4/<architecturalPattern>')
def q4(architecturalPattern):
    architecturalStructure = explanationGenerator.getRationaleOfArchitecture(baseUri + architecturalPattern)
    pattern_explanation = explanationTemplates.generateRationaleSummary(baseUri + architecturalPattern, architecturalStructure)

    sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in architecturalStructure.entities for diagram in set(entity.diagrams)}


    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'rationale': {'tab_id':'rationale_view_tab', 'tab_name': 'Rationale of architectural pattern', 'entity_structure': json.dumps(architecturalStructure.toDict()), 'explanation': pattern_explanation, 'background': '#fff6f4'}})

                            
@app.route('/popup/diagram', methods=['POST'])
def popup_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
    for figureUri in figureUriList:
        explanation[explanationHelper.diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + explanationHelper.diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupImageDiagram.html', explanations=explanation)

@app.route('/popup/featureRole', methods=['POST'])
def popup_featureRole():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    structure = explanationGenerator.getFeatureRole(featureUri)
    explanation = {}
    explanation['popup_feature_role'] = {'description': explanationTemplates.generateFeatureRoleSummary(featureUri, structure),
                                   'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/featureRole', methods=['POST'])
def getFeatureRoleStructure():
    featureUri = request.form.get('feature', '')
    structure = {'popup_feature_role': explanationGenerator.getFeatureRole(featureUri).toDict()}
    return json.dumps(structure)

@app.route('/popup/featureBehavior', methods=['POST'])
def popup_featureBehavior():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    funcStructure = explanationGenerator.getFunctionalBehaviorOfFeature(featureUri)
    logStructure = explanationGenerator.getLogicalBehaviorOfFeature(featureUri)
    devStructure = explanationGenerator.getDevelopmentBehaviorOfFeature(featureUri)
    uiStructure = explanationGenerator.getUIBehaviorOfFeature(featureUri)

    explanation = {}

    explanation['popup_func_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, funcStructure, 'functional'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_log_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, logStructure, 'logical'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_dev_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, devStructure, 'development'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_ui_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, uiStructure, 'ui'),
                                                'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/featureBehavior', methods=['POST'])
def getFeatureBehavior():
    featureUri = request.form.get('feature', '')

    funcStructure = explanationGenerator.getFunctionalBehaviorOfFeature(featureUri)
    devStructure = explanationGenerator.getDevelopmentBehaviorOfFeature(featureUri)
    logStructure = explanationGenerator.getLogicalBehaviorOfFeature(featureUri)
    uiStructure = explanationGenerator.getUIBehaviorOfFeature(featureUri)

    structures = {'popup_func_feature_behavior': funcStructure.toDict(),
                  'popup_log_feature_behavior': logStructure.toDict(),
                  'popup_dev_feature_behavior': devStructure.toDict(),
                  'popup_ui_feature_behavior': uiStructure.toDict()}
    return json.dumps(structures)

@app.route('/popup/featureImplementation', methods=['POST'])
def popup_featureImplementation():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    overviewStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(featureUri)
    overviewExplanation = explanationTemplates.generateFunctionalFeatureImplementationSummary(featureUri, overviewStructure)

    detailedStructure = explanationGenerator.getLogicalFeatureToImplementationMap(featureUri)
    detailedExplanation = explanationTemplates.generateLogicalFeatureImplementationSummary(featureUri, detailedStructure)
    
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]

    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    patternExplanation = explanationTemplates.generatePatternFeatureImplementationSummary(featureUri, patternStructure)

    explanation = {}

    explanation['popup_overview_feature_implementation'] = {'description': overviewExplanation,
                                                'newWindowPath': newWindowPath}
    explanation['popup_detailed_feature_implementation'] = {'description': detailedExplanation,
                                                'newWindowPath': newWindowPath}
    explanation['popup_pattern_implementation'] = {'description': patternExplanation,
                                                'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/featureImplementation', methods=['POST'])
def getFeatureImplementation():
    featureUri = request.form.get('feature', '')

    overviewStructure = explanationGenerator.getFunctionalFeatureToImplementationMap(featureUri)
    detailedStructure = explanationGenerator.getLogicalFeatureToImplementationMap(featureUri)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]
    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)

    structures = {'popup_overview_feature_implementation': overviewStructure.toDict(),
                  'popup_detailed_feature_implementation': detailedStructure.toDict(),
                  'popup_pattern_implementation': patternStructure.toDict()}
    return json.dumps(structures)

@app.route('/savegraph', methods=['POST'])
def saveOntology():
    graphData = request.form.get('graphData')
    with open('static/ontologyGraph.txt', 'w') as f:
        f.write(graphData)
    return 'success!'

@app.route('/popup/patternRationale', methods=['POST'])
def popup_patternRationale():
    patternUri = request.form.get('pattern', '')
    newWindowPath = request.form.get('newWindowPath', '')

    structure = explanationGenerator.getRationaleOfArchitecture(patternUri)
    explanation = {}
    explanation['popup_pattern_rationale'] = {'description': explanationTemplates.generateRationaleSummary(patternUri, structure),
                                   'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/patternRationale', methods=['POST'])
def getPatternRationale():
    patternUri = request.form.get('pattern', '')
    structure = {'popup_pattern_rationale': explanationGenerator.getRationaleOfArchitecture(patternUri).toDict()}
    return json.dumps(structure)

@app.route('/loadgraph')
def loadOntology():
    graphData = ''
    with open('static/ontologyGraph.txt', 'r') as f:
        graphData = f.read()

    return graphData