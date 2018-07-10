import json
from flask import Flask, request, send_from_directory, render_template, Markup
import explanationTemplatingEngine
import explanationStructureGenerator
import explanationHelper
import sparqlQueryManager
import ontologyStructureModel
import re
import os.path
import pickle

app = Flask(__name__, static_url_path="/static")
baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
explanationGenerator = explanationStructureGenerator.ExplanationGenerator()
explanationTemplates = explanationTemplatingEngine.ExplanationTemplates()    
queryManager = sparqlQueryManager.InformationRetriever()  


# ----------------------------------------------------------------------------
# Front page
# ----------------------------------------------------------------------------

@app.route('/index')
def index():
    return render_template('front-page-template.html')

# ----------------------------------------------------------------------------
# Explanation URLs
# ----------------------------------------------------------------------------

def saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths):
    with open('static/saved_data/'+ fileName + '.pkl', 'wb') as savedFile:
        pickle.dump(structure, savedFile, pickle.HIGHEST_PROTOCOL)
        print('Structure saved successfully')
        
        pickle.dump(explanation, savedFile, pickle.HIGHEST_PROTOCOL)
        print('Explanation saved successfully')

        pickle.dump(sideBardiagram_file_paths, savedFile, pickle.HIGHEST_PROTOCOL)
        print('Diagram file paths saved successfully')

def loadExplanation(fileName):
    print('fileFound')
    with open('static/saved_data/' + fileName + '.pkl', 'rb') as savedFile:
        structure = pickle.load(savedFile)
        explanation = pickle.load(savedFile)
        sideBardiagram_file_paths = pickle.load(savedFile)    
    return {'structure': structure, 'explanation': explanation, 'diagram_paths': sideBardiagram_file_paths}

@app.route('/q1/<feature>')
def q1(feature):
    fileName = 'q1_' + feature
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        structure = data['structure']
        explanation = data['explanation']
        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = explanationGenerator.getFeatureRole(baseUri + feature)
        explanation = explanationTemplates.generateFeatureRoleSummary(baseUri + feature, structure)
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)   
    
    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'feature_role_tab', 'tab_name': 'Feature role', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation, 'background': '#fff6f4'}})

@app.route('/q2/<feature>')
def q2(feature):
    fileName = 'q2_' + feature
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        
        structure = data['structure']
        overviewStructure = structure['overview']
        detailedStructure = structure['detailed']
        patternStructure = structure['pattern']

        explanation = data['explanation']
        overviewExplanation = explanation['overview']
        detailedExplanation = explanation['detailed']
        patternExplanation = explanation['pattern']

        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = {}
        explanation = {}
    
        overviewStructure = structure['overview'] = explanationGenerator.getOverviewFeatureToImplementationMap(baseUri + feature)
        overviewExplanation = explanation['overview'] = explanationTemplates.generateOverviewFeatureImplementationSummary(baseUri + feature, overviewStructure)

        detailedStructure = structure['detailed'] = explanationGenerator.getDetailedFeatureToImplementationMap(baseUri + feature)
        detailedExplanation = explanation['detailed'] = explanationTemplates.generateDetailedFeatureImplementationSummary(baseUri + feature, detailedStructure)
        implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]

        patternStructure = structure['pattern'] = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
        patternExplanation = explanation['pattern'] = explanationTemplates.generatePatternFeatureImplementationSummary(baseUri + feature, patternStructure)

        allEntities = []
        allEntities += detailedStructure.entities
        allEntities += overviewStructure.entities
        allEntities += patternStructure.entities

        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'overview': {'tab_id':'overview_view_tab', 'tab_name': 'Overview', 'entity_structure': json.dumps(overviewStructure.toDict()), 'explanation': overviewExplanation}, 
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Detailed view', 'entity_structure': json.dumps(detailedStructure.toDict()), 'explanation': detailedExplanation}, 
                                        'pattern': {'tab_id':'pattern_view_tab', 'tab_name': 'Pattern view', 'entity_structure': json.dumps(patternStructure.toDict()), 'explanation': patternExplanation}
                                        })

