//--------------------------------------------------------------------
// MAIN RENDERER FUNCTION
//--------------------------------------------------------------------
entityToNodeIdMap = {}
function buildDiagram(structure, view){
    // Initialize the input graph
    var g = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({edgesep: 20, ranksep: 200, nodesep: 50, rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

    var originalStructure = structure
    entityToNodeIdMap[view] = {}

    // Adding clusters
    structure.entities.forEach(function(e){
        // Create invisible entity type clusters
        g.setNode(getNameOfUri(e.type), {label: getNameOfUri(e.type), style:'fill:gray;opacity:1;', clusterLabelPos: 'top'})
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
        if(e.uri.includes('dummy')){
            if(Object.keys(ontologyCategories).includes(e.type)){
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                width: 800,
                                                height: 900, 
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

    // Make ontology layers to be positioned behind everything
    Object.keys(ontologyCategories).forEach(function(oc){
        clusters = d3.select('.interactive_diagram.' + view).select('.clusters')
        cluster = d3.select('.interactive_diagram.' + view).select('#' + oc)
        if(cluster.node()){
            clusters.node().insertBefore(cluster.node(), clusters.node().childNodes[0])
        }
    })

    // Lighten the colors a bit
    // d3.select('.interactive_diagram.' + view)
    // .selectAll('rect')
    // .each(function(){
    //     color = d3.select(this).style('fill')
    //     colorhsl = tinycolor(color).toHsl()
    //     colorhsl.l = 0.7
    //     d3.select(this).style('fill', tinycolor(colorhsl).toHexString())
    //     // recursiveLighten(d3.select(this))
    // })

    // Lighten the colors of the clusters
    gh.lightenClusters(0.9)

    // Add logic for highlighting relations and entities
    var toggleOn = ''
    selectedNodeColor = {id:'', color:''}
    gh.highlightNodepathsOnclick()

    // Resizing clusters to make them more consistent in size
    // gh.resizeClusters()

    d3.selectAll('.interactive-diagram.' + view + ' .clusters .cluster')


    gh.setClusterActions()

    // Give nodes tooltips on hover
    gh.setTitleToNodes()
    tippy('.nodeRect')

    // Create dropdown logic for the arrow button beside the node
    gh.setNodeDropdownLogic()

    // Scale the diagram to fit the screen
    gh.scaleDiagram()
    
    //Resize dummy and style dummy nodes
    // gh.resizeDummyNodes()
}

