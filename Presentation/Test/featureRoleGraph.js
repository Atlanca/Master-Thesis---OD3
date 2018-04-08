// Create the input graph
var g = new dagreD3.graphlib.Graph().setGraph({rankdir: "RL"})
  .setDefaultEdgeLabel(function() { return {}; });

//Here we"re setting nodeclass, which is used by our custom drawNodes function
//below.
var i = 1;

var CSS_COLOR_NAMES = ['#FE5F55', '#777DA7', '#94C9A9', '#C6ECAE','#885053'];

var color_count = 0;

function entitiesToList(structureList, list){
  if(structureList instanceof Array){
    structureList.forEach(function(item){
      list.push(item)
      if ('children' in item[1]){
        entitiesToList(item[1]['children'], list)
      }
    })
  }
}

function recursiveAddEdges(structureList, parent=null){
  if(structureList instanceof Array){
    structureList.forEach(function(item){
      if (parent != null){
        g.setEdge(parent[1]['object'], item[1]['object'], {label: item[0], curve: d3.curveBasis})
      }
      if ('children' in item[1]){
        recursiveAddEdges(item[1]['children'], item)
      }
    })
  }
}

function getColor(){
  return CSS_COLOR_NAMES[color_count++]
}

var datalist = []
entitiesToList(featureRoleData, datalist)

typeColor = {}
datalist.forEach(function(d){
  typeColor[d[1]['type']] = ''
})
for (key in typeColor){
  typeColor[key] = getColor()
}

var states = {}
  
for (var key in featureRoleData){
  states[key] = {
    id: "node_" + key,
    class: "box",
    style: "fill: #70b8ff",
    title: ""
  }
  
  typeColor = {}
  featureRoleData[key].forEach(function(e){
    typeColor[e[1]['type']] = ''
  })

  for (type in typeColor) {
    typeColor[type] = getColor()
  }

  featureRoleData[key].forEach(function(e){
    description = ""
    e[1]['dataTypeProperties'].forEach(function(data) {
      
      text = data[1].substring(0,100)
      if (text.length < data[1].length) {
        text += "..."
      }

      description += "<p>"+data[0]+": "+text+"</p>"
    })

    states[e[1]['object']] = {
      id: "node_" + e[1]['object'],
      title: description,
      style: "fill: " + typeColor[e[1]['type']]

    }
    
  })
}

//Add states to the graph, set labels, and style
Object.keys(states).forEach(function(state) {
var value = states[state];
value.label = state;
value.rx = value.ry = 5;
g.setNode(state, value);
});

//Set up the edges

for(var key in featureRoleData) {
if (key != "Feature") {
    g.setEdge(key, 'purchase_products', {curve: d3.curveBasis})
}

featureRoleData[key].forEach(function(e) {
    g.setEdge(e[1]['object'], key, {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
})
}

// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("#featureRoleGraph"),
    inner = svg.append("g");

// Set up zoom support
var zoom = d3.zoom()
    .on("zoom", function() {
      inner.attr("transform", d3.event.transform);
    });
svg.call(zoom);

// Run the renderer. This is what draws the final graph.
render(inner, g);

// Center the graph
var initialScale = 0.75;
svg.call(zoom.transform, d3.zoomIdentity.translate((svg.attr("width") - g.graph().width * initialScale) / 2, 20).scale(initialScale));

for(var element in states) {
  node = document.getElementById(states[element]['id']).setAttribute('title', "<p>" + element + "</p>" + "<p>" + states[element]['title'] + "</p>")
}

tippy('.node')

svg.selectAll("g.node").on("click", function(id){
  document.getElementById(id).scrollIntoView();
});

svg.attr('height', g.graph().height * initialScale + 40);