@app.route('/q3/<feature>')
def q3(feature):

    fileName = 'q3_' + feature
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        structure = data['structure']
        funcBehaviorStructure = structure['functional']
        devBehaviorStructure = structure['development']
        logBehaviorStructure = structure['logical']
        UIBehaviorStructure = structure['ui']

        explanation = data['explanation']
        func_explanation = explanation['functional']
        development_explanation = explanation['development']
        logical_explanation = explanation['logical']
        ui_explanation = explanation['ui']

        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = {}
        funcBehaviorStructure = structure['functional'] = explanationGenerator.getFunctionalBehaviorOfFeature(baseUri + feature)
        devBehaviorStructure = structure['development'] = explanationGenerator.getDevelopmentBehaviorOfFeature(baseUri + feature)
        logBehaviorStructure = structure['logical'] = explanationGenerator.getLogicalBehaviorOfFeature(baseUri + feature)
        UIBehaviorStructure = structure['ui'] = explanationGenerator.getUIBehaviorOfFeature(baseUri + feature)

        explanation = {}
        func_explanation = explanation['functional'] = explanationTemplates.generateFunctionalBehaviorSummary(baseUri + feature, funcBehaviorStructure)
        ui_explanation = explanation['ui'] = explanationTemplates.generateBehaviorSummary(baseUri + feature, UIBehaviorStructure, 'ui')
        development_explanation = explanation['development'] = explanationTemplates.generateBehaviorSummary(baseUri + feature, devBehaviorStructure, 'development')
        logical_explanation = explanation['logical'] = explanationTemplates.generateBehaviorSummary(baseUri + feature, logBehaviorStructure, 'logical')

        allEntities = funcBehaviorStructure.entities + devBehaviorStructure.entities + logBehaviorStructure.entities + UIBehaviorStructure.entities
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}
        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'Functional viewpoint', 'entity_structure': json.dumps(funcBehaviorStructure.toDict()), 'explanation': func_explanation},
                                        'logical': {'tab_id':'logical_view_tab', 'tab_name': 'Logical viewpoint', 'entity_structure': json.dumps(logBehaviorStructure.toDict()), 'explanation': logical_explanation},
                                        'development': {'tab_id':'development_view_tab', 'tab_name': 'Development viewpoint', 'entity_structure': json.dumps(devBehaviorStructure.toDict()), 'explanation': development_explanation},
                                        'ui': {'tab_id':'ui_view_tab', 'tab_name': 'UI viewpoint', 'entity_structure': json.dumps(UIBehaviorStructure.toDict()), 'explanation': ui_explanation}
                                        })

@app.route('/q4/<architecturalPattern>')
def q4(architecturalPattern):
    fileName = 'q4_' + architecturalPattern
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        architecturalStructure = data['structure']
        pattern_explanation = data['explanation']
        sideBardiagram_file_paths = data['diagram_paths']
    else:
        architecturalStructure = explanationGenerator.getRationaleOfArchitecture(baseUri + architecturalPattern)
        pattern_explanation = explanationTemplates.generateRationaleSummary(baseUri + architecturalPattern, architecturalStructure)
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in architecturalStructure.entities for diagram in set(entity.diagrams)}

        saveExplanation(fileName, architecturalStructure, pattern_explanation, sideBardiagram_file_paths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'rationale': {'tab_id':'rationale_view_tab', 'tab_name': 'Rationale of architectural pattern', 'entity_structure': json.dumps(architecturalStructure.toDict()), 'explanation': pattern_explanation, 'background': '#fff6f4'}})

@app.route('/q5/')
def q5():
    fileName = 'q5'
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        structure = data['structure']
        explanation = data['explanation']
        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = explanationGenerator.getFunctionalityOfSystem()
        explanation = explanationTemplates.generateSystemFunctionalitySummary(structure)
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}
        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'functional': {'tab_id':'functional_view_tab', 'tab_name': 'System functionality', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation, 'background': '#fff6f4'},
                                        })  
