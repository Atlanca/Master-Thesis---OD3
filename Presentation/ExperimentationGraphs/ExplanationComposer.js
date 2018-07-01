
// -------------------------------------------------------------------
// Main 
// -------------------------------------------------------------------

var graph = new joint.dia.Graph;
var paper = new joint.dia.Paper({
    el: $('#myholder'),
    width: '100%',
    height: '100%',
    gridSize: 15,
    model: graph,
    interactive: false,
    highlighting: {
        'default': {
            name: 'stroke',
            options: {
                width: 10
            }
        },
    }
});

loadGraph()


joint.dia.Element.define('standard.OrderIndicator', {
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

var cellToOrderIndicatorMapping = {}

function createOrderIndicator(cellView) {
    var cellBBox = cellView.model.getBBox()
    var rect = new joint.shapes.standard.OrderIndicator();
   
    rect.position(cellBBox.x-20, cellBBox.y-20);
    rect.attr({
        label: {
            fontSize: 30,
            text: '1',
        },
        body:{
            class: 'order-indicator',
            fill: '#fff'
        } 
    });
    rect.resize(35,35)
    cellView.model.embed(rect)
    rect.addTo(graph)
    cellToOrderIndicatorMapping[cellView.model.attributes.id] = rect
}

function removeOrderIndicator(cellView) {
    cellToOrderIndicatorMapping[cellView.model.attributes.id].remove()
    cellToOrderIndicatorMapping[cellView.model.attributes.id] = null
}


var currentSelection = null
paper.on('cell:pointerdown', 
    function(cellView, evt, x, y) { 
        if(!cellToOrderIndicatorMapping[cellView.model.attributes.id]){
            createOrderIndicator(cellView)
        } 

        if (cellView.model.attributes.type.includes('Rectangle')){
            unhighlightAllCells(cellView)
            recursiveHighlightInheritance(cellView, true)
            recursiveHighlightInheritance(cellView, false)
            cellView.highlight(null, {
                highlighter: {
                    name: 'addClass',
                    options: {
                        className: 'selected'
                    }
                }
            })
        }
        
        if (cellView == currentSelection){
            removeOrderIndicator(cellView)
            unhighlightAllCells(cellView)
            nolightAllCells()
            currentSelection = null
        } else {
            currentSelection = cellView
        }
    }
);

// -------------------------------------------------------------------
// Zoom
// -------------------------------------------------------------------
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

// -------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------

function nolightAllCells(){
    graph.getCells().forEach(function(cell){
        nolightCell(cell)
    })
}

// Unhighlights all cells in graph
function unhighlightAllCells(cellView){
    graph.getCells().forEach(function(cell){
        if (cell.attributes.type.includes('Rectangle') || cell.attributes.type.includes('Link')){
            var currentCellView = paper.findViewByModel(cell)
            unhighlightCell(currentCellView)
        }
    })

    var outboundLinks = graph.getConnectedLinks(cellView.model, {outbound: true, inbound: true})
    outboundLinks.forEach(function(link){
        var linkView = paper.findViewByModel(link)
        unhighlightCell(linkView)
    })
}

// Unhighlights a cell
function unhighlightCell(cellView){
    cellView.highlight(null, {
        highlighter: {
            name: 'opacity'
        }
    })

    cellView.unhighlight(null, {
        highlighter: {
            name: 'addClass',
            options: {
                className: 'highlighted'
            }
        }
    })

    cellView.unhighlight(null, {
        highlighter: {
            name: 'addClass',
            options: {
                className: 'selected'
            }
        }
    })
}

// Highlights a cell
function highlightCell(cellView){
    cellView.unhighlight(null, {
        highlighter: {
            name: 'opacity'
        }
    })
    
    cellView.highlight(null, {
        highlighter: {
            name: 'addClass',
            options: {
                className: 'highlighted'
            }
        }
    }) 
}

// Normal lights cell
function nolightCell(cell){
    paper.findViewByModel(cell).unhighlight(null, {
        highlighter: {
            name: 'opacity'
        }
    })
}

// Highlights cells that are connected via an outbound inheritance link
function highlightOutboundInheritance(cellView){
    var links = graph.getConnectedLinks(cellView.model, {inbound: true, outbound: true})
    highlightCell(cellView)

    links.forEach(function(link){
        if((link.prop('linkType') == 'inheritance') && (link.attributes.source.id == cellView.model.id)){
            highlightCell(paper.findViewByModel(link))
            nolightConnectedCells(link)
        } else if (link.prop('linkType') != 'inheritance'){
            nolightCell(link)
            nolightConnectedCells(link)
        }
    })
}

// Normal lights all directly connected cells
function nolightConnectedCells(link){
    var neighborCell1 = graph.getCell(link.attributes.source.id)
    nolightCell(neighborCell1)

    var neighborCell2 = graph.getCell(link.attributes.target.id)
    nolightCell(neighborCell2)
}

// Highlight current cell and neighbors
function highlightNeighbors(cellView, linkTypes=null){
    var links = graph.getConnectedLinks(cellView.model)
    highlightCell(cellView)

    links.forEach(function(link){
        if(linkTypes != null && linkTypes.includes(link.prop('linkType'))) {        
            highlightCell(paper.findViewByModel(link))
        } 
    })
}

// Recusrively highlights directly and indirectly connected cells that have the inheritance link type
function recursiveHighlightInheritance(cellView, useInbound=true){
    if (!cellView){
        return
    }

    if (useInbound) {
        highlightNeighbors(cellView, ['inheritance'])
        var inboundLinks = graph.getConnectedLinks(cellView.model, {inbound: true})
        inboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var sourceCellView = paper.findViewByModel(graph.getCell(link.attributes.source.id)) 
                recursiveHighlightInheritance(sourceCellView, useInbound)
            }
        })

    } else {
        highlightOutboundInheritance(cellView)
        var outboundLinks = graph.getConnectedLinks(cellView.model, {outbound: true})
        outboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var targetCellView = paper.findViewByModel(graph.getCell(link.attributes.target.id)) 
                recursiveHighlightInheritance(targetCellView, useInbound)
            }
        })
    }
}

var toType = function(obj) {
    return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase()
}

function loadGraph(){
    $.get('http://localhost:5000/loadgraph', function(data){
        graph.fromJSON(JSON.parse(data))
    })
}