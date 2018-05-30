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
        g.setNode(getNameOfUri(e.type), {label: getNameOfUri(e.type), clusterLabelPos: 'top', style:'fill:lightgray;opacity:1;border:black;stroke:gray'})

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

    gh = new graphHelper(structure, view, entityToNodeIdMap)

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
    })
    
    // Lighten the colors of the clusters
    gh.lightenClusters(0.9)

    // Add logic for highlighting relations and entities
    var toggleOn = ''
    selectedNodeColor = {id:'', color:''}


    gh.highlightNodepathsOnclick()

    gh.setClusterActions()

    // Give nodes tooltips on hover
    gh.setTitleToNodes()
    tippy('.nodeRect')

    // Create dropdown logic for the arrow button beside the node
    gh.setNodeDropdownLogic()

    // Scale the diagram to fit the screen
    gh.scaleDiagram()
}

