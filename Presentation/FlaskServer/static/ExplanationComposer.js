
// -------------------------------------------------------------------
// Main 
// -------------------------------------------------------------------

function getAngleOfDiagonal(rectWidth, rectHeight){
    angle = Math.asin(rectWidth/(Math.sqrt(Math.pow(rectWidth, 2) + Math.pow(rectHeight, 2))))
    return angle * (180/Math.PI)
}

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

var polyX = 0
var polyY = 0
var polyWidth = 50
var arrowSize = 8
var points = (polyX + polyWidth/2) + ',' + 
            (polyY + arrowSize + polyWidth/2) + ' ' + 
            (polyX + polyWidth/2) + ',' +
            (polyY - arrowSize + polyWidth/2) + ' ' + 
            (polyX + arrowSize + polyWidth/2) + ',' + 
            (polyY + polyWidth/2)

joint.dia.Element.define('standard.RelationSelector', {
    attrs: {
        leftBody: {
            refWidth: '50%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000',
            fill: '#fff',
            event: 'relationSelector:forward'
        },
        rightBody: {
            refX: '50%',
            refWidth: '50%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000',
            fill: '#fff',
            event: 'relationSelector:backward'
        },
        confirmBody: {
            refX: '100%',
            refWidth: '50%',
            refHeight: '100%',
            strokeWidth: 2,
            stroke: '#000',
            fill: '#999',
            event: 'relationSelector:confirm'
        },
        leftBodyArrow: {
            ref: 'leftBody',
            refX: 0,
            refY: 0,
            points: points,
            'pointer-events': 'none'
        },
        rightBodyArrow: {
            ref: 'rightBody',
            refX: 0,
            refY: 0,
            points: points,
            'pointer-events': 'none'
        },
        confirmBodyLabel: {
            ref: 'confirmBody',
            refX: '50%',
            refY: '50%',
            textVerticalAnchor: 'middle',
            textAnchor: 'middle',
            fill: '#333333',
            text: 'OK',
            'pointer-events': 'none'
        },
        isSelected: false
    }
}, {
    markup: [{
        tagName: 'rect',
        selector: 'leftBody'
    }, {
        tagName: 'rect',
        selector: 'rightBody'
    }, {
        tagName: 'rect',
        selector: 'confirmBody'
    }, {
        tagName: 'text',
        selector: 'confirmBodyLabel'
    }, {
        tagName: 'polygon',
        selector: 'leftBodyArrow'
    }, {
        tagName: 'polygon',
        selector: 'rightBodyArrow'
    }]
})

var cellToOrderIndicatorMapping = {}

