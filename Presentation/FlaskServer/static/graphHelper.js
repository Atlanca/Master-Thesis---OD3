//--------------------------------------------------------------------
// UNIVERSAL FUNCTIONS
//--------------------------------------------------------------------

var ONTOLOGY_COLORS = { 'Feature': '#af2d2d', 'Requirement': '#cc6a51', 
                        'FunctionalRequirement': '#eeb574', 
                        'NonFunctionalRequirement': '#d17f40',
                        'UseCase': '#ce9d58', 
                        'UserStory': '#b9ad5b', 
                        'Stakeholder': '#e2d15d', 
                        'Figure': '#92b177', 
                        'Diagram': '#86af38', 
                        'Sketch': '#c6d65e',
                        'ArchitecturalPattern': '#779658', 
                        'Role': '#60966b', 
                        'ArchitectureFragment': '#6bb496', 
                        'UI': '#73669b', 
                        'Logical': '#378aba', 
                        'Development': '#308f91',
                        'Physical': '#699677', 
                        'DesignOption': '#b476c4', 
                        'Technology': '#e93b99', 
                        'Argument': '#ffaece', 
                        'Constraint': '#ffaece', 
                        'Assumption': 'ffaece',
                        'Implementation': '#dbd8cb', 
                        'ImplementationClass': '#dbd8cb',
                        'ArchitectureLayer': '#6bb496', 
                        'RequirementLayer': '#af2d2d',
                        'DevelopmentStructure': '#308f91', 
                        'DevelopmentBehavior': '#308f91',
                        'LogicalStructure': '#378aba', 
                        'LogicalBehavior': '#378aba',
                        'UIStructure': '#73669b', 
                        'UIBehavior': '#73669b',
                        'PhysicalStructure': '#699677'                
                    }
                        
var views = ['Development', 'UI', 'Logical', 'Physical'] 
var ontologyCategories = {'ArchitecturalPatternLayer':  ['Role', 'ArchitecturalPattern'],
                          'ArchitectureLayer':          ['ArchitectureFragment', 'Development', 'UI', 'Physical', 'Logical'], 
                          'RequirementLayer':           ['Requirement', 'UserStory', 'UseCase', 'Feature'], 
                          'RationaleLayer':             ['DesignOption', 'Technology', 'Argument', 'Constraint', 'Assumption'], 
                          'ImplementationLayer':        ['Implementation']}

