function getOntologyColor(type){
    color = ONTOLOGY_COLORS[type]
    colorHsl = tinycolor(color)
    colorHsl = colorHsl.toHsl()
    colorHsl.l = 0.5
    color = tinycolor(colorHsl).toHexString()
    return color
}

// Requirement
var featureDescription = '<p> <font class="feature-font">Features</font> describe the functionalities the system provides to a user. </p>'
var functionalrequirementDescription = '<p> <font class="functional-requirement-font">Functional requirements</font> describe functions or behaviors that the system must satisfy. </p>'
var usecaseDescription = '<p><font class="use-case-font">Use cases</font> are used to express how an actor uses the system to perform a task.</p>'
var userstoryDescription = '<p><font class="user-story-font">User stories</font> are short stories expressed by the person who desires the new functionality. In some cases it may be used as a lighter version of a requirement.</p>'
var nonfunctionalrequirementDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var stakeholderDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Figure
var diagramDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var figureDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var sketchDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Architecture
var architecturefragmentDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var uiDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var physicalDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var developmentDescription = '<p>The <font class="development-font">development view</font> expresses the system from a programmers perspective.</p>'
var logicalDescription = '<p>The <font class="logical-font">logical view</font> expresses the functionality the system provides to the users.</p>'

// Architecture structure
var developmentstructureDescription = '<p><font class="development-entity-font">Classes of the development view</font> express the system from a programmers perspective.</p>'
var logicalstructureDescription = '<p><font class="development-entity-font">Classes of the development view</font> express the system from a programmers perspective.</p>'
var physicalstructureDescription = '<p><font class="development-entity-font">Classes of the development view</font> express the system from a programmers perspective.</p>'
var uistructureDescription = '<p><font class="development-entity-font">Classes of the development view</font> express the system from a programmers perspective.</p>'

// Architecture behavior
var physicalbehaviorDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var logicalbehaviorDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var uibehaviorDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var developmentbehaviorDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Implementation
var implementationDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Rationale
var designoptionDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var technologyDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var argumentDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var assumptionDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var constraintDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Patterns
var architecturalpatternDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'
var roleDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'


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

    addStyleString( // Requirement
                    '.feature-font { color: ' + getOntologyColor('Feature') + '}' +
                    '.functional-requirement-font { color: ' + getOntologyColor('FunctionalRequirement') + '}' +
                    '.non-functional-reqirement-font { color: ' + getOntologyColor('NonFunctionalRequirement') + '}' +
                    '.stakeholder-font { color: ' + getOntologyColor('Stakeholder') + '}' +
                    '.use-case-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.user-story-font { color: ' + getOntologyColor('UserStory') + '}' +
                    '.non-functional-req-category-font { color: ' + getOntologyColor('NonFunctionalReqCategory') + '}' +
                    // Architecture
                    '.architecture-fragment-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.ui-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.logical-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.development-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.physical-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Architecture structure
                    '.development-structure-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.logical-structure-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.physical-structure-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.ui-structure-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Architecture behavior
                    '.development-behavior-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.logical-behavior-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.ui-behavior-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Figure 
                    '.diagram-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.figure-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.sketch-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Patterns
                    '.architectural-pattern-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.role-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Rationale
                    '.design-option-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.technology-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.argument-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.assumption-font { color: ' + getOntologyColor('UseCase') + '}' +
                    '.constraint-font { color: ' + getOntologyColor('UseCase') + '}' +
                    // Implementation
                    '.implementation-class-font { color: ' + getOntologyColor('ImplementationClass') + '}'
    )
    //Requirements
    d3.selectAll('.feature-font')
    .attr('title', featureDescription)
    d3.selectAll('.functional-requirement-font')
    .attr('title', functionalrequirementDescription)
    d3.selectAll('.non-functional-requirement-font')
    .attr('title', functionalrequirementDescription)
    d3.selectAll('.use-case-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.user-story-font')
    .attr('title', userstoryDescription)
    
    // Architecture
    d3.selectAll('.architecture-fragment-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.logical-font')
    .attr('title', logicalDescription)
    d3.selectAll('.development-font')
    .attr('title', developmentDescription)
    d3.selectAll('.ui-font')
    .attr('title', developmentDescription)
    d3.selectAll('.physical-font')
    .attr('title', developmentDescription)

    // Implementation
    d3.selectAll('.implementation-class-font')
    .attr('title', implementationclassDescription)

    // Architecture structure and behavior
    d3.selectAll('.development-structure-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.development-behavior-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.ui-structure-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.ui-behavior-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.physical-structure-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.logical-structure-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.logical-behavior-font')
    .attr('title', usecaseDescription)

    // Rationale
    d3.selectAll('.design-option-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.technology-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.argument-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.constraint-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.assumption-font')
    .attr('title', usecaseDescription)

    // Patterns
    d3.selectAll('.architectural-pattern-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.role-font')
    .attr('title', usecaseDescription)

    // Figure
    d3.selectAll('.figure-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.diagram-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.sketch-font')
    .attr('title', usecaseDescription)

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