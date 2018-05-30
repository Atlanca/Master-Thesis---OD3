//--------------------------------------------------------------------
// MAIN RENDERER FUNCTION
//--------------------------------------------------------------------
function buildDiagram(structure, view){
    // Initialize the input graph
    var g = new dagreD3.graphlib.Graph({compound:true})
    .setGraph({edgesep: 50, ranksep: 100, nodesep: 50, rankdir: 'LR'})
    .setDefaultEdgeLabel(function() { return {}; });

    var entityIndexToRemove = []
    var diagramEntities = []
    //Make a copy of the structure, to keep the original
    var originalStructure = JSON.parse(JSON.stringify(structure));
    
    // Variables for the replacementEntity
    // The replacement entity is used as a placeholder for showing the image diagram
    var replacementEntity;
    var requiredWidth = 2000
    var replacementImageHeight = 622
    var replacementImageWidth = 598
    var replacementImageScale = 2000/598

    // Loop through all entities to
    // 1. Find an entity to use as a placeholder for the image
    // 2. Identify all entities to be removed
    structure.entities.forEach(function(entity, i){
        supertypes = entity.supertypes.map(st => getNameOfUri(st))
        if(supertypes.includes('Logical')){
            // Use the first entity found that belongs 
            // to the image as replacement entity
            if(!replacementEntity){
                replacementEntity = entity
            }else{
                entityIndexToRemove.push({'index': i, 'entity': entity})
            }
            diagramEntities.push(entity)
        } 
    })

    // Removes all entities that belong to the diagram
    entityIndexToRemove.forEach(function(pair, i){
        delete structure.entities[pair.index]
    })

    // Change the the edges to reference the replacement entity instead of
    // the removed entities
    var removedEntityUris = entityIndexToRemove.map(pair => pair.entity.uri)
    structure.relations.forEach(function(relation){
        if(removedEntityUris.includes(relation.source)){
            relation.source = replacementEntity.uri
        } else if (removedEntityUris.includes(relation.target)) {
            relation.target = replacementEntity.uri
        }
    })

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
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                width: 800, 
                                                style: 'fill:' + getEntityColor(e)})
            }else{
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                width: 500, 
                                                style: 'fill:' + getEntityColor(e)})
            }
        }else{
            // The replacement entity is used as a placeholder for the image. 
            if (replacementEntity && e.uri == replacementEntity.uri) {
                g.setNode(getNameOfUri(e.uri), {id: 'dummy_' + getNameOfUri(e.uri), 
                                                label: '',
                                                width: replacementImageWidth * replacementImageScale, 
                                                height: replacementImageHeight * replacementImageScale})
            } else {
                g.setNode(getNameOfUri(e.uri), {id: getNameOfUri(e.uri), 
                                                label: getNameOfEntity(e), 
                                                style: 'fill:' + getEntityColor(e)})
            }
            entityToNodeIdMap[view][getNameOfUri(e.uri)] = e
        }
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

    //TODO: Make general. Hard coded for now.
    var cart = d3.select('.interactive_diagram.' + view + ' #dummy_Cart')
    var nodeWidth = 113 * replacementImageScale
    var nodeHeight = 100
    var imageNodePosition = {'x': 179, 'y': 239}
    
    createFixedNode('Cart' ,cart, nodeHeight, nodeWidth, imageNodePosition)

    nodeWidth = 136 * replacementImageScale
    nodeHeight = 100
    var imageNodePosition = {'x': 168, 'y': 422}

    createFixedNode('Order', cart, nodeHeight, nodeWidth, imageNodePosition)


    //Remove edges
    var edgePaths = document.querySelector('.interactive_diagram.' + view + ' .edgePaths')
    var edgeLabels = document.querySelector('.interactive_diagram.' + view + ' .edgeLabels')

    var removeRecursively = function (list1, list2) {
        for (var i = 0; i < list1.children.length; i++) {
            if (list1.children[i].classList.contains('in-Cart') || list1.children[i].classList.contains('out-Cart') ) {
                list1.removeChild(list1.children[i])
                list2.removeChild(list2.children[i])
                removeRecursively(list1, list2)
                return
            }
        }
    }

    removeRecursively(edgePaths, edgeLabels)

    if (view == 'logical'){
        var imageDiagram = d3.select('.interactive_diagram.' + view + ' #dummy_Cart')
        originalStructure.relations.forEach(function(rel){
            diagramEntities.forEach(function(entity){
                if(getNameOfUri(rel.source) == getNameOfUri(entity.uri) || getNameOfUri(rel.target) == getNameOfUri(entity.uri)){
                    var currentSource = d3.select('.interactive_diagram.' + view + ' #' + getNameOfUri(rel.source))
                    var currentTarget = d3.select('.interactive_diagram.' + view + ' #' + getNameOfUri(rel.target))
                    
                    gh.createEdge(imageDiagram, rel.name, currentSource, currentTarget)
                }
            })
        })
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
    gh.lightenClusters(0.9)

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

    // Create dropdown logic for the arrow button beside the node
    gh.setNodeDropdownLogic()

    // Scale the diagram to fit the screen
    gh.scaleDiagram()

    //TODO: Make this general
    //1. Removes dummy node from 'nodes' cluster
    //2. Adds the image diagram to the dummy node
    //3. Creates new group and adds the image diagram node to that group
    var nodes = document.querySelector('.interactive_diagram.' + view + ' .nodes')
    var node = document.querySelector('.interactive_diagram.' + view + ' #dummy_Cart')
    var rect = document.querySelector('.interactive_diagram.' + view + ' #dummy_Cart .nodeRect')
    
    if (node) {
        var svgimg = document.createElementNS('http://www.w3.org/2000/svg','image');
        svgimg.setAttributeNS('http://www.w3.org/1999/xlink','href','/static/images/figure_3_10.png');
        svgimg.setAttributeNS(null, 'height', rect.getAttribute('height'))
        svgimg.setAttributeNS(null, 'width', rect.getAttribute('width'))
        svgimg.setAttributeNS(null, 'x', rect.getAttribute('x'))
        svgimg.setAttributeNS(null, 'y', rect.getAttribute('y'))
        node.appendChild(svgimg)
        
        var node = nodes.removeChild(node)
        
        //Creates group
        var imageDiagramsGroup = document.createElementNS("http://www.w3.org/2000/svg", "g")
        var output = document.querySelector('.interactive_diagram.' + view + ' .output')
        
        node.className.baseVal = 'image-diagram'
        imageDiagramsGroup.className.baseVal = 'imageDiagrams'
        edgePathsGroup = document.querySelector('.interactive_diagram.' + view + ' .edgePaths')

        //Inserts group, just in front of clusters
        output.insertBefore(imageDiagramsGroup, edgePathsGroup)
        imageDiagramsGroup.appendChild(node)
    }
    //Resize dummy and style dummy nodes
    gh.resizeDummyNodes()
}