function getEntityColor(entity){
    if (ONTOLOGY_COLORS[getNameOfUri(entity.type)]){
        color = tinycolor(ONTOLOGY_COLORS[getNameOfUri(entity.type)]).toHsl()
        color.l = 0.7
        color = tinycolor(color).toHexString()
    } else {
        color = ''
        entity.supertypes.forEach(function(s){
            //TODO: find a way to better code this
            //Brighten classes of view
            
            if (ONTOLOGY_COLORS[getNameOfUri(s)]){
                if (!color)
                    color = tinycolor(ONTOLOGY_COLORS[getNameOfUri(s)]).toHsl()
                    color.l = 0.7
                    color = tinycolor(color).toHexString()
            }
        })
    }
    return color
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

function getPrettyName(string){
    var name = ''
    for(var i in string){
        if(i > 0 && string[i] == string[i].toUpperCase()){
            name += ' ' + string[i].toLowerCase()
        }else if (i == 0 && string[i] == string[i].toLowerCase()){
            name += string[i].toUpperCase()
        }else{
            name += string[i]
        }
    }
    return name
}



//--------------------------------------------------------------------
// Helpers for building the graph
//--------------------------------------------------------------------

class graphHelper {
    constructor(originalStructure, structure, view, entityToNodeIdMap){
        this.originalStructure = originalStructure
        this.structure = structure
        this.view = view
        this.entityToNodeIdMap = entityToNodeIdMap
    }
    
    getSubTree(startEntityUri, list, forward){
        self = this
        startEntityUri = getNameOfUri(startEntityUri)
        self.originalStructure.relations.forEach(function(rel){
            if(forward) {
                if(getNameOfUri(rel.source) == startEntityUri){
                    self.getSubTree(rel.target, list, true)
                    list.push(rel)
                }
            }else{
                if(getNameOfUri(rel.target) == startEntityUri){
                    self.getSubTree(rel.source, list, false)
                    list.push(rel)
                }
            }
        })
        return list
    }
    
    //--------------------------------------------------------------------
    // Helpers for making the graph pretty
    //--------------------------------------------------------------------
    
    lightenClusters(targetL){
        var self = this
        //Lighten the clusters
        d3.select('.interactive_diagram.' + self.view).selectAll('.cluster')
        .select('rect')
        .each(function(){
            var color = d3.select(this).style('fill')
            
            var newColor = tinycolor(color).toHsl()
            newColor.l = targetL
            var newColorFill = tinycolor(newColor).toHex().toString()
            
            newColor.l = targetL - 0.1
            var newColorStroke = tinycolor(newColor).toHex().toString()
    
            d3.select(this).style('fill', newColorFill)
            d3.select(this).style('stroke', newColorStroke)
        })
    }
    
    scaleDiagram(){
        var self = this
        var svgBCR = d3.select('.interactive_diagram.' + self.view).select('svg').node().getBoundingClientRect()
        var gBBox = d3.select('.interactive_diagram.' + self.view).select('.output').node().getBBox()
        var abswidth = Math.abs(svgBCR.width - gBBox.width)
        var absheight = Math.abs(svgBCR.height - gBBox.height)
    
        if(absheight < abswidth){
            var widthScale = svgBCR.width / gBBox.width
            d3.select('.interactive_diagram.' + self.view).select('.output')
            .style('transform','scale(' + widthScale + ')')
        }else{
            var heightScale = svgBCR.height / gBBox.height
            d3.select('.interactive_diagram.' + self.view).select('.output')
            .style('transform','scale(' + heightScale + ')')
        }
    }
    
    setTitleToNodes(){
        var self = this
        self.structure.entities.forEach(function(e){
            d3.select('.interactive_diagram.' + self.view)
            .select('#' + getNameOfUri(e.uri))
            .select('.nodeRect')
            .attr('title', self.formatToolTip(e))
        })
    }
    
    formatToolTip(entity){
        var self = this
        var description = entity.dataTypeProperties[0]

        if(description && getNameOfUri(description[0]).includes('Description')){
            description = description[1]
        } else {
            description = ''
        }
        if(description.length > 200){
            description = description.substring(0,200) + '...'
        }
        var tooltip='<p><b>Type: </b>' + getPrettyName(getNameOfUri(entity.type)) + '</p>' +
                '<p><b>Name: </b>' + getNameOfEntity(entity) + '</p>' +
                '<p><b>URI: </b>' + getNameOfUri(entity.uri) + '</p>' +
                '<p>' + description + '</p>'
        return tooltip
    }
    
    getIndexOfEdgePath(inClass, outClass){
        var self = this
        var currentView = document.querySelectorAll('.interactive_diagram.' + self.view)[0]
        var children = currentView.getElementsByClassName('edgePaths')[0].children
        
        for (var i = 0; i < children.length; i++){
            if(children[i].classList.contains(inClass) && children[i].classList.contains(outClass)){
                return i
            }
        }

        return -1
    }

    highlightRelationsAndEntities(entityName){  
        var self = this
        var relations = self.getSubTree(entityName, [], true)
        var selectedEdgePaths = []
        Array.prototype.push.apply(relations, self.getSubTree(entityName, [], false))
       
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.node')
        .classed('not-selected', true)
    
        relations.forEach(function(rel){
            var inClass = 'in-' + getNameOfUri(rel.target)
            var outClass = 'out-' + getNameOfUri(rel.source)
            
            selectedEdgePaths.push(self.getIndexOfEdgePath(inClass, outClass))
    
            d3.select('.interactive_diagram.' + self.view)
            .select('#' + getNameOfUri(rel.target))
            .classed('selected-secondary', true)  
            .classed('not-selected', false)

            d3.select('.interactive_diagram.' + self.view)
            .select('#' + getNameOfUri(rel.source))
            .classed('selected-secondary', true)  
            .classed('not-selected', false)
            
            d3.select('.interactive_diagram.' + self.view)
            .selectAll('.' + inClass + '.' + outClass)
            .classed('selected', true)  
        })

        d3.select('.interactive_diagram.' + self.view)
        .select('#' + entityName)
        .classed('selected', true)
        .classed('selected-secondary', false)
        .classed('not-selected', false)

        //Set class not-selected to labels that are not selected
        var currentView = document.querySelectorAll('.interactive_diagram.' + self.view)[0]
        var labelChildren = currentView.getElementsByClassName('edgeLabels')[0].children
        var pathChildren = currentView.getElementsByClassName('edgePaths')[0].children

        for(var i = 0; i < labelChildren.length; i++){
            if(!selectedEdgePaths.includes(i)){
                labelChildren[i].classList.add('not-selected')
                pathChildren[i].classList.add('not-selected')
            }
        }

    }
    
    unlightRelationsAndEntities(){
        var self = this
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.edgePath')
        .classed('selected', false)

        //Remove secondary selection class on all nodes
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.node.selected-secondary')
        .classed('selected-secondary', false)

        //Remove class not-selected from all elements in the graph
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.not-selected')
        .classed('not-selected', false)

        //Un-select all nodes in the graph
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.node.selected')
        .classed('selected', false)
    }
    
    resizeClusters(){
        var self = this
        var largestYtop = 0
        var largestYbot = 0

        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .each(function(){
            var currentBBox = d3.select(this).node().getBBox()
            if(currentBBox.y < largestYtop){
                largestYtop = currentBBox.y
            }
            if(currentBBox.height + Math.abs(currentBBox.y) > largestYbot){
                largestYbot = currentBBox.height + Math.abs(currentBBox.y)
            }
        })
        largestYbot = largestYbot - Math.abs(largestYtop) + 100
        
        var clusterTransform = d3.select('.interactive_diagram.' + self.view)
                                    .select('.cluster')
                                    .attr('transform')
                                    .replace('translate(', '')
                                    .replace(')','')
                                    .split(',')
        var clusterTransformY = parseFloat(clusterTransform[1])
        
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .each(function(){ 
            var currentTransform = d3.select(this)
                                .attr('transform')
                                .replace(/,\d+\.*\d+/, ',' + clusterTransformY) 
    
            d3.select(this)
            .attr('transform', currentTransform)
            
            // Make cluster rects wider
            d3.select(this)
            .select('rect')
            .attr('x', (parseFloat(d3.select(this)
                                    .select('rect')
                                    .attr('x')) - 25) + 'px')
    
            d3.select(this)
            .select('rect')
            .attr('width', (parseFloat(d3.select(this)
                                        .select('rect')
                                        .attr('width')) + 50) + 'px')
        })
    
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .select('rect')
        .attr('y', largestYtop - 50)
        .attr('height',largestYbot)
    
        // Make all clusters a bit larger in height
        var heightDelta = 100
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .each(function(){
            var cluster = d3.select(this)
            if(!cluster.empty()){
                var clusterHeight = parseFloat(cluster.select('rect').attr('height'))
                var clusterY = parseFloat(cluster.select('rect').attr('y'))
                cluster.select('rect')
                .attr('height', clusterHeight + heightDelta) 
                .attr('y', clusterY - heightDelta/2) 
            }
        })
    
        // Make ontology category clusters larger in height in comparison to all other clusters
        Object.keys(ontologyCategories).forEach(function(oc){
            var cluster = d3.select('.interactive_diagram.' + self.view).select('#' + oc)
            var heightDelta = 150
            if(!cluster.empty()){
                var clusterHeight = parseFloat(cluster.select('rect').attr('height'))
                var clusterY = parseFloat(cluster.select('rect').attr('y'))
                cluster.select('rect')
                .attr('height', clusterHeight + heightDelta) 
                .attr('y', clusterY - heightDelta/2) 
            }
        })
    
        // Style labels
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .each(function(c){
            var clusterBBox = d3.select(this).node().getBBox()
            var labelBBox = d3.select(this).select('.label').node().getBBox()
    
            // Center labels in cluster
            d3.select(this)
            .select('.label')
            .select('g')
            .attr('transform', 'translate(' + labelBBox.x + ',' + (clusterBBox.y + 10) + ')')
            
            // Set color of label
            var color = d3.select(this).select('rect').style('stroke')
            d3.select(this)
            .select('text')
            .style('fill', tinycolor(color).darken(25).toString())
        })
    
        // Rounder corners of clusters
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.cluster')
        .select('rect')
        .attr('rx',50)
        .attr('ry',50)
    }
    
    setClusterActions(){
        //Label onclick
        d3.select('.interactive_diagram.' + this.view)
        .selectAll('.cluster')
        .select('.label')
        .on('click', function(){
            var rect = d3.select(this.parentNode).select('rect')
            var parent = d3.select(this.parentNode)
    
            if(parent.classed('selected')){
                d3.select(this.parentNode)
                .classed('selected', false)
                .classed('unselected', true)
            }else{
                d3.selectAll('.selected')
                .each(function(){
                    d3.select(this).classed('selected', false)
                    d3.select(this).classed('unselected', true)
                })
    
                parent.classed('unselected', false)
                .classed('selected', true)
            }
        })
    }
    
    //Resizes and styles dummy nodes 
    resizeDummyNodes(){
        var self = this
        var clusterBBox = d3.select('.interactive_diagram.' + self.view).select('.cluster').node().getBBox()
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.node')
        .each(function(){
            var id = d3.select(this).attr('id')
    
            // Define colors for styling the dummy nodes
            var color = d3.select(this).select('rect.nodeRect').style('fill')
            
            var fillhsl = tinycolor(color).toHsl()
            fillhsl.l = 0.9
            
            var strokehsl = tinycolor(color).toHsl()
            strokehsl.l = 0.78
            
            var texthsl = tinycolor(color).toHsl()
            texthsl.l = 0.5
    
            if (id.includes('dummy_') ){
                var nodeRect = d3.select(this).select('rect.nodeRect')
                
                // Set styling of the dummy nodes
                nodeRect.attr('rx', 40)
                .attr('ry', 40)
                .style('fill', tinycolor(fillhsl).toHexString())
                .style('stroke', tinycolor(strokehsl).toHexString())
                
                d3.select(this)
                .classed('dummy', true)
                .select('text')
                .style('fill', tinycolor(texthsl).toHexString())
    
                //Center the labels in the clusters
                var labelBBox = d3.select(this).select('.label').select('g').node().getBBox()
                d3.select(this)
                .select('.label')
                .select('g')
                .attr('transform', 'translate(' + -labelBBox.width/2 + ',0)')
    
                // Set the height of the clusters
                // If the type of the dummy is not a ontology category, make it smaller
                var isOntCategory = false
                self.structure.entities.forEach(function(e){
                    if(e.uri.includes(id)){
                        if(Object.keys(ontologyCategories).includes(e.type)){
                            isOntCategory = true
                        }
                    }
                })
    
                if(isOntCategory){
                    nodeRect.attr('height', clusterBBox.height)
                    .attr('y', clusterBBox.y)
                }else{
                    nodeRect.attr('height', clusterBBox.height - 250)
                    .attr('y', clusterBBox.y + 125)
                }
                
            }
        })
    }
    
    //--------------------------------------------------------------------
    // Creating the logic for node actions
    //--------------------------------------------------------------------
    
    highlightNodepathsOnclick(){
        //ADD ACTIONS THE NODE RECTANGLES
        var self = this
        d3.select('.interactive_diagram.' + self.view).selectAll('.node')
        .select('rect')
        .classed('nodeRect', true)
        .on('click', function(){
            var thisClass = d3.select(this.parentNode).attr('id')
            var parent = d3.select(this.parentNode)
            if(!parent.classed('selected')){
                self.unlightRelationsAndEntities()
                self.highlightRelationsAndEntities(thisClass) 

            }else{
                self.unlightRelationsAndEntities()
                d3.select(this.parentNode)
            }
        })
    }
    
    setNodeDropdownLogic(){
        var self = this
        d3.select('.interactive_diagram.' + self.view)
        .selectAll('.node')
        .each(function(node){
            if(d3.select(this).attr('id').includes('dummy_')){
                return
            }
    
            //CREATE DROP-DOWN BUTTON FOR NODES
            var nodeWidth = parseFloat(
                            d3.select(this)
                            .select('rect')
                            .attr('width'))
            var nodeHeight = parseFloat(
                            d3.select(this)
                            .select('rect')
                            .attr('height'))
            var rectColor = d3.select(this)
                            .select('rect')
                            .style('fill')
            
            d3.select(this)
            .select('rect')
            .attr('width', nodeWidth + nodeHeight)
    
            d3.select(this)
            .append("rect")
            .classed('nodeButton', true)
            .attr('width', nodeHeight)
            .attr('height', nodeHeight)
            .attr('x', nodeWidth/2)
            .attr('y', -nodeHeight/2)
            .attr('rx', '5')
            .attr('ry', '5')
            .style('stroke', 'none')
            .style('cursor', 'pointer')
            .style('opacity', '0')
            .on('mouseover', function(){
                d3.select(this)
                .style('fill','white')
                .transition()
                .duration(200)
                .style('opacity','0.7')
            }).on('mouseout', function(){
                d3.select(this)
                .transition()
                .duration(200)
                .style('opacity','0')
            }).on('click', function(){
                nodeWidth = parseFloat(
                    d3.select(this.parentNode)
                    .select('.nodeRect')
                    .attr('width'))
                nodeHeight = parseFloat(
                    d3.select(this.parentNode)
                    .select('.nodeRect')
                    .attr('height'))
                
                //CREATE DROPDOWN RECTANGLE
                //Put the node first in the list to avoid overlapping
                this.parentNode.parentNode.appendChild(this.parentNode)
    
                function hideDropdown(){
                    d3.selectAll('.drop-down_container')
                    .transition()
                    .duration(200)
                    .attr('height', '1')
                    .transition()
                    .duration(200)
                    .attr('width','0')
                    .remove()
                    
                    d3.selectAll('.drop-down_arrow')
                    .transition()
                    .duration(100)
                    .style('fill', '#2c4c66')
                    .style('stroke', '#2c4c66')
    
                    d3.selectAll('.drop-down_item')
                    .remove()
    
                    d3.selectAll('.drop-down_item_text')
                    .remove()
                }
    
                if(d3.select(this.parentNode).select('.drop-down_container').empty()){
    
                    hideDropdown()
                    //Create drop-down box
                    d3.select(this.parentNode)
                    .append('rect')
                    .classed('drop-down_container', true)
                    .attr('x', (nodeWidth/2+nodeHeight/2)+20)
                    .attr('y', -nodeHeight/2)
                    .attr('width', '0')
                    .attr('height', '1')
                    .attr('rx','5')
                    .attr('ry','5')
                    .transition()
                    .duration(200)
                    .attr('width', '350px')
                    .transition()
                    .duration(200)
                    .attr('height', nodeHeight*3)
                    
                    //Drop-down arrow change to white
                    d3.select(this.parentNode)
                    .select('.drop-down_arrow')
                    .transition()
                    .duration(250)
                    .style('fill', 'white')
                    .style('stroke', 'white')
    
                    //Create drop-down items
                    var item_counter = 0
                    function addDropdownItem(parent, name, callback=null){
                        d3.select(parent.parentNode)
                        .append('rect')
                        .classed('drop-down_item', true)
                        .attr('id', 'drop_down_item' + item_counter)
                        .attr('x', (nodeWidth/2+nodeHeight/2)+20)
                        .attr('y', (-nodeHeight/2 + nodeHeight*item_counter))
                        .attr('width', '350px')
                        .attr('height', nodeHeight)
                        .attr('rx', 5)
                        .attr('ry', 5)
                        .on('mouseover', function(){
                            d3.select(this)
                            .transition()
                            .duration(200)
                            .style('opacity', '0.5')
                        })
                        .on('mouseout', function(){
                            d3.select(this)
                            .transition()
                            .duration(200)
                            .style('opacity', '0')
                        })
                        .on('click', function(){
                            if (callback) {
                                callback(this)
                            }
                        })
    
                        d3.select(parent.parentNode)
                        .insert('text')
                        .classed('drop-down_item_text', true)
                        .attr('id', 'drop-down_item_text' + item_counter)
                        .attr('x', (12.5 + nodeWidth/2+nodeHeight/2)+20)
                        .attr('y', (10 + nodeHeight*item_counter))
                        .transition()
                        .delay(300)
                        .duration(200)
                        .style('opacity', '1')
                        
                        d3.select(parent.parentNode)
                        .select('#drop-down_item_text' + item_counter)
                        .html(name)
    
                        item_counter++
                    }
    
                    addDropdownItem(this, 'View diagrams', function(object){                        
                        self.createEmptyPopup()
                        var id = d3.select(object.parentNode).attr('id')
                        console.log(id)
                        console.log(self.entityToNodeIdMap[self.view])
                        var input = self.entityToNodeIdMap[self.view][id].diagrams
                        $.post('http://localhost:5000/popup/diagram', {'figure': input}, function(data){
                            self.addPopupContent(data)
                        })
                    })
    
                    addDropdownItem(this, 'Explain entity', function(object){
                        
                    })
    
                    addDropdownItem(this, 'Explain relations')
    
                }else{
                    hideDropdown() 
                }
    
            })
    
            // CREATE SVG ARROW
            var nodeButton = d3.select(this).select('.nodeButton')
            var x = parseFloat(nodeButton.attr('x'))
            var y = parseFloat(nodeButton.attr('y'))
            var width = parseFloat(nodeButton.attr('width'))
            var arrowSize = 8
            var points = (x + width/2) + ',' + 
                        (y + arrowSize + nodeHeight/2) + ' ' + 
                        (x + width/2) + ',' +
                        (y - arrowSize + nodeHeight/2) + ' ' + 
                        (x + arrowSize + width/2) + ',' + 
                        (y + nodeHeight/2)
        
            d3.select(this)
            .append("polygon")
            .classed('drop-down_arrow', true)
            .attr('points', points)
        })
    
    }
    
    createEmptyPopup(){
        var width = 80
        var height = 90

        d3.select('body')
        .append('div')
        .attr('id', 'popup-background')
        .classed('popup', true)
        .style('width', '100%')
        .style('height', '100%')
        .style('opacity','0.3')
        .style('position', 'absolute')
        .style('background-color','black')
        
        d3.select('#popup-background')
        .on('click', function(){
            d3.selectAll('.popup')
            .remove()
        })
    
        d3.select('body')
        .append('div')
        .attr('id', 'popup-view')
        .attr('class','w3-light-gray w3-border w3-border-indigo popup')
        .style('position','absolute')
        .style('left', '50%')
        .style('bottom', '50%')
        .style('transform', 'translate(-50%,50%)')
        .style('width', width + "%")
        .style('height', height + "%")
    }
    
    addPopupContent(popupContent){
        d3.select('#popup-view')
        .html(popupContent)
    
        var s = document.createElement('script')
        s.src = '/static/popup-graph.js'
        document.getElementById('popup-view').appendChild(s)
    
        d3.select('#close_popup')
        .on('click', function(){
            d3.selectAll('.popup')
            .remove()
        })
    }

    getTransformation(transform) {
        // Create a dummy g for calculation purposes only. This will never
        // be appended to the DOM and will be discarded once this function 
        // returns.
        var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        
        // Set the transform attribute to the provided string value.
        g.setAttributeNS(null, "transform", transform);
        
        // consolidate the SVGTransformList containing all transformations
        // to a single SVGTransform of type SVG_TRANSFORM_MATRIX and get
        // its SVGMatrix. 
        var matrix = g.transform.baseVal.consolidate().matrix;
        
        // Below calculations are taken and adapted from the private function
        // transform/decompose.js of D3's module d3-interpolate.
        var {a, b, c, d, e, f} = matrix;   // ES6, if this doesn't work, use below assignment
        // var a=matrix.a, b=matrix.b, c=matrix.c, d=matrix.d, e=matrix.e, f=matrix.f; // ES5
        var scaleX, scaleY, skewX;
        if (scaleX = Math.sqrt(a * a + b * b)) a /= scaleX, b /= scaleX;
        if (skewX = a * c + b * d) c -= a * skewX, d -= b * skewX;
        if (scaleY = Math.sqrt(c * c + d * d)) c /= scaleY, d /= scaleY, skewX /= scaleY;
        if (a * d < b * c) a = -a, b = -b, skewX = -skewX, scaleX = -scaleX;
        return {
          translateX: e,
          translateY: f,
          rotate: Math.atan2(b, a) * 180 / Math.PI,
          skewX: Math.atan(skewX) * 180 / Math.PI,
          scaleX: scaleX,
          scaleY: scaleY
        };
    }

    // CreatingEdges
    isInImage(imageDiagramNode, node){
        var imageDiagramBBox = imageDiagramNode.getBBox()
        var nodeBBox = node.getBBox()

        var imageDiagramTransform = gh.getTransformation(imageDiagramNode.getAttribute('transform'))       
        var nodeTransform = gh.getTransformation(node.getAttribute('transform'))

        var leftBorder = imageDiagramTransform.translateX - imageDiagramBBox.width/2
        var rightBorder = imageDiagramTransform.translateX + imageDiagramBBox.width/2
        var topBorder = imageDiagramTransform.translateY - imageDiagramBBox.height/2
        var bottomBorder = imageDiagramTransform.translateY + imageDiagramBBox.height/2

        var x = nodeTransform.translateX 
        var y = nodeTransform.translateY
        
        var result = true
        
        if(x < leftBorder)
            result = false
        if(x > rightBorder)
            result = false
        if(y < topBorder)
            result = false
        if(y > bottomBorder)
            result = false

        return result
    }

    createPath(imageDiagramNode, sourceNode, targetNode, turnPoint){
        var self = this
        var sourceBBox = sourceNode.getBBox()
        var targetBBox = targetNode.getBBox()
        var imageDiagramBBox = imageDiagramNode.getBBox()

        var imageDiagramTransform = gh.getTransformation(imageDiagramNode.getAttribute('transform'))
        var sourceTransform = gh.getTransformation(sourceNode.getAttribute('transform'))
        var targetTransform = gh.getTransformation(targetNode.getAttribute('transform'))

        var leftBorder = imageDiagramTransform.translateX - imageDiagramBBox.width/2
        var rightBorder = imageDiagramTransform.translateX + imageDiagramBBox.width/2

        var sourcePos = {}
        var targetPos = {}
        var connectorPos = {}

        var isRelationLeftToRight = sourceTransform.translateX < targetTransform.translateX
        var isSourceInImage = self.isInImage(imageDiagramNode, sourceNode)
        var isTopOfImage
        
        var curveTurnPoint = 50

        // TODO: Not all cases covered. Make it more flexible.
        // Covers when relation is left to right only
        if (isRelationLeftToRight && !isSourceInImage) {
            var connectorPos = {'x': leftBorder, 'y': targetTransform.translateY}
            var sourcePos = {'x': sourceTransform.translateX + sourceBBox.width/2 + sourceBBox.height, 'y': sourceTransform.translateY}
            var horizontalEndPos = (connectorPos.x - sourceTransform.translateX) * turnPoint + sourceTransform.translateX
            var edge =  'M ' + sourcePos.x + ',' + sourcePos.y + 
                    ' H ' + horizontalEndPos + 
                    ' Q ' + (horizontalEndPos + curveTurnPoint) + ',' + sourcePos.y + ',' + connectorPos.x + ',' + connectorPos.y

        } else if (isRelationLeftToRight && isSourceInImage) {
            var connectorPos = {'x': rightBorder, 'y': sourceTransform.translateY}
            var targetPos = {'x': targetTransform.translateX - targetBBox.width/2, 'y': targetTransform.translateY}
            var horizontalStartPos = ((targetTransform.translateX - (imageDiagramTransform.translateX + imageDiagramBBox.width/2)) * (1-turnPoint) + imageDiagramTransform.translateX + imageDiagramBBox.width/2)
            var edge =  'M ' + connectorPos.x + ',' + connectorPos.y + 
                    ' Q ' + (horizontalStartPos - curveTurnPoint) + ',' + targetPos.y + ' ' + horizontalStartPos + ',' + targetPos.y +
                    ' H ' + targetPos.x
        }

        return edge
    }

    createEdge(imageDiagram, name, source, target){
        var self = this
        var edgePaths = d3.select('.interactive_diagram.' + self.view + ' .edgePaths')
        var edgeLabels = d3.select('.interactive_diagram.' + self.view + ' .edgeLabels')  
        var turnPoint = 0.8
        
        var edge = edgePaths.append('g')
        .classed('edgePath', true)
        .classed('out-' + source.attr('id'), true)
        .classed('in-' + target.attr('id'), true)
        .classed('diagram-edge', true)
        .append('path')
        .classed('path', true)
        .attr('d', self.createPath(imageDiagram.node(), source.node(), target.node(), turnPoint))

        var sourceBBox = source.node().getBBox()
        var targetBBox = target.node().getBBox()
        var imageBBox = imageDiagram.node().getBBox()
        var edgeBBox = edge.node().getBBox()

        var sourceTransform = gh.getTransformation(source.attr('transform'))
        var targetTransform = gh.getTransformation(target.attr('transform'))
        var imageDiagramTransform = gh.getTransformation(imageDiagram.attr('transform'))

        if(self.isInImage(imageDiagram.node(), source.node())){
            var startX = sourceTransform.translateX + sourceBBox.width/2 + sourceBBox.height
            var startY = sourceTransform.translateY
            var endX = imageDiagramTransform.translateX + imageBBox.width/2
            var circleX = endX
        }else{
            var startX = imageDiagramTransform.translateX - imageBBox.width/2
            var startY = targetTransform.translateY
            var endX = targetTransform.translateX - targetBBox.width/2
            var circleX = startX
        }

        
        var path = 'M ' + startX + ',' + startY + ' H ' + endX
        d3.select(edge.node().parentNode)
        .append('path')
        .classed('connector', true)
        .attr('d', path)

        d3.select(edge.node().parentNode)
        .append('circle')
        .classed('connector', true)
        .attr('r', 15)
        .attr('cx', circleX)
        .attr('cy', startY)
        
        self.createEdgeLabel(imageDiagram, name, source, target, edge, turnPoint)
    }

    createEdgeLabel(imageDiagram, name, source, target, edge, turnPoint){    
        var self = this    
        var edgeLabels = d3.select('.interactive_diagram.' + self.view + ' .edgeLabels')  

        var sourceBBox = source.node().getBBox()
        var targetBBox = target.node().getBBox()
        var imageBBox = imageDiagram.node().getBBox()
        var edgeBBox = edge.node().getBBox()

        var sourceTransform = gh.getTransformation(source.attr('transform'))
        var targetTransform = gh.getTransformation(target.attr('transform'))
        var imageDiagramTransform = gh.getTransformation(imageDiagram.attr('transform'))

        
        //Create labels
        var isSourceInImage = self.isInImage(imageDiagram.node(), source.node())
        var isRelationLeftToRight = sourceTransform.translateX < targetTransform.translateX

        // TODO: Cover all cases
        // Right now only covers relations going from left to right

        if (isRelationLeftToRight && !isSourceInImage) {
            // ABOVE
            if (sourceTransform.translateY < targetTransform.translateY) {
                console.log(sourceTransform)
                var translation = 'translate(' + (((edgeBBox.x + edgeBBox.width) - sourceTransform.translateX) * turnPoint + sourceTransform.translateX) + ',' + (edgeBBox.y) + ')'
            // BELOW
            } else {
                var translation = 'translate(' + (((edgeBBox.x + edgeBBox.width) - sourceTransform.translateX) * turnPoint + sourceTransform.translateX) + ',' + (edgeBBox.y + edgeBBox.height) + ')'
            }
        } else if(isRelationLeftToRight && isSourceInImage) {
            // ABOVE
            if (sourceTransform.translateY > targetTransform.translateY) {
                var translation = 'translate(' + ((edgeBBox.width + targetBBox.width/2) * 0.2 + edgeBBox.x) + ',' + (edgeBBox.y) + ')'
            // BELOW
            } else {
                var translation = 'translate(' + ((edgeBBox.width + targetBBox.width/2) * 0.2 + edgeBBox.x) + ',' + (edgeBBox.y + edgeBBox.height) + ')'
            }
        }

        var edgeLabel = edgeLabels.append('g')
        .classed('edgeLabel', true)
        .attr('transform', translation)
        .append('g')
        .classed('label', true)

        edgeLabel.append('text')
        .append('tspan')
        .text(name)

        var edgeLabelBBox = edgeLabel.node().getBBox()

        //Position label depending on whether the source node belongs to the image 
        if(!isSourceInImage)
            edgeLabel.attr('transform', 'translate(' + -edgeLabelBBox.width + ',' + edgeLabelBBox.height  +')')
        else
            edgeLabel.attr('transform', 'translate(' + 0 + ',' + edgeLabelBBox.height  +')')
    }
    
}

