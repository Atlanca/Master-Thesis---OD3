// Create the input graph

var g = new dagreD3.graphlib.Graph({compound:true})
  .setGraph({edgesep: 10, ranksep: 100, nodesep: 50})
  .setDefaultEdgeLabel(function() { return {}; });

var CSS_COLOR_NAMES = ["AliceBlue","AntiqueWhite","Aqua","Aquamarine","Azure","Beige","Bisque","Black","BlanchedAlmond","Blue","BlueViolet","Brown","BurlyWood","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Cornsilk","Crimson","Cyan","DarkBlue","DarkCyan","DarkGoldenRod","DarkGray","DarkGrey","DarkGreen","DarkKhaki","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Grey","Green","GreenYellow","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYellow","LightGray","LightGrey","LightGreen","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","White","WhiteSmoke","Yellow","YellowGreen"];
var takenColorId = 0

function getRandomColor(){
    takenColorId = (takenColorId+25)%147
    return CSS_COLOR_NAMES[takenColorId]
}

var skipNodes = ['Diagram', 'Stakeholder', 'UserStory', 'Stereotype']
var architectureLayering = {'Architecture' : ['Package', 'ClassEntity', 'ClassPackage', 'Role', 'ArchitecturalPattern'],
                            //'Requirement' : ['UseCase', 'Feature', 'FunctionalRequirement', ''],  
                            //'Rationale' : ['DesignOption','Technology','Constraint', 'Argument','Assumption'], 
                            'Implementation' : []}
var views = {'Logical' : ['Package'],
             'Development' : ['ClassEntity', 'ClassPackage'],
             'High level' : ['ArchitecturalPattern', 'Role']
            }
            
var allInverseRelations = ['compriseOf', 'realizedBy', 'roleImplementedBy', 'verifies', 
                           'resultsIn', 'causes', 'hasAlternative', 'implements']
var typeColors = {}
var addedNodes = []
allObjects.forEach(function(object) {
    for (key in architectureLayering){
        if(architectureLayering[key].includes(object['type'])){
            
            // coloring
            if(!Object.keys(typeColors).includes(object['type'])){
                typeColors[object['type']] = getRandomColor()
            }
            
            // addnode
            g.setNode(object['object'], {width:150, height:70, style:'fill:'+typeColors[object['type']]})
           
            // add types invisible
            g.setNode(object['type'], {style: 'fill:' + typeColors[object['type']] + '; fill-opacity: 0; stroke-width: 0px;'})
            g.setParent(object['object'], object['type'])
            
            // add view layering
            Object.keys(views).forEach(function(view) {
                g.setNode(view, {label:view, style: 'fill:' + getRandomColor() + '; fill-opacity: 0.25; stroke-width: 1px;', clusterLabelPos: 'top'})
                if (views[view].includes(object['type'])) {
                    g.setParent(object['type'], view)
                }
            })   
            
            addedNodes.push(object['object'])
        }
    }
})


allRelations.forEach(function(relation){
    if(addedNodes.includes(relation[0]) && 
    addedNodes.includes(relation[2]) && 
    allInverseRelations.includes(relation[1]))
    g.setEdge(relation[0], relation[2], {label: relation[1], curve: d3.curveBasis})
})

g.nodes().forEach(function(v) {
    var node = g.node(v);
    // Round the corners of the nodes
    node.rx = node.ry = 5; 
});

// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("svg"),
svgGroup = svg.append("g");


// Set up zoom support
var zoom = d3.zoom()
.on("zoom", function() {
    svgGroup.attr("transform", d3.event.transform);
});
svg.call(zoom);

// Run the renderer. This is what draws the final graph.
render(d3.select("svg g"), g);

// Center the graph
var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
svg.attr("height", g.graph().height + 40);

breakLabels()
var originalColor = ''
d3.selectAll('.cluster').select('rect').attr('rx', '45').attr('ry', '45')
d3.selectAll('.node').select('rect').on('mouseover', function(){
    style = d3.select(this).attr('style')
    console.log(style)
    if(style != 'fill:green'){
        originalColor = style.substring(5, style.length)
        d3.select(this).attr('style', 'fill:white')
    }
}).on('mouseout', function(){
    d3.select(this).attr('style','fill:'+originalColor)
    originalColor = ''
})

function breakLabels(){
    brokenString = {}
    texts = d3.selectAll(".node .label").select("text").select('tspan')
    texts.each(function(e){
        if(e.length > 15){
            brokenString['first'] = e.substring(0,e.length/2)
            brokenString['second'] = e.substring(e.length/2,e.length)
            length = d3.select(this.parentNode.parentNode.getBBox().width)._groups[0][0]
            d3.select(this).attr('y', '-0.7em').attr('x', length/4).html(brokenString['first'])
            d3.select(this.parentNode).insert('tspan').attr('dy','1.4em').attr('x',length/4).html(brokenString['second'])
            
        }
    })
}