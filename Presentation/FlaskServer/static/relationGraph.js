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

function recursiveAddEdges(g, structureList, parent=null){
  if(structureList instanceof Array){
      structureList.forEach(function(item){
          if (parent != null){
              if(item[0]){
                  g.setEdge(parent[1]['object'], item[1]['object'], {label: item[0], curve: d3.curveBasis})
              }
          }
          if ('children' in item[1]){
              recursiveAddEdges(g, item[1]['children'], item)
          }
      })
  }
}

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

function setTextColor(){
  texts = d3.selectAll(".node .label").select("text")
  texts.each(function(text){
    nodeColor = d3.select(this.parentNode.parentNode.parentNode).select('rect').style('fill')
    nodeColor = tinycolor(nodeColor)
    if(nodeColor.isDark()){
      d3.select(this).style('fill', 'white')
    }else{
      d3.select(this).style('color', 'green')
    }
  })
}

function relationGenerateGraph(svgId, testdata){
  
  function getColor(){
      return CSS_COLOR_NAMES[color_count++]
  }
  // Create the input graph
  var g = new dagreD3.graphlib.Graph({compound:true}).setGraph({rankdir: "LR"})
  .setDefaultEdgeLabel(function() { return {}; });
  
  //Here we"re setting nodeclass, which is used by our custom drawNodes function
  //below.
  var i = 1;
  var CSS_COLOR_NAMES = ['#FE5F55', '#777DA7', '#94C9A9', '#C6ECAE','#885053', '#4ABDAC', 
                         '#FCA41A', '#DFDCE3', '#0375B4', '#007849', '#C0B283', 
                         '#EEAA7B', '#6D7993'];
  var views = {'Logical' : ['Package'],
              'Development' : ['ClassEntity', 'ClassPackage'],
              'Rationale' : ['Technology']
            }
  var ontology = {'Architecture' : ['Logical', 'Development', 'ClassPackage', 'Role', 'ArchitecturalPattern'],
                  //'Requirement' : ['UseCase', 'Feature', 'FunctionalRequirement', ''],  
                  //'Rationale' : ['DesignOption','Technology','Constraint', 'Argument','Assumption'], 
                  //'Implementation' : []}
          }

  var color_count = 0;
  var datalist = []
  entitiesToList(testdata, datalist)
  
  Object.keys(ontology).forEach(function(o){
    g.setNode(o, {label:o, clusterLabelPos:'top', style:'fill:' + getColor()})
  })

  Object.keys(views).forEach(function(v){
    color = getColor()
    g.setNode(v, {label:v, clusterLabelPos:'top', style:'fill:' + color})
    Object.keys(ontology).forEach(function(o){
      console.log(v +', ' + o)
      if(ontology[o].includes(v)){
        g.setParent(v,o)
      }
    })
  })

  datalist.forEach(function(e) {
    g.setNode(e[1]['type'],{clusterLabelPos:'top', style:'fill-opacity:0; stroke-width:0'})
    Object.keys(views).forEach(function(v){
      if(views[v].includes(e[1]['type'])){
        g.setParent(e[1]['type'], v)
      }
    })

  })


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
        shortenedText = d[1].substring(0,200)
        if(d[1].length > shortenedText.length){
          description += "<p>" + d[0] + " : " + shortenedText + "...</p>"
        } else{
          description += "<p>" + d[0] + " : " + shortenedText + "</p>"
        }
      })
    }
  
    states[item[1]['object']] = {
      id: "node_" + item[1]['object'],
      class: "box",
      style: "fill: " + typeColor[item[1]['type']],
      width: 120,
      height: 50,
      type: item[1]['type'],
      title: description}
  })
  
  // Add states to the graph, set labels, and style
  Object.keys(states).forEach(function(state) {
    var value = states[state];
    value.label = state;
    value.rx = value.ry = 5;
    g.setNode(state, value);
    g.setParent(state, states[state].type)
  });
  
  // Set up the edges
  recursiveAddEdges(g, testdata)
  
  // Create the renderer
  var render = new dagreD3.render();
  
  // Set up an SVG group so that we can translate the final graph.
  var svg = d3.select("#"+svgId),
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
    requestSideDescription(id)
  });
  
  svg.attr('height', g.graph().height * initialScale + 40);
  breakLabels()
  setTextColor()
}