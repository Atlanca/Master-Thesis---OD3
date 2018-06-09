var graph = new joint.dia.Graph;
var paper = new joint.dia.Paper({
  el: $('#myholder'),
  width: '100%',
  height: '100%',
  gridSize: 20,
  model: graph
});

var mode

//MAIN Code
//UGLY Workaround!
loadGraph(buildGraph)

function buildGraph(){
    var panCanvas = d3.select('.panCanvas')
    var jointViewport = d3.select('.joint-viewport')
    var jointMarkers = d3.select('#v-4')
    var myholder = d3.select('#myholder')
    var body = d3.select('body')

    addItem(jointMarkers.node())
    addItem(jointViewport.node())
    
    body.node().removeChild(myholder.node())
    jointViewport.attr('transform', 'translate(-1500, 450)')
    
    jointViewport.selectAll('rect.metaType').each(function(){
        d3.select(this).on('click', function(){
            mode.handleElementClick(this)
        })
    })  

    jointViewport.selectAll('.metaLink').each(function(){
        clonedNode = this.cloneNode()
        d3.select(clonedNode)
        .style('stroke-width', '20px')
        .style('opacity', '0')
        .classed('metaLink', false)
        .classed('linkInteractionArea', true)
        d3.select(this.parentNode).node().appendChild(clonedNode)
    })

    // this.mode = startPathMode()
}

//Helpers 
function startPathMode(){
    this.mode = new pathMode()
}

function loadGraph(callback){
    $.get('http://localhost:5000/loadgraph', function(data, status){
        graph.fromJSON(JSON.parse(data))
        callback()
    })
}

function clearSelection(){
    this.mode.clearSelection()
}

function getEntityPath(){
    mode.getEntityPath()
}

