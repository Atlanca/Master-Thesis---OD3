d_info = 
"<p><b>Diagram navigation actions:</b></p>" +
"<p>Dragging moves the view position</p>" +
"<p>Scrolling zooms the diagram</p>" +
"<p><b>Entity actions:</b></p>" + 
"<p>Clicking the entity highlights the entity relations</p>" +
"<p>Clicking the entity arrow opens options that provides more information of the entity </p>"

setupInfo(d_info)

function setupInfo(info){
    d3.select('.info').attr('title', info)
    tippy('.info', {trigger: 'click', placement: 'right-start', arrow:true})
}

