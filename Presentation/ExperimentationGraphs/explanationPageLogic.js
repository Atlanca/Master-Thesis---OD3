

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

//NEW FUNCTIONS
function getNameOfUri(string){
    string = string.replace(/.+#/, '')
    string = string.replace(/\./g, '_')
    return string
}

var deactivated = false

function addTypeOptionDiv(uri, containerDivClass) {
    var name = getNameOfUri(uri)
    var type = {entityOptions: null, name: name, uri: uri, selectId: getNameOfUri(uri)}

    if (d3.select('.' + containerDivClass).select('.type-block' + getNameOfUri(uri)).empty() && !deactivated) {
        deactivated = true
        $.post('http://localhost:5000/query/getentitiesbytype', {typeUri: uri}, function(data, status){
            type.entityOptions = []
            JSON.parse(data).forEach(function(entityUri){
                type.entityOptions.push({uri: entityUri, type: ''})
            }) 

            $.post('http://localhost:5000/getTypeOptionDiv', {entityType: JSON.stringify(type)}, function(data, status){
                div = data
                var container = d3.select('.' + containerDivClass)
                container.append('div')
                .html(div)
                deactivated = false
            })
        })
    }

}

function removeTypeOptionDiv(uri, containerDivClass) {
    d3.select('.' + containerDivClass).select('.type-block.' + getNameOfUri(uri)).remove()
}

function getAllSelectedTypes() {
    var selection = []
    d3.selectAll('.type-block').each(function(){
        var option = d3.select(this).select('input.radio-input:checked').node().value
        if (option == 'specific') {
            var entitySelection = d3.select(this).select('input.datalist-input').node().value
            var baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
            selection.push({uri: d3.select(this).attr('data-type-uri'), option: option, entityUri: baseUri + entitySelection})
        } else {
            selection.push({uri: d3.select(this).attr('data-type-uri'), option: option})
        }

    })
    return selection
}

function confirmSelection() {
    var selectedLinks = getAllSelectedLinks()
    var selectedElements = getAllSelectedTypes()

    var jsonStringLinks = []
    selectedLinks.forEach(function(link){
        jsonStringLinks.push(JSON.stringify(link))
    }) 
    
    var jsonStringElements = []
    selectedElements.forEach(function(el){
        jsonStringElements.push(JSON.stringify(el))
    }) 

    window.setTimeout(function(){
        post('http://localhost:5000/getManualExplanation', {'types': jsonStringElements, 'relations': jsonStringLinks})
    },0);

}

function post(path, parameters) {
    var form = $('<form></form>');

    form.attr("method", "post");
    form.attr("action", path);

    $.each(parameters, function(key, value) {
        if ( typeof value == 'object' || typeof value == 'array' ){
            $.each(value, function(subkey, subvalue) {
                var field = $('<input />');
                field.attr("type", "hidden");
                field.attr("name", key+'[]');
                field.attr("value", subvalue);
                form.append(field);
            });
        } else {
            var field = $('<input />');
            field.attr("type", "hidden");
            field.attr("name", key);
            field.attr("value", value);
            form.append(field);
        }
    });
    $(document.body).append(form);
    form.submit();
}

function clearSelection(){
    unhighlightAllCells()
    d3.selectAll('.type-block').remove()
}

function hideEntityInput(inputElementId){
    d3.select('#' + inputElementId).style('display', 'none')
}

function showEntityInput(inputElementId){
    d3.select('#' + inputElementId).style('display', 'block')
}