//Mode "class"
function pathMode(){

    var selectedLinks = {}
    var selectedTypes = {}
    var metaTypeSelectionCounter = {}
    jointViewport.selectAll('rect.metaType').each(function(){
        var modelId = d3.select(this.parentNode).attr('model-id')
        metaTypeSelectionCounter[modelId] = 0
        d3.select(this).on('click', function(){
            mode.handleElementClick(this)
        })
    
    })  
    
    this.handleElementClick = function(node){
        var modelId = d3.select(node.parentNode).attr('model-id')
        if (d3.select(node).classed('selected')){
            setUnselectedElement(modelId)
        }else{
            setSelectedElement(modelId)
        } 
    }

    this.handleEdgeClick = function(){

    }

    function getSelectedTypeIdByNumber(number){
        var returnVal = null
        Object.keys(selectedTypes).forEach(function(key){
            if (selectedTypes[key] == number) {
                returnVal = key
            }
        })
        return returnVal
    }

    function getSelectedEdges() {
        var childTypeUri = ''
        var relations = []        
        Object.keys(selectedTypes).forEach(function(key){
            if (selectedTypes[key] > 0) {
                var currentModelId = key
                var previousModelId = getSelectedTypeIdByNumber(selectedTypes[key] - 1)
                
                d3.selectAll('.wrapper .joint-viewport path.metaLink').each(function(){
                    var link = null
                    var sourceId1 = d3.select(this).attr('data-source-1')
                    var targetId1 = d3.select(this).attr('data-target-1')
                    var sourceId2 = d3.select(this).attr('data-source-2')
                    var targetId2 = d3.select(this).attr('data-target-2')
                    var sourceId
                    var targetId
                    var linkName

                    if ((sourceId1 == previousModelId && targetId1 == currentModelId)) {
                        linkName = d3.select(this).attr('data-uri-1')
                        sourceId = sourceId1
                        targetId = targetId1
                    }

                    if ((targetId1 == previousModelId && sourceId1 == currentModelId)) {
                        sourceId = sourceId2
                        targetId = targetId2
                        linkName = d3.select(this).attr('data-uri-2')         
                    }

                    if(!sourceId && !targetId && !linkName){
                        return
                    // Check if the link is inheritance or not
                    } else if (linkName == 'none') {
                        if (!childTypeUri) {
                            childTypeUri = d3.select('#' + getRectByModelId(sourceId)).attr('data-uri')
                        }
                    } else {
                        // Check if we have a child type
                        // If we do, make the relation to the child instead
                        if (childTypeUri) {
                            var sourceUri = childTypeUri
                            childTypeUri = null
                        } else {
                            var sourceUri = d3.select('#' + getRectByModelId(sourceId)).attr('data-uri')
                        }
                        var targetUri = d3.select('#' + getRectByModelId(targetId)).attr('data-uri')
                        link = {'source': sourceUri, 'property': linkName, 'target': targetUri}
                    }

                    if(link && !isInList(link, relations)) {
                        relations.push(link)
                    }
                })
            }
        })
        return relations
    }

    function isInList(object, list){
        var objectFound = false
        list.forEach(function(listobject){
            if(JSON.stringify(object) === JSON.stringify(listobject)){
                objectFound = true
            }
        })
        return objectFound
    }

    function getSelectionNumber(){
        var i = 0
        Object.keys(selectedTypes).forEach(function(key){
            if (selectedTypes[key] >= 0) {
                i++
            }
        })
        return i
        
    }

    function setSelectedElement(elementId){
        element = d3.select('#' + getRectByModelId(elementId)).classed('selected', true)
        selectedTypes[elementId] = getSelectionNumber()
        createOrderRect(element.node().parentNode)
    }

    function setUnselectedElement(elementId){
        d3.selectAll('.metaLink').each(function(){
            var sourceId = d3.select(this).attr('data-source-1')
            var targetId = d3.select(this).attr('data-target-1')
            if (sourceId == elementId || targetId == elementId) {
                d3.select(this).classed('selected', false)
                selectedLinks[d3.select(this).attr('id')] = false
            }
        })
        var element = d3.select('#' + getRectByModelId(elementId)).classed('selected', false)
        selectedTypes[elementId] = -1
        removeOrderRect(element.node().parentNode)
    }

    function setSelectedEdge(linkId, sourceId, targetId){
        d3.select('#' + linkId).classed('selected', true)        
        d3.select('#' + getRectByModelId(sourceId)).classed('selected', true)
        d3.select('#' + getRectByModelId(targetId)).classed('selected', true)
        selectedLinks[linkId] = true
        selectedTypes[sourceId] = getSelectionNumber()
        selectedTypes[targetId] = getSelectionNumber()
        metaTypeSelectionCounter[sourceId]++
        metaTypeSelectionCounter[targetId]++
    }

    function setUnselectedEdge(linkId, sourceId, targetId){
        d3.select('#' + linkId).classed('selected', false)
        selectedLinks[linkId] = false

        if(metaTypeSelectionCounter[sourceId] < 2){
            d3.select('#' + getRectByModelId(sourceId)).classed('selected', false)
            selectedTypes[sourceId] = -1
        }

        if(metaTypeSelectionCounter[targetId] < 2){
            d3.select('#' + getRectByModelId(targetId)).classed('selected', false)
            selectedTypes[targetId] = -1
        }

        metaTypeSelectionCounter[sourceId]--
        metaTypeSelectionCounter[targetId]--
    }

    function createOrderRect(elementNode){
        rectWidth = 20
        d3.select(elementNode)
        .append('rect')
        .attr('id', 's_1')
        .attr('width', rectWidth)
        .attr('height', rectWidth)
        .attr('x', -rectWidth/2)
        .attr('y', -rectWidth/2)
        .style('stroke', 'black')
        .style('fill', 'red')
        .classed('order-indicator', true)

        d3.select(elementNode)
        .append('text')
        .classed('order-indicator', true)
        .attr('y', rectWidth/4)
        .attr('x', -rectWidth/4)
        .text(getSelectionNumber())
    }

    function removeOrderRect(elementNode){
        d3.select(elementNode).selectAll('.order-indicator').remove()
    }

        
    function entityIsActive(modelId){
        var isActive = false
        d3.selectAll('.selected.metaLink').each(function(){
            var sourceId = d3.select(this).attr('data-source-1')
            var targetId = d3.select(this).attr('data-target-1')
            if (sourceId == modelId || targetId == modelId) {
                if (d3.select(this).classed('selected')) {
                    console.log('m:' + modelId)
                    console.log('s:' + sourceId)
                    console.log('t:' + targetId)
                    isActive = true
                }
            }
        })
        return isActive
    }

    function getRectByModelId(mId){
        var element
        d3.selectAll('.metaType').each(function(){
            if (mId == d3.select(this.parentNode).attr('model-id')){
                element = this.id
            }
        })
        return element
    }

    this.getEntityPath = function() {
        var linkUris = []
        var typeUris = []
        Object.keys(selectedLinks).forEach(function(key){
            if (selectedLinks[key]) {
                var forward = d3.select('#' + key).attr('data-uri-1')
                var backward = d3.select('#' + key).attr('data-uri-1')
                var sourceId = d3.select('#' + key).attr('data-source-1')
                var targetId = d3.select('#' + key).attr('data-target-1')
                var source = d3.select('#' + getRectByModelId(sourceId)).attr('data-uri')
                var target = d3.select('#' + getRectByModelId(targetId)).attr('data-uri')
                var link = {}
        
                if (forward)
                    link['forward-uri'] = forward
                if (backward)
                    link['backward-uri'] = backward
                link['source'] = source
                link['target'] = target
        
                linkUris.push(link)
            }
        })
        Object.keys(selectedTypes).forEach(function(key){
            if(selectedTypes[key]){
                typeUris.push(d3.select('#' + getRectByModelId(key)).attr('data-uri'))
            }
        })
        
        var relations = JSON.stringify(getSelectedEdges())
        console.log(JSON.stringify(relations))
        var baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
        typeUri = d3.select('#' + getRectByModelId(getSelectedTypeIdByNumber(1))).attr('data-uri')

        $.post('http://localhost:5000/getEntitiesByPath', {'startType': typeUri, 'relations': relations}, function(data){
            console.log(JSON.parse(data))

        })
    }

    this.clearSelection = function() {
        d3.selectAll('.metaType').each(function(){
            var modelId = d3.select(this.parentNode).attr('model-id')
            setUnselectedElement(modelId)
        })
    }

    // jointViewport.selectAll('.linkInteractionArea').on('mouseover', function(){
    //     d3.select(this.parentNode)
    //     .select('.metaLink')
    //     .classed('hovered', true)
    //     sourceId = d3.select(this).attr('data-source')
    //     targetId = d3.select(this).attr('data-target')
    // })

    // jointViewport.selectAll('.linkInteractionArea').on('mouseout', function(){
    //     d3.select(this.parentNode)
    //     .select('.metaLink')
    //     .classed('hovered', false)
    //     sourceId = d3.select(this).attr('data-source')
    //     targetId = d3.select(this).attr('data-target')
    // })

    // jointViewport.selectAll('.linkInteractionArea').on('click', function(){
    //     metaLink = d3.select(this.parentNode).select('.metaLink')
    //     sourceId = d3.select(this).attr('data-source')
    //     targetId = d3.select(this).attr('data-target')
        
    //     if (metaLink.classed('selected')){
    //         setUnselectedEdge(metaLink.attr('id'), sourceId, targetId)

    //     } else {
    //         setSelectedEdge(metaLink.attr('id'), sourceId, targetId)
    //     }
    // })

}