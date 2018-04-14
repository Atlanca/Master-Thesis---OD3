import json

from flask import Flask, request, send_from_directory

import httpQuery
import yattagTest

app = Flask(__name__, static_url_path="/static")
builder = yattagTest.htmlBuilder()
ir = httpQuery.InformationRetriever('')

EXPLANATION_TYPES = ['explainFeatureRole', 
                     'explainFeatureImplementation', 
                     'relatedImplementationClasses', 
                     'relationsByEncapsulatingComponent', 
                     'relationsByArchitecturalRole',
                     'relationsByDesignOption'
                    ]


@app.route('/index')
def index():
    return builder.main()
    
@app.route('/getExplanationView', methods=['POST'])
def getExplanationView():
    explanationType = request.form.getlist('explanationType')
    inputData = request.form.getlist('inputData')
    title = request.form.getlist('title')
    explanationStructure = getExplanationStructure(explanationType[0], inputData)

    htmlString = ''

    if(explanationType[0] == EXPLANATION_TYPES[0]):
        htmlString = builder.featureRoleExplanation(explanationType[0], explanationType[0] + "Data", explanationStructure)
    else:
        htmlString = builder.relatedImplementationClassesExplanation(explanationType[0], explanationType[0] + "Data", explanationStructure, title[0])
    
    return htmlString

@app.route('/getSideDescription/<individual>')
def getSideDescription(individual):
    return builder.createSideDescription(individual)

@app.route('/explainFeatureRole/<feature>')
def explainFeatureRole(feature):
    returnVal = None
    try:
        returnVal = ir.explainFeatureRole(feature)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString
    
@app.route('/explainFeatureImplementation/<feature>')
def explainFeatureImplementation(feature):
    returnVal = None
    try:
        returnVal = ir.explainFeatureImplementation(feature)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relatedImplementationClasses/<feature>')
def relatedImplementationClasses(feature):
    returnVal = None
    try:
        returnVal = ir.relatedImplementationClasses(feature)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByFeature/<architectureFragment>')
def relationsByFeature(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByFeature(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByEncapsulatingComponent/<architectureFragment>')
def relationsByEncapsulatingComponent(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByEncapsulatingComponent(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByArchitecturalRole/<architectureFragment>')
def relationsByArchitecturalRole(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByArchitecturalRole(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByNonFunctionalRequirement/<architectureFragment>')
def relationsByNonFunctionalRequirement(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByNonFunctionalRequirement(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByFunctionalRequirement/<architectureFragment>')
def relationsByFunctionalRequirement(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByFunctionalRequirement(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

#Something is wrong!
@app.route('/relationsByDesignOption/<architectureFragment>')
def relationsByDesignOption(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByDesignOption(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/relationsByDiagram/<architectureFragment>')
def relationsByDiagram(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.relationsByDiagram(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/findIntersectingFeatures/', methods=['POST'])
def findIntersectingFeatures():
    returnVal = None
    architectureFragments = request.form.getlist('architectureFragment')
    try:
        returnVal = ir.findIntersectingFeatures(architectureFragments)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)
    print('Served this data: ' + returnString)
    return returnString 

@app.route('/findIntersectingFunctionalRequirements/)', methods=['POST'])
def findIntersectingFunctionalRequirements():
    returnVal = None
    architectureFragments = request.form.getlist('architectureFragment')
    try:
        returnVal = ir.findIntersectingFunctionalRequirements(architectureFragments)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)     
    return returnString 

@app.route('/findIntersectingNonFunctionalRequirements/', methods=['POST'])
def findIntersectingNonFunctionalRequirements():
    returnVal = None
    architectureFragments = request.form.getlist('architectureFragment')
    try:
        returnVal = ir.findIntersectingNonFunctionalRequirements(architectureFragments)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)     
    return returnString 

# From any architectural fragment
@app.route('/getArchitecture/<architectureFragment>')
def getArchitecture(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.getArchitecture(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)     
    return returnString 

@app.route('/locationInArchitecture/<architectureFragment>')
def locationInArchitecture(architectureFragment):
    returnVal = None
    try:
        returnVal = ir.locationInArchitecture(architectureFragment)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)    
    return returnString 

@app.route('/rationaleOfArchitecture/<architecture>')
def rationaleOfArchitecture(architecture):
    returnVal = None
    try:
        returnVal = ir.rationaleOfArchitecture(architecture)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)     
    return returnString 

@app.route('/getAllTechnologies/)')
def getAllTechnologies():
    returnVal = None
    try:
        returnVal = ir.getAllTechnologies()
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)    
    return returnString 

@app.route('/getRationaleOfTechnology/<technology>')
def getRationaleOfTechnology(technology):
    returnVal = None
    try:
        returnVal = ir.getRationaleOfTechnology(technology)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)    
    return returnString 

@app.route('/getDescriptionOfTechnology/<technology>')
def getDescriptionOfTechnology(technology):
    returnVal = None
    try:
        returnVal = ir.getDescriptionOfTechnology(technology)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)    
    return returnString 

@app.route('/getArchitectureByTechnology/<technology>')
def getArchitectureByTechnology(technology):
    returnVal = None
    try:
        returnVal = ir.getArchitectureByTechnology(technology)
    except BaseException:
        print("No such feature")

    returnString = json.dumps(returnVal)     
    print('Served this data: ' + returnString)     
    return returnString 

# HELPERS
def getExplanationStructure(explanationType, inputData):
    explanationStructure = None
    inputData = inputData[0]

    if explanationType == EXPLANATION_TYPES[0]:
        try:
            explanationStructure = ir.explainFeatureRole(inputData)
        except BaseException:
            print("No such feature")

    elif explanationType == EXPLANATION_TYPES[1]:
        try:
            explanationStructure = ir.explainFeatureImplementation(inputData)
        except BaseException:
            print("No such feature")

    elif explanationType == EXPLANATION_TYPES[2]:
        try:
            explanationStructure = ir.relatedImplementationClasses(inputData)
        except BaseException:
            print("No such feature")

    elif explanationType == EXPLANATION_TYPES[3]:
        try:
            explanationStructure = ir.relationsByEncapsulatingComponent(inputData)
        except BaseException:
            print("No such feature")

    elif explanationType == EXPLANATION_TYPES[4]:
        try:
            explanationStructure = ir.relationsByArchitecturalRole(inputData)
        except BaseException:
            print("No such feature")

    elif explanationType == EXPLANATION_TYPES[5]:
        try:
            explanationStructure = ir.relationsByDesignOption(inputData)
        except BaseException:
            print("No such feature")
    
    return explanationStructure
