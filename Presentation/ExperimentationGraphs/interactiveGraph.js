//--------------------------------------------------------------------
// UNIVERSAL FUNCTIONS
//--------------------------------------------------------------------

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
                        'RationaleLayer': '#b476c4', 'ImplementationLayer': 'gray'}
                        
var views = ['Development', 'UI', 'Logical', 'Physical'] 
var ontologyCategories = {'ArchitectureLayer':     ['Role', 'ArchitecturalPattern', 'Development', 'UI', 'Physical', 'Logical'], 
                          'RequirementLayer':      ['Requirement', 'UserStory', 'UseCase', 'Feature'], 
                          'RationaleLayer':        ['DesignOption', 'Technology', 'Argument', 'Constraint', 'Assumption'], 
                          'ImplementationLayer':   ['Implementation']}

function getEntityColor(entity){
    if(ONTOLOGY_COLORS[getNameOfUri(entity.type)]){
        return ONTOLOGY_COLORS[getNameOfUri(entity.type)]
    }else{
        color = ''
        entity.supertypes.forEach(function(s){
            //TODO: find a way to better code this
            //Brighten classes of views
            if(getNameOfUri(s) == 'DevelopmentClassPackage'){
                if(!color)
                    color = tinycolor(ONTOLOGY_COLORS['Development']).spin(0).brighten(25).desaturate(10).toString()
            }
            if(getNameOfUri(s) == 'DevelopmentClass'){
                if(!color)
                    color = tinycolor(ONTOLOGY_COLORS['Development']).spin(-20).brighten(35).desaturate(35).toString()
            }
            else if(ONTOLOGY_COLORS[getNameOfUri(s)]){
                if(!color)
                    color = ONTOLOGY_COLORS[getNameOfUri(s)]
            }
        })
        return color
    }
}

function getNameOfUri(string){
    string = string.replace(/.+#/, '')
    string = string.replace(/\./g, '_')
    return string
}

function getNameOfEntity(entity){
    if(entity.label){
        return entity.label
    }else{
        return getNameOfUri(entity.uri)
    }
}

// ----------------------------------------------------------------
// JOINTJS-CODE
// ----------------------------------------------------------------
var cells = []
var graph = new joint.dia.Graph;
var paper = new joint.dia.Paper({
  el: $('#myholder'),
  width: '100%',
  height: '100%',
  gridSize: 20,
  model: graph
});

// Custom elements

joint.shapes.standard.Rectangle.define('examples.CustomRectangle', {
    attrs: {
        body: {
            refWidth: '100%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000000',
            fill: '#FFFFFF',
            event: 'element:body:pointerdown'
        },
        label: {
            textVerticalAnchor: 'middle',
            textAnchor: 'middle',
            refX: '50%',
            refY: '50%',
            fontSize: 14,
            fill: '#333333',
            pointerEvents: 'none'
        },
    },
}, {

    markup: [{
        tagName: 'rect',
        selector: 'body',
    }, {
        tagName: 'text',
        selector: 'label'
    }]

}, {
    create: function(entity){
        var newElement = new this()
        newElement.entityId = entity.uri
        newElement.attr({
            entity: entity,
            label: {
                text: entity.label
            },
            body: {
                fill: ONTOLOGY_COLORS[getNameOfUri(entity.type)]
            }
        })
        return newElement
    }
}) 

// Diagram events
const DE = {
    find_rel: {event:'element:find_relations:pointerdown', text:'Find relations'}, 
    find_path: {event:'element:find_path_to:pointerdown', text:'Find path to'},
    explain_entity: {event:'element:explain_entity:pointerdown', text:'Explain entity'}
}

// Element 1
var element1 = joint.shapes.examples.CustomRectangle.create(ontologyData.entities[0])
element1.position(50,300);
element1.resize(350,50)
element1.addTo(graph)

var element1 = joint.shapes.examples.CustomRectangle.create(ontologyData.entities[2])
element1.position(50,300);
element1.resize(350,50)
element1.addTo(graph)

// Handle events
var selectedElementView
paper.on('element:body:pointerdown', function(elementView, evt, x, y){
    selectedElementView = elementView
    var entity = elementView.model.attr('entity')
    var elements = graph.getElements()
    
    elements.forEach(function(element){
        paper.findViewByModel(element).unhighlight()
    })

    elementView.highlight()

    d3.select('#entity_selection')
    .text(getNameOfUri(entity.uri))

    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    $.post('http://localhost:5000/query/getobjectpropertyrelations', {subjectUri: entity.uri}, function(data, status){
        relations = JSON.parse(data)
        var select = document.getElementById("relations_select");

        for (i = select.options.length - 1; i >= 0; i--) {
            select.remove(i);
        }

        var rel = []
        for (i in relations){
            rel.push(relations[i].relationUri)
        }

        new Set(rel).forEach(function(relationUri, i){
            var option = document.createElement("option");
            option.value = relationUri
            option.text = getNameOfUri(relationUri);
            if (i == 0){
                option.selected = 'selected'
            }
            select.add(option);
        })
    })
})

function drawPathTo(){
    var select = document.getElementById('path_select')
    var value = select.options[select.selectedIndex].value
    
}

function drawRelations(){
    elementView = selectedElementView
    entity = elementView.model.attr('entity')

    if(!entity){
        return
    }
    var select = document.getElementById('relations_select')
    var value = select.options[select.selectedIndex].value

    baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    $.post('http://localhost:5000/query/getrelations', {subjectUri: entity.uri, relationUri: value,  objectTypeUri: ''}, function(data, status){
        relations = JSON.parse(data)
        for (index in relations) {

            var existingElement = null
            graph.getElements().forEach(function(element){
                if (element.entityId == relations[index].entity.uri) {
                    existingElement = element
                }
            })

            if (!existingElement) {
                var entityElement = joint.shapes.examples.CustomRectangle.create(relations[index].entity)
                entityElement.position(50,300);
                entityElement.resize(350,50)
                entityElement.addTo(graph)
            } else {
                entityElement = existingElement
            }

            link = new joint.dia.Link({
                source: { id: elementView.model.attributes.id},
                target: { id: entityElement.attributes.id},
                attrs: { 
                    '.connection' : { 'stroke-dasharray': '10,10'},
                    '.marker-target': { d: 'M 4 0 L 0 2 L 4 4 z' } 
                },
                router: {'name': 'metro'}

            });
            link.addTo(graph)
            
            joint.layout.DirectedGraph.layout(graph, {
                nodeSep: 20,
                edgeSep: 80,
                rankSep: 300,
                rankDir: "LR"
                }
            );
            
        }
    })
}

var svgZoom = svgPanZoom('#myholder svg', {
    center: true,
    zoomEnabled: true,
    panEnabled: true,
    controlIconsEnabled: true,
    enableDblClickZoom: false,
    fit: false,
    minZoom: 0,
    maxZoom:10,
    zoomScaleSensitivity: 0.3
  });

paper.on('blank:pointerdown', function (evt, x, y) {
    svgZoom.enablePan();
});
paper.on('cell:pointerup blank:pointerup', function(cellView, event) {
    svgZoom.disablePan();
});

joint.layout.DirectedGraph.layout(graph, {
    nodeSep: 20,
    edgeSep: 80,
    rankSep: 300,
    rankDir: "LR"
    }
);