function createOrderIndicator(cellView) {
    var cellBBox = cellView.model.getBBox()
    var rect = new joint.shapes.standard.OrderIndicator()
   
    rect.position(cellBBox.x-20, cellBBox.y-20)
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

paper.on('relationSelector:confirm', function(view, evt, x, y) {
    if ((view.model.attr('leftBody/class') != 'selected') && (view.model.attr('rightBody/class') != 'selected')) {
        unhighlightCell(paper.findViewByModel(view.model.getParentCell()))
        view.model.remove()
    }else if (!view.model.attr('isSelected')) {
        view.model.attr({
            confirmBody: {
                opacity: 0
            },
            confirmBodyLabel: {
                opacity: 0
            }
        })
        view.model.attr('isSelected', true)  
        highlightCell(paper.findViewByModel(view.model.getParentCell()))
    }

})

function editRelationSelector(view){
    if (view.model.attr('isSelected')) {
        view.model.attr({
            confirmBody: {
                opacity: 1
            },
            confirmBodyLabel: {
                opacity: 1
            }
        })
        view.model.attr('isSelected', false)  
    }
}

paper.on('relationSelector:forward', function(view, evt, x, y) {
    editRelationSelector(view)
    // console.log(view.model.attr('leftBody'))
    if (view.model.attr('leftBody/class') == 'selected') {
        view.model.attr('leftBody/class', '')   
    } else {
        view.model.attr('leftBody/class', 'selected')
    }
})

paper.on('relationSelector:backward', function(view, evt, x, y) {
    editRelationSelector(view)
    if (view.model.attr('rightBody/class') == 'selected') {
        view.model.attr('rightBody/class', '')        
    } else {
        view.model.attr('rightBody/class', 'selected')
    }
})

paper.on('blank:pointerdown', function(view, evt, x ,y) {
    clearRelationSelectors()   
})

paper.on('element:pointerdown', function(elementView, evt, x, y) {

    if (elementView.model.attributes.type == 'standard.Rectangle') {
        if (d3.select('#' + elementView.id).attr('class').includes('selected')) {
            removeTypeOptionDiv(elementView.model.attr('body/data-uri'), 'type-container')

            unhighlightCell(elementView, true)
            recursiveUnhighlightInheritanceWrapper(elementView, true)
            recursiveUnhighlightInheritanceWrapper(elementView, false)
        } else {
            //Add side-bar div element
            addTypeOptionDiv(elementView.model.attr('body/data-uri'), 'type-container')

            //Highlight selection
            currentSelection = elementView
            clearRelationSelectors()
            highlightCell(elementView)
            recursiveHighlightInheritanceWrapper(elementView, true)
            recursiveHighlightInheritanceWrapper(elementView, false)
            elementView.highlight(null, {
                highlighter: {
                    name: 'addClass',
                    options: {
                        className: 'selected'
                    }
                }
            })
        }        
    }
})

paper.on('link:pointerdown', function(linkView, evt,x,y) {
    clearRelationSelectors()   
    // console.log(linkView)
    if (linkView.model.attr('line/data-uri-2')) {
        createRelationSelector(linkView)
    } else {
        if (Math.abs(linkView.sourcePoint.y - linkView.targetPoint.y) > Math.abs(linkView.sourcePoint.x - linkView.targetPoint.x)) {
            if (linkView.sourcePoint.y > linkView.targetPoint.y) {
                createRelationSelector(linkView, true, 'BT')
            } else {
                createRelationSelector(linkView, true, 'TB')
            }
        } else {
            if (linkView.sourcePoint.x < linkView.targetPoint.x) {
                createRelationSelector(linkView, true, 'LR')
            } else {
                createRelationSelector(linkView, true, 'RL')
            }
        }
    }
})

function getAllSelectedLinks() {
    var selectedLinkUris = []
    graph.getElements().forEach(function(element){
        if (element.attributes.type == 'standard.RelationSelector' && element.attr('isSelected')) {
            if (element.prop('leftBodyUri') && element.attr('leftBody/class') && element.attr('leftBody/class').includes('selected')){
                selectedLinkUris.push({
                    name: element.prop('leftBodyUri'),
                    source: graph.getCell(element.prop('leftSourceUri')).attr('body/data-uri'),
                    target: graph.getCell(element.prop('leftTargetUri')).attr('body/data-uri')
                })
            }
            if (element.prop('rightBodyUri') && element.attr('rightBody/class') && element.attr('rightBody/class').includes('selected')) {
                selectedLinkUris.push({
                    name: element.prop('rightBodyUri'),
                    source: graph.getCell(element.prop('rightSourceUri')).attr('body/data-uri'),
                    target: graph.getCell(element.prop('rightTargetUri')).attr('body/data-uri')
                })    
            }
        }
    })

    return selectedLinkUris

}

function createRelationSelector(linkView, singleArrow=false, direction=''){
    if (singleArrow && linkView.model.prop('linkType') != 'inheritance') {
        var relationSelectorWidth = 50
        var relationSelectorHeight = 50
        var rect = new joint.shapes.standard.RelationSelector()
        var x = Math.max(linkView.targetPoint.x, linkView.sourcePoint.x) - (Math.abs(linkView.targetPoint.x - linkView.sourcePoint.x)/2 + relationSelectorWidth/2) 
        var y = Math.max(linkView.targetPoint.y, linkView.sourcePoint.y) - (Math.abs(linkView.targetPoint.y - linkView.sourcePoint.y)/2 + relationSelectorHeight/2) 

        rect.prop('leftBodyUri', linkView.model.attr('line/data-uri-1'))
        rect.prop('leftSourceUri', linkView.model.attr('line/data-source-1'))
        rect.prop('leftTargetUri', linkView.model.attr('line/data-target-1'))
                
        rect.position(x,y)
        rect.resize(relationSelectorWidth, relationSelectorHeight)
        rect.attr({
            leftBody: {
                class: 'selected',
                refWidth: '100%'
            },
            rightBody: {
                display: 'none'
            },
            confirmBody: {
                refWidth: '100%'
            },
            rightBodyArrow: {
                display: 'none'
            }
        })

        if(direction == 'BT'){
            rect.attr({
                leftBodyArrow: {
                    refY: arrowSize/2,
                    transform: 'rotate(270 25 25)'
                }
            })   
        } else if (direction == 'TB') {
            rect.attr({
                leftBodyArrow: {
                    refY: -arrowSize/2,
                    transform: 'rotate(90 25 25)'
                }
            })   
        } else if (direction == 'LR') {
            // Do nothing
        } else if (direction == 'RL') {
            rect.attr({
                leftBodyArrow: {
                    transform: 'rotate(180 25 25)'
                }
            })   
        }
        
        linkView.model.embed(rect)
        rect.addTo(graph)      
    } else if (!singleArrow){
        var pathBBox = d3.select('#' + linkView.id).select('.metaLink').node().getBBox()
        var pathAngle = getAngleOfDiagonal(pathBBox.height, pathBBox.width)
        var relationSelectorWidth = 100
        var relationSelectorHeight = 50
        var rect = new joint.shapes.standard.RelationSelector()
        var x = Math.max(linkView.targetPoint.x, linkView.sourcePoint.x) - (Math.abs(linkView.targetPoint.x - linkView.sourcePoint.x)/2 + relationSelectorWidth/2) 
        var y = Math.max(linkView.targetPoint.y, linkView.sourcePoint.y) - (Math.abs(linkView.targetPoint.y - linkView.sourcePoint.y)/2 + relationSelectorHeight/2)         

        rect.position(x,y)
        rect.resize(relationSelectorWidth, relationSelectorHeight)

        if (pathAngle % 180 > 45 && pathAngle % 180 < 135) {
            pathAngle = 90
            rect.attr({
                leftBodyArrow: {
                    refY: arrowSize/2,
                    transform: 'rotate(' + (pathAngle + 180) + ' 25 25)'
                },
                rightBodyArrow: {
                    refY: -arrowSize/2,
                    transform: 'rotate(' + pathAngle + ' 25 25)'
                }
            })    

            if (linkView.sourcePoint.y > linkView.targetPoint.y) {
                rect.prop('leftSourceUri', linkView.model.attr('line/data-source-1'))
                rect.prop('leftTargetUri', linkView.model.attr('line/data-target-1'))
                rect.prop('leftBodyUri', linkView.model.attr('line/data-uri-1'))
                
                rect.prop('rightSourceUri', linkView.model.attr('line/data-source-2'))
                rect.prop('rightTargetUri', linkView.model.attr('line/data-target-2'))
                rect.prop('rightBodyUri', linkView.model.attr('line/data-uri-2'))
            } else {
                rect.prop('leftBodyUri', linkView.model.attr('line/data-uri-2'))
                rect.prop('leftSourceUri', linkView.model.attr('line/data-source-2'))
                rect.prop('leftTargetUri', linkView.model.attr('line/data-target-2'))
                
                rect.prop('rightSourceUri', linkView.model.attr('line/data-source-1'))
                rect.prop('rightTargetUri', linkView.model.attr('line/data-target-1'))
                rect.prop('rightBodyUri', linkView.model.attr('line/data-uri-1'))
            }

        } else {
            pathAngle = 0
            rect.attr({
                leftBodyArrow: {
                    transform: 'rotate(' + (pathAngle + 180) + ' 25 25)'
                },
                rightBodyArrow: {
                    transform: 'rotate(' + pathAngle + ' 25 25)'
                }
            })    
            
            if (linkView.sourcePoint.x > linkView.targetPoint.y) {
                rect.attr('data-leftBodyUri', linkView.model.attr('data-uri-1'))
                rect.attr('data-rightBodyUri', linkView.model.attr('data-uri-2'))
            } else {
                rect.attr('data-leftBodyUri', linkView.model.attr('data-uri-2'))
                rect.attr('data-rightBodyUri', linkView.model.attr('data-uri-1'))
            }

            if (linkView.sourcePoint.x > linkView.targetPoint.x) {
                rect.prop('leftSourceUri', linkView.model.attr('line/data-source-1'))
                rect.prop('leftTargetUri', linkView.model.attr('line/data-target-1'))
                rect.prop('leftBodyUri', linkView.model.attr('line/data-uri-1'))
                
                rect.prop('rightSourceUri', linkView.model.attr('line/data-source-2'))
                rect.prop('rightTargetUri', linkView.model.attr('line/data-target-2'))
                rect.prop('rightBodyUri', linkView.model.attr('line/data-uri-2'))
            } else {
                rect.prop('leftBodyUri', linkView.model.attr('line/data-uri-2'))
                rect.prop('leftSourceUri', linkView.model.attr('line/data-source-2'))
                rect.prop('leftTargetUri', linkView.model.attr('line/data-target-2'))
                
                rect.prop('rightSourceUri', linkView.model.attr('line/data-source-1'))
                rect.prop('rightTargetUri', linkView.model.attr('line/data-target-1'))
                rect.prop('rightBodyUri', linkView.model.attr('line/data-uri-1'))
            }

        }
        
    linkView.model.embed(rect)
    rect.addTo(graph)      
    }      
}

function clearRelationSelectors() {
    graph.getElements().forEach(function(element){
        if (element.attributes.type == 'standard.RelationSelector' && !element.attr('isSelected')) {
            element.remove()
        }
    })
}
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

// Unhighlights all cells in graph
function unhighlightAllCells(){
    graph.getCells().forEach(function(cell){
        var currentCellView = paper.findViewByModel(cell)
        if (currentCellView) {
            clearHighlight(currentCellView)
        }
    })
}

function clearHighlight(cellView) {
    cellView.model.prop('isSelected', 0)
    if (cellView.model.attributes.type == 'standard.Rectangle') {
        cellView.unhighlight(null, {
            highlighter: {
                name: 'addClass',
                options: {
                    className: 'selected'
                }
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
    }
    else {
        unhighlightCell(cellView, true)
    }
}

// Unhighlights a cell
function unhighlightCell(cellView, forceUnselect=false){
    cellView.model.prop('isSelected', parseInt(cellView.model.prop('isSelected')) - 1)

    if (cellView.model.attributes.type == 'standard.RelationSelector') {
        cellView.model.remove()
    }

    if (forceUnselect) {
        cellView.unhighlight(null, {
            highlighter: {
                name: 'addClass',
                options: {
                    className: 'selected'
                }
            }
        })
    }

    if (cellView.model.prop('isSelected') > 0) {
        return
    }

    cellView.unhighlight(null, {
        highlighter: {
            name: 'addClass',
            options: {
                className: 'selected'
            }
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
}

// Highlights a cell
function highlightCell(cellView){
    cellView.model.prop('isSelected', parseInt(cellView.model.prop('isSelected')) + 1)
    
    if (cellView.model.attributes.type == 'standard.Link') {
        // console.log('Link: ' + cellView.model.prop('isSelected'))
    } else {
        // console.log('Element: ' + cellView.model.prop('isSelected'))
    }

    cellView.highlight(null, {
        highlighter: {
            name: 'addClass',
            options: {
                className: 'highlighted'
            }
        }
    }) 
}

// Highlights cells that are connected via an outbound inheritance link
function highlightOutboundInheritance(cellView, first=false){
    var links = graph.getConnectedLinks(cellView.model, {inbound: true, outbound: true})
    
    if (!first){
        highlightCell(cellView)
    }

    links.forEach(function(link){
        if((link.prop('linkType') == 'inheritance') && (link.attributes.source.id == cellView.model.id)){
            highlightCell(paper.findViewByModel(link))
        }
    })
}

// Unhighlights cells that are connected via an outbound inheritance link
function unhighlightOutboundInheritance(cellView, first=false){
    var links = graph.getConnectedLinks(cellView.model, {inbound: true, outbound: true})
    
    if (!first) {
        unhighlightCell(cellView)
    }

    links.forEach(function(link){
        if((link.prop('linkType') == 'inheritance') && (link.attributes.source.id == cellView.model.id)){
            unhighlightCell(paper.findViewByModel(link))
        }
    })
}

// Highlight current cell and neighbors
function highlightNeighbors(cellView, linkTypes=null, isInbound=null, first=false){
    if (isInbound == null) {
        var links = graph.getConnectedLinks(cellView.model)
    } else if (isInbound == false) {
        var links = graph.getConnectedLinks(cellView.model, {outbound: true}) 
    } else if (isInbound == true)
        var links = graph.getConnectedLinks(cellView.model, {inbound: true}) 
    
    if (!first) {
        highlightCell(cellView)
    }

    links.forEach(function(link){
        if(linkTypes != null && linkTypes.includes(link.prop('linkType'))) {        
            highlightCell(paper.findViewByModel(link))
        } 
    })
}

// Unhighlight current cell and neighbors
function unhighlightNeighbors(cellView, linkTypes=null, isInbound=null, first=false){
    if (isInbound == null) {
        var links = graph.getConnectedLinks(cellView.model)
    } else if (isInbound == false) {
        var links = graph.getConnectedLinks(cellView.model, {outbound: true}) 
    } else if (isInbound == true)
        var links = graph.getConnectedLinks(cellView.model, {inbound: true}) 

    if(!first){
        unhighlightCell(cellView)
    }

    links.forEach(function(link){
        if(linkTypes != null && linkTypes.includes(link.prop('linkType'))) {        
            unhighlightCell(paper.findViewByModel(link))
        } 
    })
}

// Recursively highlights directly and indirectly connected cells that have the inheritance link type
function recursiveHighlightInheritanceWrapper(cellView, useInbound=true){
    recursiveHighlightInheritance(cellView, useInbound, true)
}

function recursiveHighlightInheritance(cellView, useInbound=true, first=false){
    if (!cellView){
        return
    }

    if (useInbound) {
        highlightNeighbors(cellView, ['inheritance'], true, first)
        var inboundLinks = graph.getConnectedLinks(cellView.model, {inbound: true})
        inboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var sourceCellView = paper.findViewByModel(graph.getCell(link.attributes.source.id)) 
                recursiveHighlightInheritance(sourceCellView, useInbound)
            }
        })

    } else {
        highlightOutboundInheritance(cellView, first)
        var outboundLinks = graph.getConnectedLinks(cellView.model, {outbound: true})
        outboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var targetCellView = paper.findViewByModel(graph.getCell(link.attributes.target.id)) 
                recursiveHighlightInheritance(targetCellView, useInbound)
            }
        })
    }
}

function recursiveUnhighlightInheritanceWrapper(cellView, useInbound=true) {
    recursiveUnhighlightInheritance(cellView, useInbound, true)
}

function recursiveUnhighlightInheritance(cellView, useInbound=true, first=false){
    if (!cellView){
        return
    }

    if (useInbound) {
        unhighlightNeighbors(cellView, ['inheritance'], true, first)
        var inboundLinks = graph.getConnectedLinks(cellView.model, {inbound: true})
        inboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var sourceCellView = paper.findViewByModel(graph.getCell(link.attributes.source.id)) 
                recursiveUnhighlightInheritance(sourceCellView, useInbound)
            }
        })

    } else {
        unhighlightOutboundInheritance(cellView, first)
        var outboundLinks = graph.getConnectedLinks(cellView.model, {outbound: true})
        outboundLinks.forEach(function(link){
            if(link.prop('linkType') == 'inheritance'){
                var targetCellView = paper.findViewByModel(graph.getCell(link.attributes.target.id)) 
                recursiveUnhighlightInheritance(targetCellView, useInbound)
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
    
        //Adjust screen pos
        
        var viewport = d3.select('g.joint-viewport')
        viewport.attr('transform', 'scale(0.32,0.32) translate(-4602, -1696) ')
        console.log(viewport.node().getBoundingClientRect())

    })
}