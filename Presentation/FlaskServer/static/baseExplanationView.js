// var section_toggle = {summary:true}
// function toggleVisiblityOfDescription(className){
//     if(!Object.keys(section_toggle).includes(className)){
//         section_toggle[className] = false
//     }
    
//     inner = d3.select('.title.' + className).html()

//     if (section_toggle[className]) {
//         d3.select('.title.' + className)
//         .html(inner.substring(0, inner.length-1) + '+')

//         d3.select('div.' + className)
//         .transition()
//         .ease(d3.easeCubic)
//         .style("opacity", 0)
//         .style("display",'none')
//         .duration(300)
//         .style("max-height", "0px")
        
//         section_toggle[className] = false
//     } else {
//         d3.select('.title.' + className)
//         .html(inner.substring(0, inner.length-1) + '-')

//         d3.select('div.' + className)
//         .style("display", "block")
//         .transition()
//         .duration(300)
//         .style("opacity", "1")
//         .style("max-height", "20000px")

//         section_toggle[className] = true

//     }
// }