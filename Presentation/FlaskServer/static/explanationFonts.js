function getOntologyColor(type){
    color = ONTOLOGY_COLORS[type]
    colorHsl = tinycolor(color)
    colorHsl = colorHsl.toHsl()
    colorHsl.l = 0.5
    color = tinycolor(colorHsl).toHexString()
    return color
}

var featureDescription = '<p> <font class="feature-font">Features</font> describe the functionalities the system provides to a user. </p>'
var functionalrequirementDescription = '<p> <font class="functional-requirement-font">Functional requirements</font> describe functions or behaviors that the system must satisfy. </p>'
var usecaseDescription = '<p><font class="use-case-font">Use cases</font> are used to express how an actor uses the system to perform a task.</p>'
var userstoryDescription = '<p><font class="user-story-font">User stories</font> are short stories expressed by the person who desires the new functionality. In some cases it may be used as a lighter version of a requirement.</p>'
var developmententityDescription = '<p><font class="development-entity-font">Classes of the development view</font> express the system from a programmers perspective.</p>'
var developmentDescription = '<p>The <font class="development-font">development view</font> expresses the system from a programmers perspective.</p>'
var logicalentityDescription = '<p><font class="logical-entity-font">Classes of the logical view</font> express the functionality the system provides to the users.</p>'
var logicalDescription = '<p>The <font class="logical-font">logical view</font> expresses the functionality the system provides to the users.</p>'
var implementationclassDescrption = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

function setFontColors(){

    d3.selectAll('.entity-font').on('mouseover', function(){
        currentColor = d3.select(this).style(color)
        d3.select(this)
        .style('text-shadow', '1px 0 0 ' + currentColor)
    }).on('mouseout', function(){
        d3.select(this)
        .style('text-shadow', '')
    }).style('cursor', 'pointer')

    d3.selectAll('.class-font').on('mouseover', function(){
        currentColor = d3.select(this).style(color)
        d3.select(this)
        .style('text-shadow', '1px 0 0 ' + currentColor)
    }).on('mouseout', function(){
        d3.select(this)
        .style('text-shadow', '')
    }).style('cursor', 'pointer')

    d3.selectAll('.view-font').on('mouseover', function(){
        currentColor = d3.select(this).style(color)
        d3.select(this)
        .style('text-shadow', '1px 0 0 ' + currentColor)
    }).on('mouseout', function(){
        d3.select(this)
        .style('text-shadow', '')
    }).style('cursor', 'pointer')

    function addStyleString(str){
        var node = document.createElement('style')
        node.innerHTML = str
        document.body.appendChild(node)
    }

    addStyleString( '.feature-font { color: ' + getOntologyColor('Feature') + '}' +
                    '.logical-class-font { color: ' + getOntologyColor('Logical') + '}' +
                    '.logical-entity-font { color: ' + getOntologyColor('Logical') + '}' +
                    '.development-class-font { color: ' + getOntologyColor('Development') + '}' +
                    '.development-class-package-font { color: ' + getOntologyColor('Development') + '}' +
                    '.logical-font { color: ' + getOntologyColor('Logical') + '}' +
                    '.development-font { color: ' + getOntologyColor('Development') + '}' +
                    '.development-entity-font { color: ' + getOntologyColor('Development') + '}' +
                    '.implementation-class-font { color: ' + getOntologyColor('ImplementationClass') + '}' +
                    '.functional-requirement-font { color: ' + getOntologyColor('FunctionalRequirement') + '}' +
                    '.use-case-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.user-story-font { color: ' + getOntologyColor('UserStory') + '}'                 
    )

    d3.selectAll('.feature-font')
    .attr('title', featureDescription)

    d3.selectAll('.logical-class-font')
    .attr('title', logicalentityDescription)

    d3.selectAll('.development-class-font')
    .attr('title', developmententityDescription)

    d3.selectAll('.development-class-package-font')
    .attr('title', developmententityDescription)

    d3.selectAll('.logical-font')
    .attr('title', logicalDescription)

    d3.selectAll('.development-font')
    .attr('title', developmentDescription)

    d3.selectAll('.implementation-class-font')
    .attr('title', implementationclassDescrption)

    d3.selectAll('.functional-requirement-font')
    .attr('title', functionalrequirementDescription)

    d3.selectAll('.use-case-font')
    .attr('title', usecaseDescription)

    d3.selectAll('.user-story-font')
    .attr('title', userstoryDescription)

    tippy('.entity-font', {
        duration: 500,
        trigger: 'click',
        arrow: true,
        theme: 'entity-description'
    })
    tippy('.class-font', {
        duration: 500,
        trigger: 'click',
        arrow: true,
        theme: 'entity-description'
    })
    tippy('.view-font', {
        duration: 500,
        trigger: 'click',
        arrow: true,
        theme: 'entity-description'
    })
}