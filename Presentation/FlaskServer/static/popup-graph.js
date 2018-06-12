setZoomForAll()

function setZoomForAll(){
    var diagram_svg = d3.selectAll("#diagram_image")
    diagram_svg.each(function(){
        diagram_group = d3.select(this).select('g')

        // Set up zoom support
        d3.select(this).call(zoom(diagram_group));
        centerSVG(diagram_group.select('image'))
    })
}

function zoom(diagram_group){
    var diagram_zoom = d3.zoom()
    .on("zoom", function() {
        diagram_group.attr("transform", d3.event.transform);
    }); 
    return diagram_zoom
}


