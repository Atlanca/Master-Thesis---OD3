
var ONTOLOGY_COLORS = {'Feature': '#af2d2d', 'Requirement': '#cc6a51', 'FunctionalRequirement': '#eeb574', 
                        'NonFunctionalRequirement': '#d17f40',
                        'UseCase': '#ce9d58', 'UserStory': '#b9ad5b', 'Stakeholder': '#e2d15d', 
                        'Figure': '#92b177', 'Diagram': '#86af38', 'Sketch': '#c6d65e',
                        'ArchitecturalPattern': '#79d6e3', 'Role': '#64cfa3', 'ArchitectureFragment': '#6bb496', 
                        'UI': '#73669b', 'Logical': '#378aba', 'Development': '#308f91',
                        'Physical': '#699677', 'DesignOption': '#b476c4', 'Technology': '#e93b99', 'Argument': '#ffaece', 
                        'Constraint': '#ffaece', 'Assumption': 'ffaece',
                        'Implementation': 'gray', 'ImplementationClass': 'lightgray',
                        'ArchitectureLayer': '#6bb496', 'RequirementLayer': '#af2d2d',
                        'RationaleLayer': '#b476c4', 'ImplementationLayer': 'gray', 'FigureLayer': '#92b177',
                        'UILayer': '#73669b', 'LogicalLayer': '#378aba', 'DevelopmentLayer': '#308f91',
                        'PhysicalLayer': '#699677'}

var views = ['Development', 'UI', 'Logical', 'Physical'] 
var ontologyCategories = {'ArchitectureLayer':   ['Role', 'ArchitecturalPattern'], 
                        'DevelopmentLayer': ['Development'],
                        'PhysicalLayer': ['Physical'],
                        'LogicalLayer': ['Logical'],
                        'UILayer': ['UI'],
                        'RequirementLayer':      ['Requirement', 'UserStory', 'UseCase', 'Feature', 'NonFunctionalReqCategory', 'Stakeholder', 'Testcases'], 
                        'RationaleLayer':        ['DesignOption', 'Technology', 'Argument', 'Constraint', 'Assumption'], 
                        'ImplementationLayer':   ['ImplementationClass', 'ClassRoleStereotype'],
                        'FigureLayer':           ['Figure']}

var reverseOntologyCategories = {}

Object.keys(ontologyCategories).forEach(function(key){
    ontologyCategories[key].forEach(function(type){
        reverseOntologyCategories[type] = key
    })
})

