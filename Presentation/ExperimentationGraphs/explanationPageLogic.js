

function centerSVG(svg){
    if(svg.node().getBBox().height > svg.node().getBBox().width){
        svg.style("height", '90%')
        svg.style('transform','translate(50%,5%)')
        svg.attr('x', -svg.node().getBBox().width/2)
    }else{
        svg.style("width", '90%')
    }
}

var toggle = {summary_description:true}
function toggleVisiblityOfDescription2(className){
    if(!Object.keys(toggle).includes(className)){
        toggle[className] = false
    }

    console.log(d3.selectAll('.title.' + className))
    
    inner = d3.select('h3.' + className).html()

    if (toggle[className]) {
        d3.select('h3.' + className)
        .html(inner.substring(0, inner.length-1) + '+')

        d3.select('div.' + className)
        .transition()
        .ease(d3.easeCubic)
        .style("opacity", 0)
        .style("display",'none')
        .duration(300)
        .style("max-height", "0px")
        
        toggle[className] = false
    } else {
        d3.select('h3.' + className)
        .html(inner.substring(0, inner.length-1) + '-')

        d3.select('div.' + className)
        .style("display", "block")
        .transition()
        .duration(300)
        .style("opacity", "1")
        .style("max-height", "20000px")

        toggle[className] = true

    }
}

var toggle = {summary_description:true}
function toggleVisiblityOfDescription(id){
    if(!Object.keys(toggle).includes(id)){
        toggle[id] = false
    }

    if (toggle[id]) {
        if(id.includes('description')){
            inner = document.getElementById(id.replace('description', 'title')).textContent
            document.getElementById(id.replace('description', 'title')).textContent = inner.substring(0,inner.length-1) + '+'
        }

        d3.select('#'+id)
        .transition()
        .ease(d3.easeCubic)
        .style("opacity", 0)
        .style("display",'none')
        .duration(300)
        .style("max-height", "0px")
        
        toggle[id] = false
    } else {
        if(id.includes('description')){
            inner = document.getElementById(id.replace('description', 'title')).textContent
            document.getElementById(id.replace('description', 'title')).textContent = inner.substring(0,inner.length-1) + '-'
        }
        d3.select('#'+id)
        .style("display", "block")
        .transition()
        .duration(300)
        .style("opacity", "1")
        .style("max-height", "20000px")

        toggle[id] = true

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
        d3.select('#' + id)
        .style('transform', 'translateX(98%)')
        sidebarOpen=false
    }else{
        d3.select('#' + id)
        .style('transform', 'translateX(0%)')
        sidebarOpen=true
    }
}