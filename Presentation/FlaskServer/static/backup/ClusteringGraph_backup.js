//--------------------------------------------------------------------
// MAIN RENDERER FUNCTION
//--------------------------------------------------------------------
function buildDiagram(structure, view){
    // Initialize the input graph
    var g = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({edgesep: 50, ranksep: 100, nodesep: 50, rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

    var entityToNodeIdMap = {}
    entityToNodeIdMap[view] = {}

    // Adding clusters
    structure.entities.forEach(function(e){
        // Create invisible entity type clusters
        g.setNode(getNameOfUri(e.type), {style:'fill:none;opacity:0;border:none;stroke:none'})

        // Create clusters for architectural views, sets them as parent to entity type clusters
        views.forEach(function(v){
            e.supertypes.forEach(function(s){
                if(s.includes(v)){
                    if(!g.nodes().includes(v))
                        g.setNode(v, {label: v + ' view', style: 'fill:' + ONTOLOGY_COLORS[v] + ';stroke:' + ONTOLOGY_COLORS[v] , clusterLabelPos: 'top'})
                    g.setParent(getNameOfUri(e.type), v)
                }
            }) 
        })
    })

    // Creates entities and sets parent clusters for entity types, views and ontology categories accordingly
    structure.entities.forEach(function(e){
        Object.keys(ontologyCategories).forEach(function(oc){
            e.supertypes.forEach(function(s){
                ontologyCategories[oc].forEach(function(type){
                    if(s.includes(type)){
                        if(!g.nodes().includes(oc)){
                            g.setNode(oc, {label: oc, id:oc, style: 'fill:' + ONTOLOGY_COLORS[oc] + ';stroke:' + ONTOLOGY_COLORS[oc], clusterLabelPos: 'top'})
                        }
                        // Sets parents
                        parent = g.parent(getNameOfUri(e.type))
                        if(parent && parent != oc){
                            g.setParent(parent, oc)
                        } else {
                            g.setParent(getNameOfUri(e.type), oc)
                        }
                    }
                })
            })
        })
    })

    // Sets parent for entities to relative entity type cluster
    structure.entities.forEach(function(e){ 
        if(e.uri.includes('dummy_')){
            if(Object.keys(ontologyCategories).includes(e.type)){
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), label: getNameOfEntity(e), width: 800, style: 'fill:' + getEntityColor(e)})
            }else{
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), label: getNameOfEntity(e), width: 500, style: 'fill:' + getEntityColor(e)})
            }
        }else{
            g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), label: getNameOfEntity(e), style: 'fill:' + getEntityColor(e)})
            entityToNodeIdMap[view][getNameOfUri(e.uri)] = e
        }
        g.setParent(getNameOfUri(e.uri), getNameOfUri(e.type))
        
    })

    // Create edges for all entities
    structure.relations.forEach(function(r){
        g.setEdge(getNameOfUri(r.source), getNameOfUri(r.target), {class:'in-' + getNameOfUri(r.target) + ' out-' + getNameOfUri(r.source), label: r.name, 
        curve: d3.curveBasis})
        //  style: "stroke-dasharray: 10,10;",
        // arrowheadStyle: "fill: #bec6d8; stroke-width:0",
        })
    
    // Rounding edges of all entity nodes
    g.nodes().forEach(function(v) {
        var node = g.node(v);
        node.rx = 5
        node.ry = 5
    });

    // Create the renderer
    var render = new dagreD3.render();

    // Set up an SVG group so that we can translate the final graph.
    var svg = d3.select('.' + view + '.interactive_diagram_svg'),
    svgGroup = svg.append("g");

    // Set up zoom support
    var zoom = d3.zoom()
    .on("zoom", function() {
    svgGroup.attr("transform", d3.event.transform);
    });

    //Disable double click zoom
    svg.call(zoom).on("dblclick.zoom", null);

    // Run the renderer. This is what draws the final graph.
    render(d3.select('.' + view + ".interactive_diagram_svg").select('g'), g);

    // -----------------------------------------------------------------------------------------
    // Beneath this point, we are adding actions to the rendered graph and making it prettier
    // -----------------------------------------------------------------------------------------

    // Make ontology layers to be positioned behind everything
    Object.keys(ontologyCategories).forEach(function(oc){
        clusters = d3.select('.interactive_diagram.' + view).select('.clusters')
        cluster = d3.select('.interactive_diagram.' + view).select('#' + oc)
        if(cluster.node()){
            clusters.node().insertBefore(cluster.node(), clusters.node().childNodes[0])
        }
    })

    // Lighten the colors a bit
    d3.select('.interactive_diagram.' + view)
    .selectAll('rect')
    .each(function(){
        color = d3.select(this).style('fill')
        colorhsl = tinycolor(color).toHsl()
        colorhsl.l = 0.7
        d3.select(this).style('fill', tinycolor(colorhsl).toHexString())
        // recursiveLighten(d3.select(this))
    })

    // Lighten the colors of the clusters
    lightenClusters(0.9)

    // Add logic for highlighting relations and entities
    var toggleOn = ''
    selectedNodeColor = {id:'', color:''}
    highlightNodepathsOnclick()

    // Resizing clusters to make them more consistent in size
    resizeClusters()

    setClusterActions()

    // Give nodes tooltips on hover
    setTitleToNodes()
    tippy('.nodeRect')

    // Create dropdown logic for the arrow button beside the node
    setNodeDropdownLogic()

    // Scale the diagram to fit the screen
    scaleDiagram()

    //Resize dummy and style dummy nodes
    resizeDummyNodes()

    //--------------------------------------------------------------------
    // BENEATH THIS POINT THERE ARE ONLY HELPER FUNCTIONS
    //--------------------------------------------------------------------

    //--------------------------------------------------------------------
    // Helpers for building the graph
    //--------------------------------------------------------------------

    function getNameOfEntity(entity){
        if(entity.label){
            return entity.label
        }else{
            return getNameOfUri(entity.uri)
        }
    }

    function getPrettyName(string){
        name = ''
        for(i in string){
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

    function getSubTree(startEntityUri, list, forward){
        startEntityUri = getNameOfUri(startEntityUri)
        structure.relations.forEach(function(rel){
            if(forward) {
                if(getNameOfUri(rel.source) == startEntityUri){
                    getSubTree(rel.target, list, true)
                    list.push(rel)
                }
            }else{
                if(getNameOfUri(rel.target) == startEntityUri){
                    getSubTree(rel.source, list, false)
                    list.push(rel)
                }
            }
        })
        return list
    }

    //--------------------------------------------------------------------
    // Helpers for making the graph pretty
    //--------------------------------------------------------------------

    function lightenClusters(targetL){
        //Lighten the clusters
        d3.select('.interactive_diagram.' + view).selectAll('.cluster')
        .select('rect')
        .each(function(){
            color = d3.select(this).style('fill')
            newColor = tinycolor(color).toHsl()
            newColor.l = targetL

            newColorFill = tinycolor(newColor).toHex().toString()
            
            newColor.l = targetL - 0.1
            newColorStroke = tinycolor(newColor).toHex().toString()

            d3.select(this).style('fill', newColorFill)
            d3.select(this).style('stroke', newColorStroke)
        })
    }

    function recursiveLighten(rect){
        color = rect.style('fill')
        if(tinycolor(rect.style('fill')).isDark()){
            rect.style('fill', tinycolor(color).lighten(10).toString())
            recursiveLighten(rect)
        }
    }

    function scaleDiagram(){
        svgBCR = d3.select('.interactive_diagram.' + view).select('svg').node().getBoundingClientRect()
        gBBox = d3.select('.interactive_diagram.' + view).select('.output').node().getBBox()
        abswidth = Math.abs(svgBCR.width - gBBox.width)
        absheight = Math.abs(svgBCR.height - gBBox.height)

        if(absheight < abswidth){
            widthScale = svgBCR.width / gBBox.width
            d3.select('.interactive_diagram.' + view).select('.output')
            .style('transform','scale(' + widthScale + ')')
        }else{
            heightScale = svgBCR.height / gBBox.height
            d3.select('.interactive_diagram.' + view).select('.output')
            .style('transform','scale(' + heightScale + ')')
        }
    }

    function setTitleToNodes(){
        structure.entities.forEach(function(e){
            d3.select('.interactive_diagram.' + view)
            .select('#' + getNameOfUri(e.uri))
            .select('.nodeRect')
            .attr('title', formatToolTip(e))
        })
    }

    function formatToolTip(entity){
        description = entity.dataTypeProperties[0]
        if(description && getNameOfUri(description[0]).includes('Description')){
        description = description[1]
        } else {
            description = ''
        }
        if(description.length > 200){
            description = description.substring(0,200) + '...'
        }
        tooltip='<p><b>Type: </b>' + getPrettyName(getNameOfUri(entity.type)) + '</p>' +
                '<p><b>Name: </b>' + getNameOfEntity(entity) + '</p>' +
                '<p><b>URI: </b>' + getNameOfUri(entity.uri) + '</p>' +
                '<p>' + description + '</p>'
        return tooltip
    }

    function highlightRelations(entityName){  
        relations = getSubTree(entityName, [], true)
        Array.prototype.push.apply(relations, getSubTree(entityName, [], false))

        relations.forEach(function(rel){
            inClass = '.in-' + getNameOfUri(rel.target)
            outClass = '.out-' + getNameOfUri(rel.source)

            d3.select('.interactive_diagram.' + view)
            .select(inClass + outClass)
            .classed('selected', true)  
        })
    }

    function unlightRelations(){
        d3.select('.interactive_diagram.' + view)
        .selectAll('.edgePath')
        .classed('selected', false)
    }

    function resizeClusters(){
        largestYtop = 0
        largestYbot = 0
        d3.select('.interactive_diagram.' + view).selectAll('.cluster').each(function(){
            currentBBox = d3.select(this).node().getBBox()
            if(currentBBox.y < largestYtop){
                largestYtop = currentBBox.y
            }
            if(currentBBox.height + Math.abs(currentBBox.y) > largestYbot){
                largestYbot = currentBBox.height + Math.abs(currentBBox.y)
            }
        })
        largestYbot = largestYbot - Math.abs(largestYtop) + 100
        
        clusterTransform = d3.select('.interactive_diagram.' + view).select('.cluster')
                            .attr('transform')
                            .replace('translate(', '')
                            .replace(')','')
                            .split(',')
        clusterTransformY = parseFloat(clusterTransform[1])
        
        d3.select('.interactive_diagram.' + view).selectAll('.cluster').each(function(){ 
            currentTransform = d3.select(this)
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
    
        d3.select('.interactive_diagram.' + view).selectAll('.cluster')
        .select('rect').attr('y', largestYtop - 50)
        .attr('height',largestYbot)

        // Make all clusters a bit larger in height
        heightDelta = 100
        d3.select('.interactive_diagram.' + view).selectAll('.cluster').each(function(){
            cluster = d3.select(this)
            if(!cluster.empty()){
                clusterHeight = parseFloat(cluster.select('rect').attr('height'))
                clusterY = parseFloat(cluster.select('rect').attr('y'))
                cluster.select('rect')
                .attr('height', clusterHeight + heightDelta) 
                .attr('y', clusterY - heightDelta/2) 
            }
        })

        // Make ontology category clusters larger in height in comparison to all other clusters
        Object.keys(ontologyCategories).forEach(function(oc){
            cluster = d3.select('.interactive_diagram.' + view).select('#' + oc)
            heightDelta = 150
            if(!cluster.empty()){
                clusterHeight = parseFloat(cluster.select('rect').attr('height'))
                clusterY = parseFloat(cluster.select('rect').attr('y'))
                cluster.select('rect')
                .attr('height', clusterHeight + heightDelta) 
                .attr('y', clusterY - heightDelta/2) 
            }
        })

        // Style labels
        d3.select('.interactive_diagram.' + view)
        .selectAll('.cluster')
        .each(function(c){
            clusterBBox = d3.select(this).node().getBBox()
            labelBBox = d3.select(this).select('.label').node().getBBox()

            // Center labels in cluster
            d3.select(this)
            .select('.label')
            .select('g')
            .attr('transform', 'translate(' + labelBBox.x + ',' + (clusterBBox.y + 10) + ')')
            
            // Set color of label
            color = d3.select(this).select('rect').style('stroke')
            d3.select(this)
            .select('text')
            .style('fill', tinycolor(color).darken(25).toString())
        })

        // Rounder corners of clusters
        d3.select('.interactive_diagram.' + view)
        .selectAll('.cluster')
        .select('rect')
        .attr('rx',50)
        .attr('ry',50)
    }
    
    function setClusterActions(){
        //Label onclick
        d3.select('.interactive_diagram.' + view)
        .selectAll('.cluster')
        .select('.label')
        .on('click', function(){
            rect = d3.select(this.parentNode).select('rect')
            parent = d3.select(this.parentNode)
    
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
    
                parent
                .classed('unselected', false)
                .classed('selected', true)
            }
        })
    }

    //Resizes and styles dummy nodes 
    function resizeDummyNodes(){
        clusterBBox = d3.select('.interactive_diagram.' + view).select('.cluster').node().getBBox()
        d3.select('.interactive_diagram.' + view)
        .selectAll('.node')
        .each(function(){
            id = d3.select(this).attr('id')

            // Define colors for styling the dummy nodes
            color = d3.select(this).select('rect.nodeRect').style('fill')
            
            fillhsl = tinycolor(color).toHsl()
            fillhsl.l = 0.9
           
            strokehsl = tinycolor(color).toHsl()
            strokehsl.l = 0.78
           
            texthsl = tinycolor(color).toHsl()
            texthsl.l = 0.5

            if (id.includes('dummy_') ){
                nodeRect = d3.select(this).select('rect.nodeRect')
                
                // Set styling of the dummy nodes
                nodeRect
                .attr('rx', 40)
                .attr('ry', 40)
                .style('fill', tinycolor(fillhsl).toHexString())
                .style('stroke', tinycolor(strokehsl).toHexString())
                
                d3.select(this)
                .classed('dummy', true)
                .select('text')
                .style('fill', tinycolor(texthsl).toHexString())

                //Center the labels in the clusters
                labelBBox = d3.select(this).select('.label').select('g').node().getBBox()
                d3.select(this)
                .select('.label')
                .select('g')
                .attr('transform', 'translate(' + -labelBBox.width/2 + ',0)')

                // Set the height of the clusters
                // If the type of the dummy is not a ontology category, make it smaller
                isOntCategory = false
                structure.entities.forEach(function(e){
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

    function highlightNodepathsOnclick(){
        //ADD ACTIONS THE NODE RECTANGLES
        d3.select('.interactive_diagram.' + view).selectAll('.node')
        .select('rect')
        .attr('class', 'nodeRect')
        .on('click', function(){
            thisClass = d3.select(this.parentNode).attr('id')
            parent = d3.select(this.parentNode)
            if(!parent.classed('selected')){
                unlightRelations()
                highlightRelations(thisClass)
                d3.select('.interactive_diagram.' + view)
                .selectAll('.node.selected')
                .classed('selected', false)

                d3.select(this.parentNode)
                .classed('selected', true)
            }else{
                unlightRelations()
                d3.select(this.parentNode)
                .classed('selected', false)
            }
        })
    }

    function setNodeDropdownLogic(){
        d3.select('.interactive_diagram.' + view).selectAll('.node').each(function(node){
            if(d3.select(this).attr('id').includes('dummy_')){
                return
            }

            //CREATE DROP-DOWN BUTTON FOR NODES
            nodeWidth = parseFloat(
                d3.select(this)
                .select('rect')
                .attr('width'))
            nodeHeight = parseFloat(
                d3.select(this)
                .select('rect')
                .attr('height'))
            rectColor = d3.select(this)
                .select('rect')
                .style('fill')
            
            d3.select(this)
            .select('rect')
            .attr('width', nodeWidth + nodeHeight)

            d3.select(this)
            .append("rect")
            .attr('class', 'nodeButton')
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
                    .attr('class', 'drop-down_container')
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
                    item_counter = 0
                    function addDropdownItem(parent, name, callback=null){
                        d3.select(parent.parentNode)
                        .append('rect')
                        .attr('class', 'drop-down_item')
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
                        .attr('class', 'drop-down_item_text')
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
                        id = d3.select(object.parentNode).attr('id')
                        createEmptyPopup()
                        input = entityToNodeIdMap[view][id].diagrams
                        $.post('popup/diagram', {'figure': input}, function(data){
                            addPopupContent(data)
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
            nodeButton = d3.select(this).select('.nodeButton')
            x = parseFloat(nodeButton.attr('x'))
            y = parseFloat(nodeButton.attr('y'))
            width = parseFloat(nodeButton.attr('width'))
            arrowSize = 8
            points = (x + width/2) + ',' + 
                     (y + arrowSize + nodeHeight/2) + ' ' + 
                     (x + width/2) + ',' +
                     (y - arrowSize + nodeHeight/2) + ' ' + 
                     (x + arrowSize + width/2) + ',' + 
                     (y + nodeHeight/2)
        
            d3.select(this)
            .append("polygon")
            .attr('class', 'drop-down_arrow')
            .attr('points', points)
        })

    }

    function createEmptyPopup(){
        width = 80
        height = 90
        d3.select('body')
        .append('div')
        .attr('id', 'popup-background')
        .attr('class', 'popup')
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

    function addPopupContent(popupContent){
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

}

