// Create the input graph
var g = new dagreD3.graphlib.Graph().setGraph({rankdir: "LR"})
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

var roleExplanation = true

var datalist = []
entitiesToList(relImpClassesData, datalist)

typeColor = {}
datalist.forEach(function(d){
  typeColor[d[1]['type']] = ''
})
for (key in typeColor){
  typeColor[key] = getColor()
}

var states = {}

datalist.forEach(function(item){
  description = "<p>Type : " + item[1]['type'] +"</p>"
  if ('dataTypeProperties' in item[1]){
    item[1]['dataTypeProperties'].forEach(function(d){
      description += "<p>" + d[0] + " : " + d[1].substring(0,200) + "...</p>"
    })
  }

  states[item[1]['object']] = {
    id: "node_" + item[1]['object'],
    class: "box",
    style: "fill: " + typeColor[item[1]['type']],
    title: description}
})

// Add states to the graph, set labels, and style
Object.keys(states).forEach(function(state) {
  var value = states[state];
  value.label = state;
  value.rx = value.ry = 5;
  g.setNode(state, value);
});

// Set up the edges
recursiveAddEdges(relImpClassesData)

// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("#relationGraph"),
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