function getNameOfUri(string){
    string = string.replace(/.+#/, '')
    string = string.replace(/\./g, '_')
    return string
}

var cells = []
var graph = new joint.dia.Graph;
var paper = new joint.dia.Paper({
  el: $('#myholder'),
  width: '100%',
  height: '100%',
  gridSize: 15,
  model: graph
});

joint.dia.Element.define('standard.Rectangle', {
    attrs: {
        body: {
            refWidth: '100%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000000',
            fill: '#FFFFFF',
        },
        label: {
            textVerticalAnchor: 'middle',
            textAnchor: 'middle',
            refX: '50%',
            refY: '50%',
            fill: '#333333'
        }
    }
}, {
    markup: [{
        tagName: 'rect',
        selector: 'body',
    }, {
        tagName: 'text',
        selector: 'label'
    }]
});

rectMap = {}

baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'


function getOppositeLink(source, target){
    var returnVal = null
    var allLinks = graph.getLinks()
    allLinks.forEach(function(link){
        if (link.attributes.source.id == target.id && link.attributes.target.id == source.id) {
            returnVal = link
        } 
    })

    return returnVal
}

// Assumes that there can be only a single parent for each
// type
$.get('http://localhost:5000/getOntology', function(data, status){
    var ontology = JSON.parse(data)
    var types = ontology.types
    var relations = ontology.relations

    $.post('http://localhost:5000/getDirectSuperClassParentMap', {'types[]': types}, function(data, status){
        parentMap = JSON.parse(data)

        types.forEach(function(type){

            var color
            var superTypes = getSuperTypes(parentMap, type)

            if (reverseOntologyCategories[getNameOfUri(type)]){
                color = ONTOLOGY_COLORS[reverseOntologyCategories[getNameOfUri(type)]]
                hslColor = tinycolor(color).toHsl()
                hslColor.l = 0.8
                color = tinycolor(hslColor).toHexString()
            } else {
                superTypes.forEach(function(superType){
                    superTypeFound = reverseOntologyCategories[getNameOfUri(superType)]

                    if(superTypeFound){
                        color = ONTOLOGY_COLORS[superTypeFound]
                        hslColor = tinycolor(color).toHsl()
                        hslColor.l = 0.8
                        color = tinycolor(hslColor).toHexString()
                    }
                })
            }

            var rect = new joint.shapes.standard.Rectangle();
            rect.position(90, 30);
            rect.attr({
                label: {
                    fontSize: 30,
                    text: getNameOfUri(type),
                },
                body:{
                    fill: color,
                    class: 'metaType',
                    'data-uri': type
                } 
            });
            minwidth = 90
            width = parseInt(getNameOfUri(type).length) * 22
            
            if(minwidth > width){
                width = minwidth
            }

            rect.resize(width, 40);
            rect.addTo(graph);
            rectMap[getNameOfUri(type)] = rect
        })

        var min = restructureRelations(types, relations, 'min', parentMap)
        var exactly = restructureRelations(types, relations, 'exactly', parentMap)
        var some = restructureRelations(types, relations, 'some', parentMap)

        types.forEach(function(type){
            if(getNameOfUri(parentMap[getNameOfUri(type)].parent)){
                var link = new joint.shapes.standard.Link()
                link.prop('linkType', 'inheritance')
                link.source(rectMap[getNameOfUri(type)])
                link.target(rectMap[getNameOfUri(parentMap[getNameOfUri(type)].parent)])
                link.attr({
                    line: {
                        class: 'metaLink',
                        'data-source-1': rectMap[getNameOfUri(type)].attributes.id,
                        'data-target-1': rectMap[getNameOfUri(parentMap[getNameOfUri(type)].parent)].attributes.id,
                        'data-uri-1': 'none',
                        stroke: 'orange',
                        targetMarker: {
                            fill: 'white',
                            'stroke-width': 2
                        }
                    }
                })
                link.addTo(graph)
            }
        })
        
        min.forEach(function(rel){
            createLink(rel)
        })

        exactly.forEach(function(rel){
            createLink(rel)
        })

        some.forEach(function(rel){
            createLink(rel)
        })
    
        joint.layout.DirectedGraph.layout(graph, {
            nodeSep: 20,
            edgeSep: 80,
            rankSep: 300,
            rankDir: "LR"
            }
        );

        loadLayout()

    })  
})

var svgZoom = svgPanZoom(' svg', {
    center: true,
    zoomEnabled: true,
    panEnabled: true,
    controlIconsEnabled: true,
    enableDblClickZoom: false,
    fit: false,
    minZoom: 0.2,
    maxZoom:10,
    zoomScaleSensitivity: 0.3
  });

paper.on('blank:pointerdown', function (evt, x, y) {
    svgZoom.enablePan();
});
paper.on('cell:pointerup blank:pointerup', function(cellView, event) {
    svgZoom.disablePan();
});


graph.on('change:source change:target', function(link) {
    if (link.get('source').id === link.get('target').id) {
        // self-looping link detected.
        link.set('vertices', findLoopLinkVertices(link));
    }
})

// -----------------------------
// Helpers
// -----------------------------

function getSuperTypes(parentMap, type) {
    var allParents = []
    getSuperTypesInner(parentMap, type, allParents)
    return allParents
}

function getSuperTypesInner(parentMap, type, allParents){
    var directParent = parentMap[getNameOfUri(type)].parent
    if (directParent) {
        allParents.push(directParent)
        getSuperTypesInner(parentMap, directParent, allParents)
    }
}

function createLink(rel){
    var link = new joint.shapes.standard.Link()
    link.prop('linkType', 'association')
    var oppositeLink = getOppositeLink(rectMap[getNameOfUri(rel.source)], rectMap[getNameOfUri(rel.target)])
    if(rel.source == rel.target){
        
    } else if(oppositeLink){
        oppositeLink.prop('linkType', 'association')
        oppositeLink.appendLabel({
            attrs: {
                text: {
                    fontSize: 25,
                    text: getNameOfUri(rel.property)
                }
            },
            position: {
                distance: 0.25
            }
        });

        oppositeLink.attr({
            line: {
                'data-uri-2': rel.property,
                'data-source-2': rectMap[getNameOfUri(rel.source)].attributes.id,
                'data-target-2': rectMap[getNameOfUri(rel.target)].attributes.id,
                sourceMarker: {
                    type: 'path',
                    'd': 'M 10 -5 0 0 10 5 Z',
                    fill: 'black',
                    stroke: 'black'
                }
            }
        })
    } else {
        link.source(rectMap[getNameOfUri(rel.source)])
        link.target(rectMap[getNameOfUri(rel.target)])
        link.appendLabel({
            attrs: {
                text: {
                    fontSize: 25,
                    text: getNameOfUri(rel.property)
                }
            },
            position: {
                distance: 0.75
            }
        });
        link.attr({
            line: {
                'data-uri-1': rel.property,
                'data-source-1': rectMap[getNameOfUri(rel.source)].attributes.id,
                'data-target-1': rectMap[getNameOfUri(rel.target)].attributes.id,
                class: 'metaLink'  
            }
        })
        link.addTo(graph)
    }
}

function relationIncludes(list, item, STDirection){
    var included = false
    list.forEach(function(i){
        itemCopy = JSON.parse(JSON.stringify(item))
        iCopy = JSON.parse(JSON.stringify(i))

        if (STDirection) {
            iCopy.source = ''
            itemCopy.source = ''
        } else {
            iCopy.target = ''
            itemCopy.target = ''
        }

        if (JSON.stringify(iCopy) === JSON.stringify(itemCopy)){
            included = true
        }
    })
    
    return included
}

function restructureRelations(types, relations, relationType, parentMap){
    var relationsBySource = []
    
    types.forEach(function(type){
        var typeName = getNameOfUri(type)
        var relationsByType = relations[relationType].filter(rel => rel.source == type)
        var relationsByParentType = relations[relationType].filter(rel => rel.source == parentMap[typeName].parent)
        var difference = relationsByType.filter(rel => !relationIncludes(relationsByParentType, rel, true))

        relationsBySource = relationsBySource.concat(difference)
    })
    return relationsBySource
}

function saveGraph(){
    graphData = JSON.stringify(graph)
    graphData = JSON.stringify(graph.toJSON())
    $.post('http://localhost:5000/savegraph', {graphData: graphData}, function(data, status){ 
    })
}

function loadGraph(){
    $.get('http://localhost:5000/loadgraph', function(data, status){
        graph.fromJSON(JSON.parse(data))
    })
}

function loadLayout(){
    $.get('http://localhost:5000/loadgraph', function(data, status){
        loadedGraph = JSON.parse(data)
        loadedGraph.cells = loadedGraph.cells.filter(cell => cell.type == 'standard.Rectangle')
        graph.getElements().forEach(function(element, index){
            loadedGraph.cells.forEach(function(cell){
                if(cell.attrs.body['data-uri'] == element.attributes.attrs.body['data-uri']){
                    element.position(cell.position.x, cell.position.y)
                }
            })
        })
        graph.getLinks().forEach(function(link){
            console.log(link.prop('type'))
        })
    })
}

function saveCanvasAsPNG(){
    var canvas = document.getElementsByClassName('canvas')[0]
    var img = canvas.toDataURL('image/png')
    console.log('hej')
    console.log(img)
}