@app.route('/q6/')
def q6():
    fileName = 'q6'
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        structure = data['structure']
        overviewStructure = structure['overview']
        physicalStructure = structure['physical']
        developmentStructure = structure['development']
        
        explanation = data['explanation']
        overviewExplanation = explanation['overview']
        physicalExplanation = explanation['physical']
        developmentExplanation = explanation['development']

        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = {}
        overviewStructure = structure['overview'] = explanationGenerator.getOverviewPatternArchitecture()
        physicalStructure = structure['physical'] = explanationGenerator.getFullPhyPatternArchitecture()
        developmentStructure = structure['development'] = explanationGenerator.getFullDevPatternArchitecture()

        explanation = {}
        overviewExplanation = explanation['overview'] = explanationTemplates.generateSystemPatternsOverviewSummary(overviewStructure)
        physicalExplanation = explanation['physical'] = explanationTemplates.generateSystemPatternsDetailedSummary(physicalStructure, 'physical')
        developmentExplanation = explanation['development'] = explanationTemplates.generateSystemPatternsDetailedSummary(developmentStructure, 'development')

        allEntities = list(set(physicalStructure.entities + developmentStructure.entities + overviewStructure.entities))

        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}
        
        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)

    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'overview': {'tab_id':'overview_view_tab', 'tab_name': 'Overview', 'entity_structure': json.dumps(overviewStructure.toDict()), 'explanation': overviewExplanation},
                                          'physical': {'tab_id':'physical_view_tab', 'tab_name': 'Physical view', 'entity_structure': json.dumps(physicalStructure.toDict()), 'explanation': physicalExplanation},
                                          'development': {'tab_id':'development_view_tab', 'tab_name': 'Development view', 'entity_structure': json.dumps(developmentStructure.toDict()), 'explanation': developmentExplanation},
                                        })  
@app.route('/q7/<architecturalPattern>')
def q7(architecturalPattern):
    fileName = 'q7_' + architecturalPattern
    if os.path.isfile('static\\saved_data\\' + fileName + '.pkl'):
        data = loadExplanation(fileName)
        structure = data['structure']
        overviewStructure = structure['overview']
        devStructure = structure['development']
        phyStructure = structure['physical']
        
        explanation = data['explanation']
        overviewExplanation = explanation['overview']
        devExplanation = explanation['development']
        phyExplanation = explanation['physical']

        sideBardiagram_file_paths = data['diagram_paths']
    else:
        structure = {}
        patternEntity = ontologyStructureModel.Entity(baseUri + architecturalPattern)
        overviewStructure = structure['overview'] = explanationGenerator.getOverviewPatternArchitecture(baseUri + architecturalPattern)
        devStructure = structure['development'] = explanationGenerator.getFullDevPatternArchitecture(baseUri + architecturalPattern)
        phyStructure = structure['physical'] = explanationGenerator.getFullPhyPatternArchitecture(baseUri + architecturalPattern)

        explanation = {}
        overviewExplanation = explanation['overview'] = explanationTemplates.generateSystemPatternsOverviewSummary(overviewStructure, patternEntity)
        devExplanation = explanation['development'] = explanationTemplates.generateSpecificSystemPatternsDetailedSummary(devStructure, patternEntity)
        phyExplanation = explanation['physical'] = explanationTemplates.generateSpecificSystemPatternsDetailedSummary(phyStructure, patternEntity)

        allEntities = list(set(phyStructure.entities + devStructure.entities + overviewStructure.entities))
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}
    
        saveExplanation(fileName, structure, explanation, sideBardiagram_file_paths)
    
    return render_template('childtemplate.html', 
                            diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'overview': {'tab_id':'overview_view_tab', 'tab_name': 'Overview', 'entity_structure': json.dumps(overviewStructure.toDict()), 'explanation': overviewExplanation},
                                          'physical': {'tab_id':'physical_view_tab', 'tab_name': 'Physical view', 'entity_structure': json.dumps(phyStructure.toDict()), 'explanation': phyExplanation},
                                          'development': {'tab_id':'development_view_tab', 'tab_name': 'Development view', 'entity_structure': json.dumps(devStructure.toDict()), 'explanation': devExplanation},
                                        })  
# ----------------------------------------------------------------------------
# Popup URLs
# ----------------------------------------------------------------------------

# Shows diagram and entities found in diagram                    
@app.route('/popup/diagram', methods=['POST'])
def popup_diagram():
    figureUriList = request.form.getlist('figure[]')
    explanation = {}
 
    for figureUri in figureUriList:
        explanation[explanationHelper.diagramUriToFileName(figureUri)] = {'diagramFilePath': '/static/images/' + explanationHelper.diagramUriToFileName(figureUri) + '.png',
                                  'description': explanationTemplates.generatePopupFigureDescription(figureUri).toDict(),
                                  'newWindowPath': '/static/something.html'}

    return render_template('popupImageDiagram.html', explanations=explanation)

