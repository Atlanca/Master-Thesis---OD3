//--------------------------------------------------------------------
// MAIN RENDERER FUNCTION
//--------------------------------------------------------------------
entityToNodeIdMap = {}

function getViewColor(v){
    var color = ONTOLOGY_COLORS[v]
    var hsl = tinycolor(color).toHsl()
    hsl.l = 0.8
    color = tinycolor(hsl).toHexString()
    return color
}

function buildDiagram(structure, view){
    // Initialize the input graph
    var g = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({edgesep: 20, ranksep: 200, nodesep: 50, rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

    var originalStructure = structure
    entityToNodeIdMap[view] = {}

    var invisCount = 0
    var addedNodes = []
    // Adding clusters
    structure.entities.forEach(function(e){
        // Create invisible entity type clusters
        if(!addedNodes.includes(e.type) && !e.type.includes('dummy')){
            g.setNode(getNameOfUri(e.type), {label: getNameOfUri(e.type), style:'fill:' + getEntityColor(e) + ';opacity:1;', clusterLabelPos: 'top'})
            g.setNode('invisible_node_' + invisCount, {id: 'invisible_node_' + invisCount, label: getNameOfUri(e.type)})
            g.setParent('invisible_node_' + invisCount++, getNameOfUri(e.type))
            addedNodes.push(e.type)
        }
        // Create clusters for architectural views, sets them as parent to entity type clusters
        views.forEach(function(v){
            e.supertypes.forEach(function(s){
                if(s.includes(v)){
                    if(!g.nodes().includes(v)){
                        g.setNode(v, {id: v, label: v + ' view', style: 'fill:' + ONTOLOGY_COLORS[v] + ';stroke:' + ONTOLOGY_COLORS[v], clusterLabelPos: 'top'})
                    }
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
        if(e.uri.includes('dummy')){
            if(ontologyDummyCategories.includes(e.supertypes[0])){
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                width: 1000,
                                                height: 1200, 
                                                style: 'fill:' + getEntityColor(e)})
            }else{
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                width: 500,
                                                height: 600, 
                                                style: 'fill:' + getEntityColor(e)})
            }
        }else{
            g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), label: getNameOfEntity(e), style: 'fill:' + getEntityColor(e)})  
            id = getNameOfUri(e.uri)
            entityToNodeIdMap[view][id] = e 
        }
        if(e.uri != e.type)
            g.setParent(getNameOfUri(e.uri), getNameOfUri(e.type))
    })

    gh = new graphHelper(originalStructure, structure, view, entityToNodeIdMap)
    
    // Create edges for all entities
    structure.relations.forEach(function(r){
        g.setEdge(getNameOfUri(r.source), getNameOfUri(r.target), {class:'in-' + getNameOfUri(r.target) + ' out-' + getNameOfUri(r.source), label: r.name, 
        curve: d3.curveBasis})
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
    function createFixedNode(nodeId, replacementNode, nodeHeight, nodeWidth, imageNodePosition){
        if(!replacementNode.empty()){
            transform = replacementNode.attr('transform')
            transformValues = gh.getTransformation(transform)
            cart_bbox = replacementNode.node().getBBox()
            translate_x = transformValues.translateX - cart_bbox.width/2 + imageNodePosition.x * replacementImageScale + nodeWidth/2
            translate_y = transformValues.translateY - cart_bbox.height/2 + imageNodePosition.y * replacementImageScale + nodeHeight/2
    
            d3.select('.interactive_diagram.' + view + ' .nodes')
            .append('g')
            .classed('node', true)
            .classed('diagram-node', true)
            .attr('id', nodeId)
            .attr('transform', 'translate(' + translate_x+ ',' + translate_y + ')')
            .append('rect')
            .classed('nodeRect', true)
            .attr('width', nodeWidth)
            .attr('height', nodeHeight)
            .attr('x', -nodeWidth/2)
            .attr('y', -nodeHeight/2)
            .attr('rx', 20)
            .attr('ry', 20)
            .style('fill-opacity', '0')
        }
    }
    // Make ontology views be positioned second to last
    views.forEach(function(v){
        var clusters = d3.select('.interactive_diagram.' + view).select('.clusters')
        var cluster = d3.select('.interactive_diagram.' + view).select('#' + v)
        if(cluster.node()){
            clusters.node().insertBefore(cluster.node(), clusters.node().childNodes[0])
        }
    })

    // Make ontology layers to be positioned behind everything
    Object.keys(ontologyCategories).forEach(function(oc){
        var clusters = d3.select('.interactive_diagram.' + view).select('.clusters')
        var cluster = d3.select('.interactive_diagram.' + view).select('#' + oc)
        if(cluster.node()){
            clusters.node().insertBefore(cluster.node(), clusters.node().childNodes[0])
        }
    })


    d3.select('.interactive_diagram.' + view)
    .selectAll('.node').each(function(){
        if (d3.select(this).attr('id').includes('dummy')) {
            d3.select(this)
            .classed('cluster', true)
            .classed('node', false)
            .select('rect')
            .classed('nodeRect', false)
        } else if (d3.select(this).attr('id').includes('invisible_node')) {
            d3.select(this)
            .classed('invisible_node', true)
            .classed('node', false)
            .select('rect')
            .classed('nodeRect', false)
        }
    })

    // Lighten the colors of the clusters
    gh.lightenClusters(0.85)

    // Add logic for highlighting relations and entities
    var toggleOn = ''
    selectedNodeColor = {id:'', color:''}
    gh.highlightNodepathsOnclick()

    // Resizing clusters to make them more consistent in size
    gh.resizeClusters()

    gh.setClusterActions()

    // Give nodes tooltips on hover
    gh.setTitleToNodes()
    tippy('.nodeRect')

    // Make invisible nodes invisible
    d3.selectAll('.invisible_node').each(function(node){
            d3.select(this).style('opacity', '0')
    })

    // Sets dropdown logic
    // Create dropdown logic for the arrow button beside the node
    // View diagram dropdown item logic
    var viewDiagramsFunction = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].diagrams
        $.post('http://localhost:5000/popup/diagram', {'figure': input}, function(data){
            gh.addPopupContent(data)
        })
    }

    var showPatternRationale = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri

        $.post('http://localhost:5000/structure/patternRationale', {'pattern': input}, function(structure){
            $.post('http://localhost:5000/popup/patternRationale', {'pattern': input, 'newWindowPath': '/q4/' + getNameOfUri(input)}, function(content){
                gh.addPopupContent(content, structure)
            })
        })
    }

    var showFeatureRole = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri

        $.post('http://localhost:5000/structure/featureRole', {'feature': input}, function(structure){
            $.post('http://localhost:5000/popup/featureRole', {'feature': input, 'newWindowPath': '/q1/' + getNameOfUri(input)}, function(content){
                gh.addPopupContent(content, structure)
            })
        })
    }

    var showFeatureBehavior = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri

        $.post('http://localhost:5000/structure/featureBehavior', {'feature': input}, function(structure){
            $.post('http://localhost:5000/popup/featureBehavior', {'feature': input, 'newWindowPath': '/q3/' + getNameOfUri(input)}, function(content){
                gh.addPopupContent(content, structure)
            })
        })
    }

    var showFeatureImplementation = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri

        $.post('http://localhost:5000/structure/featureImplementation', {'feature': input}, function(structure){
            $.post('http://localhost:5000/popup/featureImplementation', {'feature': input, 'newWindowPath': '/q2/' + getNameOfUri(input)}, function(content){
                gh.addPopupContent(content, structure)
            })
        })
    }

    var showPatternImplementation = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri

        $.post('http://localhost:5000/structure/patternImplementation', {'pattern': input}, function(structure){
            $.post('http://localhost:5000/popup/patternImplementation', {'pattern': input, 'newWindowPath': '/q7/' + getNameOfUri(input)}, function(content){
                gh.addPopupContent(content, structure)
            })
        })
    }

    var showDiagramFunction = function(object){                        
        gh.createEmptyPopup()
        var id = d3.select(object.parentNode).attr('id')
        var input = gh.entityToNodeIdMap[view][id].uri
        $.post('http://localhost:5000/popup/diagram', {'figure': [input]}, function(data){
            gh.addPopupContent(data)
        })
    }

    // The selection of elements that the dropdown logic should apply to
    d3.select('.interactive_diagram.' + gh.view).selectAll('.node').each(function(){
        var current = d3.select(this)
        var currentEntity = entityToNodeIdMap[view][current.attr('id')]
        if (currentEntity.diagrams.length > 0){
            gh.addNodeDropdownLogic(current, 'Show diagrams', viewDiagramsFunction)
        }
        
        currentEntity.supertypes.forEach(function(st){
            if (st.includes('Figure')){
                gh.addNodeDropdownLogic(current, 'Show this diagram', showDiagramFunction)
            }
        })

        if (currentEntity.type.includes('Feature')){
            gh.addNodeDropdownLogic(current, 'Show role', showFeatureRole)
            gh.addNodeDropdownLogic(current, 'Show behavior', showFeatureBehavior)
            gh.addNodeDropdownLogic(current, 'Show mapping to implementation', showFeatureImplementation)
        }

        if (currentEntity.type.includes('ArchitecturalPattern')){
            gh.addNodeDropdownLogic(current, 'Show rationale', showPatternRationale)
            gh.addNodeDropdownLogic(current, 'Show implementation', showPatternImplementation)
        }
        
    })

    // Scale the diagram to fit the screen
    gh.scaleDiagram()

}

