function centerSVG(svg){
    if(svg.node().getBBox().height > svg.node().getBBox().width){
        svg.style("height", '90%')
        svg.style('transform','translate(50%,5%)')
        svg.attr('x', -svg.node().getBBox().width/2)
    }else{
        svg.style("width", '90%')
    }
}

var tabList = []
var currentView
function initializeTabs(tablist){
    tabList = tablist
}

function toggleFirstTab(){
    toggleTab(tabList[0])
}

function toggleTab(view){    
    currentView = view

    tab_display = d3.select('button.' + view).style('display')
    if (tab_display || tab.display == 'none'){
        d3.selectAll('.side-bar-tab').classed('selected', false)

        d3.selectAll('div.side-bar-content-base').style('display', 'none')
        d3.selectAll('.interactive_diagram').style('display', 'none')

        d3.select('div.side-bar-content-base.' + view).style('display', 'block')
        d3.select('button.' + view).classed('selected', true)
        d3.select('.' + view + '.interactive_diagram').style('display', 'block')
    }

    for (var i = 0; i < tabList.length; i++){
        d3.select('.interactive-diagram-tab-container').classed(tabList[i], false)
        d3.select('.side-bar-toggle').classed(tabList[i], false)
    }
    
    d3.select('.side-bar-toggle').classed(view, true)
    d3.select('.interactive-diagram-tab-container').classed(view, true)
}

function mod(n, m) {
    return ((n % m) + m) % m;
}

function nextTab(){
    if (currentView){
        index = tabList.indexOf(currentView)
        if(index < tabList.length - 1){
            nextIndex = index + 1
            d3.select('.view-navigation.back').style('display', 'block')
            if(nextIndex == tabList.length - 1)
                d3.select('.view-navigation.forward').style('display', 'none')
        }else{
            nextIndex = index
        }
        toggleTab(tabList[nextIndex])
    }
}

function previousTab(){
    if(currentView){
        index = tabList.indexOf(currentView)
        if(index > 0){
            previousIndex = index - 1
            d3.select('.view-navigation.forward').style('display', 'block')
            if(previousIndex == 0)
                d3.select('.view-navigation.back').style('display', 'none')
        }else{
            previousIndex = index
        }
        toggleTab(tabList[previousIndex])
    }
}

function toggleVisibilityFirst(toggleClass){
    tab_content = d3.select('div.' + className)
    tab_button = d3.select('button.' + className)
    tab_display = tab_content.style('display')
    
    // If this tab already selected, return
    if(tab_button.classed('selected')){
        return
    }
    
}

function toggleVisibility(className){
    tab_content = d3.select('div.' + className)
    tab_button = d3.select('button.' + className)
    tab_display = tab_content.style('display')
    
    // Hide everything
    d3.selectAll('.left-side').classed('selected', false)
    d3.selectAll('.popup-content').style('display', 'none')

    // Display tab
    if (tab_display == 'block') {
        tab_content.transition()
        .style("display",'block')
        tab_button
        .classed('selected', true)
        
    } else {
        tab_content
        .style("display", "block")
        .transition()
        .duration(300)
        .style("opacity", "1")
        .style("max-height", "20000px")

        tab_button
        .classed('selected', true)
    }
}

function toggleVisiblityOfDescription(className, wrapperClassName=''){
    if (wrapperClassName) {
        wrapperClassName = '.' + wrapperClassName
    } else {
        wrapperClassName = 'body'
    }  
    console.log(wrapperClassName)
    console.log(className)

    console.log(d3.select(wrapperClassName + ' .title.' + className))

    inner = d3.select(wrapperClassName + ' .title.' + className).html()
    tab_display = d3.select(wrapperClassName + ' div.' + className).style('display')

    if (tab_display == 'block') {
        d3.select(wrapperClassName + ' .title.' + className)
        .html(inner.substring(0, inner.length-1) + '+')

        d3.select(wrapperClassName + ' div.' + className)
        .transition()
        .ease(d3.easeCubic)
        .style("opacity", 0)
        .style("display",'none')
        .duration(300)
        .style("max-height", "0px")
    
    } else {
        d3.select(wrapperClassName + ' .title.' + className)
        .html(inner.substring(0, inner.length-1) + '-')

        d3.select(wrapperClassName + ' div.' + className)
        .style("display", "block")
        .transition()
        .duration(300)
        .style("opacity", "1")
        .style("max-height", "20000px")

    }
}

function toggleVisiblityOfDescriptionFromNode(className, wrapperClassName=''){
    if (wrapperClassName) {
        wrapperClassName = '.' + wrapperClassName
    } else {
        wrapperClassName = 'body'
    }  
    console.log(wrapperClassName)
    console.log(className)

    console.log(d3.select(wrapperClassName + ' .title.' + className))

    inner = d3.select(wrapperClassName + ' .title.' + className).html()
    tab_display = d3.select(wrapperClassName + ' div.' + className).style('display')

    d3.select(wrapperClassName + ' .title.' + className)
    .html(inner.substring(0, inner.length-1) + '-')

    d3.select(wrapperClassName + ' div.' + className)
    .style("display", "block")
    .transition()
    .duration(300)
    .style("opacity", "1")
    .style("max-height", "20000px")


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

function toggleMenu(elem, menuButtonClass, menuContentClass){
    menu = d3.select(elem.parentNode).select('.' + menuContentClass)
    if(menu.classed('w3-show')){
        menu.classed('w3-show', false)
        d3.select(elem).classed('selected', false)
    }else{
        d3.selectAll('.' + menuContentClass).classed('w3-show', false)
        d3.selectAll('.' + menuButtonClass).classed('selected', false)

        menu.classed('w3-show', true)
        d3.select(elem).classed('selected', true)
    }

}

function changeInputType(){
    var select = document.getElementById('menu-search-question-select')
    var currentSelection = select.options[select.selectedIndex].value
    var selectionHasListInput = select.options[select.selectedIndex].dataset.listinput
    var selectionType = select.options[select.selectedIndex].dataset.type
    var baseUri = 'http://www.semanticweb.org/ontologies/snowflake#'
    var input = document.getElementById('search-input')
    var inputwrapper = document.getElementById('menu-search-input-wrapper')
    input.value = ''
    
    if (selectionHasListInput == 'true') {
        inputwrapper.style.display = 'inline-block'
        input.style.display = 'block'
        input.placeholder = 'Name of ' + selectionType + '...'
        var datalist = document.getElementById('entities-list')
        datalist.innerHTML = ''

        $.post('http://localhost:5000/query/getentitiesbytype', {typeUri: baseUri + selectionType}, function(data){
            data = JSON.parse(data)
            data.forEach(function(entity){
                var option = document.createElement('option')
                option.value = getNameOfUri(entity)
                option.innerHTML = selectionType
                datalist.appendChild(option)
            })

        })
    } else {
        input.style.display = 'none'
        inputwrapper.style.display = 'inline-block'
    }
}

function performSearch(question_select, query_input){
    selectElem = document.getElementById(question_select)
    selectValue = selectElem.options[selectElem.selectedIndex].value;

    d3.select('body')
    .append('div')
    .classed('query-loader-background', true)
    .append('div')
    .classed('query-loader', true)
    .style('transform', 'translate(50px, 50px)')

    query = document.getElementById(query_input).value;
    setTimeout(function(){
        document.location.href = 'http://localhost:5000/' + selectValue + '/' + query
    },500);

    return false;
}

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