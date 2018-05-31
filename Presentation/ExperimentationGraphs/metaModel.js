var graph = new joint.dia.Graph;
var paper = new joint.dia.Paper({
  el: $('#myholder'),
  width: '100%',
  height: '100%',
  gridSize: 20,
  model: graph
});

//UGLY Workaround!
loadGraph(buildGraph)

function buildGraph(){
    var panCanvas = d3.select('.panCanvas')
    var jointViewport = d3.select('.joint-viewport')
    var jointMarkers = d3.select('#v-4')
    var myholder = d3.select('#myholder')
    var body = d3.select('body')
    
    addItem(jointViewport.node())
    addItem(jointMarkers.node())
    
    body.node().removeChild(myholder.node())
    jointViewport.attr('transform', 'translate(-2000, 200)')

    jointViewport.selectAll('.joint-type-standard-rectangle rect')
    .each(function(){
        color = d3.select(this).attr('fill')
        hslColor = tinycolor(color).toHsl()
        hslColor.l = 0.8
        color = tinycolor(hslColor).toHexString()
        d3.select(this)
        .attr('fill', color)
    })
}

function loadGraph(callback){
    $.get('http://localhost:5000/loadgraph', function(data, status){
        graph.fromJSON(JSON.parse(data))
        callback()
    })
}
