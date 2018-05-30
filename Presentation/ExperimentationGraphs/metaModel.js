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
  gridSize: 20,
  model: graph
});

joint.dia.Element.define('standard.Rectangle', {
    attrs: {
        body: {
            refWidth: '100%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000000',
            fill: '#FFFFFF'
        },
        label: {
            textVerticalAnchor: 'middle',
            textAnchor: 'middle',
            refX: '50%',
            refY: '50%',
            fontSize: 14,
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
$.get('http://localhost:5000/getOntology', function(data, status){
    console.log(data)
    var ontology = JSON.parse(data)
    var types = ontology.types
    var relations = ontology.relations

    types.forEach(function(type){
        var rect = new joint.shapes.standard.Rectangle();
        rect.position(100, 30);
        rect.resize(100, 40);
        rect.attr({
            label: {
                text: getNameOfUri(type),
            }
        });
        rect.addTo(graph);
        rectMap[getNameOfUri(type)] = rect
    })

    relations.min.forEach(function(rel){
        var link = new joint.shapes.standard.Link()
        link.source(rectMap[getNameOfUri(rel.source)])
        link.target(rectMap[getNameOfUri(rel.target)])
        link.labels([{
            attrs: {
                text: {
                    //text: getNameOfUri(rel.name)
                }
            }
        }])
        link.addTo(graph)
    })

    relations.exactly.forEach(function(rel){
        var link = new joint.shapes.standard.Link()
        link.source(rectMap[getNameOfUri(rel.source)])
        link.target(rectMap[getNameOfUri(rel.target)])
        link.labels([{
            attrs: {
                text: {
                    //text: getNameOfUri(rel.name)
                }
            }
        }])
        link.addTo(graph)
    })
    relations.some.forEach(function(rel){
        var link = new joint.shapes.standard.Link()
        link.source(rectMap[getNameOfUri(rel.source)])
        link.target(rectMap[getNameOfUri(rel.target)])
        link.labels([{
            attrs: {
                text: {
                    //text: getNameOfUri(rel.name)
                }
            }
        }])
        link.addTo(graph)
    })

    joint.layout.DirectedGraph.layout(graph, {
        nodeSep: 20,
        edgeSep: 80,
        rankSep: 300,
        rankDir: "LR"
        }
    );

})

// metaModel.types.forEach(function(type){
//     var rect = new joint.shapes.standard.Rectangle();
//     rect.position(100, 30);
//     rect.resize(100, 40);
//     rect.attr({
//         label: {
//             text: getNameOfUri(type),
//         }
//     });
//     rect.addTo(graph);
//     rectMap[getNameOfUri(type)] = rect
// }) 

// metaModel.relations.forEach(function(relation){
//     var link = new joint.shapes.standard.Link()
//     link.source(rectMap[getNameOfUri(relation.source)])
//     link.target(rectMap[getNameOfUri(relation.target)])
//     link.labels([{
//         attrs: {
//             text: {
//                 text: getNameOfUri(relation.name)
//             }
//         }
//     }])
//     link.addTo(graph)
// }) 

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


graph.on('change:source change:target', function(link) {
    if (link.get('source').id === link.get('target').id) {
        // self-looping link detected.
        link.set('vertices', findLoopLinkVertices(link));
    }
 })

// function findLoopLinkVertices(link){

// }

// graph.resetCells(graph.getElements())



joint.layout.DirectedGraph.layout(graph, {
    nodeSep: 20,
    edgeSep: 80,
    rankSep: 300,
    rankDir: "LR"
    }
);

function saveGraph(){
    graphData = JSON.stringify(graph)
    $.post('http://localhost:5000/savegraph', {graphData: graphData}, function(data, status){ 
        console.log(status)
    })
}

function loadGraph(){
    $.get('http://localhost:5000/loadgraph', function(data, status){
        graph.fromJSON(JSON.parse(data))
    })
}