# What is the role of this feature?
@app.route('/popup/featureRole', methods=['POST'])
def popup_featureRole():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    structure = explanationGenerator.getFeatureRole(featureUri)
    allEntities = structure.entities

    side_bar_diagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    explanation = {}
    explanation['popup_feature_role'] = {'description': explanationTemplates.generateFeatureRoleSummary(featureUri, structure),
                                   'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', side_bar_diagram_file_paths=side_bar_diagram_file_paths, explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/featureRole', methods=['POST'])
def getFeatureRoleStructure():
    featureUri = request.form.get('feature', '')
    structure = {'popup_feature_role': explanationGenerator.getFeatureRole(featureUri).toDict()}
    return json.dumps(structure)

# What is the behavior of this feature?
@app.route('/popup/featureBehavior', methods=['POST'])
def popup_featureBehavior():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    funcStructure = explanationGenerator.getFunctionalBehaviorOfFeature(featureUri)
    logStructure = explanationGenerator.getLogicalBehaviorOfFeature(featureUri)
    devStructure = explanationGenerator.getDevelopmentBehaviorOfFeature(featureUri)
    uiStructure = explanationGenerator.getUIBehaviorOfFeature(featureUri)

    allEntities = funcStructure.entities + logStructure.entities + devStructure.entities + uiStructure.entities
    side_bar_diagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    explanation = {}

    explanation['popup_func_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, funcStructure, 'functional'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_log_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, logStructure, 'logical'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_dev_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, devStructure, 'development'),
                                                'newWindowPath': newWindowPath}
    explanation['popup_ui_feature_behavior'] = {'description': explanationTemplates.generateBehaviorSummary(featureUri, uiStructure, 'ui'),
                                                'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', side_bar_diagram_file_paths=side_bar_diagram_file_paths, explanations=explanation, newWindowPath=newWindowPath)

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

# How is this feature implemented?
@app.route('/popup/featureImplementation', methods=['POST'])
def popup_featureImplementation():
    featureUri = request.form.get('feature', '')
    newWindowPath = request.form.get('newWindowPath', '')

    overviewStructure = explanationGenerator.getOverviewFeatureToImplementationMap(featureUri)
    overviewExplanation = explanationTemplates.generateOverviewFeatureImplementationSummary(featureUri, overviewStructure)

    detailedStructure = explanationGenerator.getDetailedFeatureToImplementationMap(featureUri)
    detailedExplanation = explanationTemplates.generateDetailedFeatureImplementationSummary(featureUri, detailedStructure)
    
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]

    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)
    patternExplanation = explanationTemplates.generatePatternFeatureImplementationSummary(featureUri, patternStructure)

    allEntities = overviewStructure.entities + detailedStructure.entities + patternStructure.entities
    side_bar_diagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    explanation = {}

    explanation['popup_overview_feature_implementation'] = {'description': overviewExplanation,
                                                'newWindowPath': newWindowPath}
    explanation['popup_detailed_feature_implementation'] = {'description': detailedExplanation,
                                                'newWindowPath': newWindowPath}
    explanation['popup_pattern_implementation'] = {'description': patternExplanation,
                                                'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', side_bar_diagram_file_paths=side_bar_diagram_file_paths, explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/featureImplementation', methods=['POST'])
def getFeatureImplementation():
    featureUri = request.form.get('feature', '')

    overviewStructure = explanationGenerator.getOverviewFeatureToImplementationMap(featureUri)
    detailedStructure = explanationGenerator.getDetailedFeatureToImplementationMap(featureUri)
    implementationEntityUris = [implementation.uri for implementation in list(filter(lambda x: baseUri + 'ImplementationClass' in x.supertypes, detailedStructure.entities))]
    patternStructure = explanationGenerator.getImplementationToArchitecturalPatternMap(implementationEntityUris)

    structures = {'popup_overview_feature_implementation': overviewStructure.toDict(),
                  'popup_detailed_feature_implementation': detailedStructure.toDict(),
                  'popup_pattern_implementation': patternStructure.toDict()}
    return json.dumps(structures)

# What is the rationale of this architectural pattern?
@app.route('/popup/patternRationale', methods=['POST'])
def popup_patternRationale():
    patternUri = request.form.get('pattern', '')
    newWindowPath = request.form.get('newWindowPath', '')

    structure = explanationGenerator.getRationaleOfArchitecture(patternUri)

    allEntities = structure.entities
    side_bar_diagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    explanation = {}
    explanation['popup_pattern_rationale'] = {'description': explanationTemplates.generateRationaleSummary(patternUri, structure),
                                   'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', side_bar_diagram_file_paths=side_bar_diagram_file_paths, explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/patternRationale', methods=['POST'])
def getPatternRationale():
    patternUri = request.form.get('pattern', '')
    structure = {'popup_pattern_rationale': explanationGenerator.getRationaleOfArchitecture(patternUri).toDict()}
    return json.dumps(structure)

# What is the rationale of this architectural pattern?
@app.route('/popup/patternImplementation', methods=['POST'])
def popup_patternImplementation():
    patternUri = request.form.get('pattern', '')
    newWindowPath = request.form.get('newWindowPath', '')
    pattern = ontologyStructureModel.Entity(patternUri)

    overviewStructure = explanationGenerator.getOverviewPatternArchitecture(patternUri)
    physicalStructure = explanationGenerator.getFullPhyPatternArchitecture(patternUri)
    developmentStructure = explanationGenerator.getFullDevPatternArchitecture(patternUri)

    allEntities = overviewStructure.entities + physicalStructure.entities + developmentStructure.entities
    side_bar_diagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in allEntities for diagram in set(entity.diagrams)}

    explanation = {}
    explanation['popup_overview_pattern'] = {'description': explanationTemplates.generateSystemPatternsOverviewSummary(overviewStructure, pattern),
                                   'newWindowPath': newWindowPath}
    explanation['popup_physical_pattern'] = {'description': explanationTemplates.generateSpecificSystemPatternsDetailedSummary(physicalStructure, pattern),
                                   'newWindowPath': newWindowPath}
    explanation['popup_development_pattern'] = {'description': explanationTemplates.generateSpecificSystemPatternsDetailedSummary(developmentStructure, pattern),
                                   'newWindowPath': newWindowPath}

    return render_template('popupInteractiveDiagram.html', side_bar_diagram_file_paths=side_bar_diagram_file_paths, explanations=explanation, newWindowPath=newWindowPath)

@app.route('/structure/patternImplementation', methods=['POST'])
def getPatternImplementation():
    patternUri = request.form.get('pattern', '')
    structure = {'popup_overview_pattern': explanationGenerator.getOverviewPatternArchitecture(patternUri).toDict(),
                 'popup_physical_pattern': explanationGenerator.getFullPhyPatternArchitecture(patternUri).toDict(),
                 'popup_development_pattern': explanationGenerator.getFullDevPatternArchitecture(patternUri).toDict()
                 }
    return json.dumps(structure)

# ----------------------------------------------------------------------------
# Loading and saving metamodel graph
# ----------------------------------------------------------------------------

@app.route('/loadgraph')
def loadOntology():
    graphData = ''
    with open('static/ontologyGraph.txt', 'r') as f:
        graphData = f.read()

    return graphData

@app.route('/savegraph', methods=['POST'])
def saveOntology():
    graphData = request.form.get('graphData')
    with open('static/ontologyGraph.txt', 'w+') as f:
        f.write(graphData)
    return 'success!'

# ----------------------------------------------------------------------------
# Helper URLs
# ----------------------------------------------------------------------------

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

@app.route('/getTypeOptionDiv', methods=['POST'])
def getTypeOptionDiv():
    entityType = request.form.get('entityType', '')

    if (entityType):
        entityType = json.loads(entityType)
        for eo in entityType['entityOptions'] :
            eo['uri'] = explanationHelper.getNameFromUri(eo['uri'])
            eo['type'] = explanationHelper.getNameFromUri(queryManager.getTypeOfIndividual(baseUri + eo['uri']))
        
        return render_template('typeOptionDiv.html', type=entityType)
    return ''

@app.route('/getManualExplanation', methods=['POST'])
def getManualExplanation():
    types = request.form.getlist('types[]')
    relations = request.form.getlist('relations[]')

    parsedTypes = [json.loads(entityType) for entityType in types]
    parsedRelations = [json.loads(relation) for relation in relations]

    if(parsedTypes):
        structure = explanationGenerator.getManualExplanation(parsedTypes, parsedRelations)
        explanation = explanationTemplates.generateGeneralManualExplanation(structure)
        sideBardiagram_file_paths = {diagram: 'static/images/' + explanationHelper.diagramUriToFileName(diagram) + '.png' for entity in structure.entities for diagram in set(entity.diagrams)}

        return render_template('childtemplate.html', diagram_path='static/ClusteringGraph.js', 
                            side_bar_diagram_file_paths=sideBardiagram_file_paths,
                            entityData = {'overview': {'tab_id': 'overview_view_tab', 'tab_name': 'Overview', 'entity_structure': json.dumps(structure.toDict()), 'explanation': explanation } } )  
    return ''

@app.route('/manualExplanationComposer')
def manualExplanationComposer():
    return render_template('ExplanationComposer.html')