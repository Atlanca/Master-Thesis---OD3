
function centerSVG(svg){
    if(svg.node().getBBox().height > svg.node().getBBox().width){
        svg.style("height", '90%')
        svg.style('transform','translate(50%,5%)')
        svg.attr('x', -svg.node().getBBox().width/2)
    }else{
        svg.style("width", '90%')
    }
}

function scrollIntoDescription(id){
    originalColor = d3.select('#'+id).style('color')

    d3.select('#'+id)
    .transition()
    .duration(0)
    .style("color", '#ff9011')
    .style("font-weight", 'bold')

    d3.select('#'+id)
    .transition()
    .duration(1000)
    .style("color", originalColor)
    .style("font-weight", 'normal')
    
    originalColor = d3.select('#'+id.replace('title','description')).style('color')

    d3.select('#'+id.replace('title','description')).
    transition().duration(0).style("color", '#ff9011')
    .style("font-weight", 'bold')

    d3.select('#'+id.replace('title','description'))
    .transition().duration(1000)
    .style("color", originalColor)
    .style("font-weight", 'normal')
    
    if(!toggle[id.replace('title', 'description')]){
        toggleVisiblityOfDescription(id.replace('title','description'))
    }
    var e = document.getElementById(id)
    e.scrollIntoView()
}

function screen_height(){
    console.log(screen.height)
    return screen.height
}

sidebarOpen = true
function sidebarToggle(id) {
    if(sidebarOpen){
        d3.select('#' + id).transition()
        .duration(500)
        .style('transform', 'translateX(36%)')
        sidebarOpen=false
    }else{
        d3.select('#' + id)
        .transition()
        .duration(0)
        .style('display', 'block')
        .transition()
        .duration(500)
        .style('transform', 'translateX(-0%)')
        sidebarOpen=true
    }
}