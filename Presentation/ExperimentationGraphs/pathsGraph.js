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

var entities = []
var elements = {}
paths.forEach(function(rel){
    var source
    var target
    if (!entities.includes(rel.source)){
        entities.push(rel.source)
        source = createEntity(rel.source)
        elements[rel.source] = source
    }
    if (!entities.includes(rel.target)){
        entities.push(rel.target)
        target = createEntity(rel.target)
        elements[rel.target] = target
    }
    console.log(entities)
    var link = new joint.shapes.standard.Link()
    link.source(elements[rel.source])
    link.target(elements[rel.target])
    link.appendLabel({
        attrs: {
            text: {
                text: 'hej'
            }
        },
        position: {
            distance: 0.75
        }
    });
    link.attr({
        stroke: 'orange',
        targetMarker: {
            fill: 'white',
            'stroke-width': 2
        }
    })
    link.addTo(graph)
    
})

function createEntity(e){
    var rect = new joint.shapes.standard.Rectangle();
    rect.position(90, 30);
    rect.attr({
        label: {
            fontSize: 20,
            text: getNameOfUri(e),
        },
        body:{
            fill: 'white',
        } 
    });
    minwidth = 90
    width = parseInt(getNameOfUri(e).length) * 15
    
    if(minwidth > width){
        width = minwidth
    }

    rect.resize(width, 40);
    rect.addTo(graph);
    return rect
}

paths.forEach(function(rel){

})

function getNameOfUri(string){
    string = string.replace(/.+#/, '')
    string = string.replace(/\./g, '_')
    return string
}

joint.layout.DirectedGraph.layout(graph, {
    nodeSep: 100,
    edgeSep: 80,
    rankSep: 300,
    rankDir: "LR"
    }
);

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