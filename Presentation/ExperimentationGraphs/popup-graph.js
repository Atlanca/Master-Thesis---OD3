var diagram_svg = d3.select("#diagram_image"),
diagram_group = diagram_svg.append("g");

// Set up zoom support
var diagram_zoom = d3.zoom()
.on("zoom", function() {
    diagram_group.attr("transform", d3.event.transform);
});
diagram_svg.call(diagram_zoom);

diagram_group.append("svg:image")
.attr("xlink:href", "static/figure_3_10.png")

image = diagram_group.select('image')
centerSVG(image)


