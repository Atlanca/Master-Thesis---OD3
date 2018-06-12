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
var nonfunctionalrequirementDescription = '<p><font class="non-functional-requirement-font">Non-functional requirements</font> describe attributes or qualities that a system must satisfy.</p>'
var stakeholderDescription = '<p><font class="stakeholder-font">Stakeholders</font> are people who are involved in the system.</p>'

// Figure
var diagramDescription = '<p><font class="diagram-font">Diagrams</font> are used to visually express system behaviors and structures.</p>'
var figureDescription = '<p><font class="figure-font">Figures</font> are used to visually express parts of the system.</p>'
var sketchDescription = '<p><font class="sketch-font">Sketches</font> are used to show decisions during the GUI design phase.</p>'

// Architecture
var architecturefragmentDescription = '<p><font class="architecture-fragment-font">Architecture fragments are smaller parts that together represents the architecture.</p>'
var uiDescription = '<p>The <font class="ui-font">UI view</font> expresses the UI components of the system.</p>'
var physicalDescription = '<p>The <font class="physical-font">physical view</font> expresses the system from a system engineer\'s perspective. It shows how the system is deployed.</p>'
var developmentDescription = '<p>The <font class="development-font">development view</font> expresses the system from a programmer\'s perspective. It gives insight to how the system is built.</p>'
var logicalDescription = '<p>The <font class="logical-font">logical view</font> expresses the functionality the system provides to end-users.</p>'

// Architecture structure
var developmentstructureDescription = '<p><font class="development-structure-font">Structural classes of the development view</font> express the system from a programmer\'s perspective. They give insight to how the system is built.</p>'
var logicalstructureDescription = '<p><font class="logical-structure-font">Structural classes of the logical view</font> express the functionality the system provides to end-users.</p>'
var physicalstructureDescription = '<p><font class="physical-structure-font">Structural classes of the physical view</font> express the system from a system engineer\'s perspective. They show how the system is deployed.</p>'
var uistructureDescription = '<p><font class="ui-structure-font">Structural classes of the UI view</font> express the UI components of the system.</p>'

// Architecture behavior
var logicalbehaviorDescription = '<p><font class="logical-behavior-font">Behavioral classes of the logical view</font> describe the behavior of the system from the logical point of view.</p>'
var uibehaviorDescription = '<p><font class="ui-behavior-font">Behavioral classes of the UI view</font> describe the behavior of the system\'s UI components.</p>'
var developmentbehaviorDescription = '<p><font class="development-behavior-font">Behavioral classes of the development view</font> describe the behavior of the system from the development point of view.</p>'

// Implementation
var implementationDescription = '<p><font class="implementation-class-font">Implementation classes</font> are classes that can be found directly in the source code.</p>'

// Rationale
var designoptionDescription = '<p><font class="design-option-font">Design options</font> are considered options for the system design. The options that are implemented in the system is tagged as chosen.</p>'
var technologyDescription = '<p><font class="technology-font">Technologies</font> are considered technologies for implementing the system. The technologies that are implemented in the system is tagged as chosen.</p>'
var argumentDescription = '<p><font class="argument-font">Arguments</font> are used to motivate the choice of a design option.</p>'
var assumptionDescription = '<p><font class="assumption-font">Assumptions</font> describe the assumptions made for a chosen design option.</p>'
var constraintDescription = '<p><font class="constraint-font">Constraints</font> describe limitations that design options are based on.</p>'

// Patterns
var architecturalpatternDescription = '<p><font class="architectural-pattern-font">Architectural patterns</font> are common techniques used to solve recurring archititectural design problems.</p>'
var roleDescription = '<p><font class="role-font">Roles</font> are part of an architectural pattern. They are used to describe the responsibilities of the pattern components.</p>'

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
                    '.architecture-fragment-font { color: ' + getOntologyColor('ArchitectureFragment') + '}' +
                    '.u-i-font { color: ' + getOntologyColor('UI') + '}' +
                    '.logical-font { color: ' + getOntologyColor('Logical') + '}' +
                    '.development-font { color: ' + getOntologyColor('Development') + '}' +
                    '.physical-font { color: ' + getOntologyColor('Physical') + '}' +
                    // Architecture structure
                    '.development-structure-font { color: ' + getOntologyColor('DevelopmentStructure') + '}' +
                    '.logical-structure-font { color: ' + getOntologyColor('LogicalStructure') + '}' +
                    '.physical-structure-font { color: ' + getOntologyColor('PhysicalStructure') + '}' +
                    '.u-i-structure-font { color: ' + getOntologyColor('UIStructure') + '}' +
                    // Architecture behavior
                    '.development-behavior-font { color: ' + getOntologyColor('DevelopmentBehavior') + '}' +
                    '.logical-behavior-font { color: ' + getOntologyColor('LogicalBehavior') + '}' +
                    '.u-i-behavior-font { color: ' + getOntologyColor('UIBehavior') + '}' +
                    // Figure 
                    '.diagram-font { color: ' + getOntologyColor('Diagram') + '}' +
                    '.figure-font { color: ' + getOntologyColor('Figure') + '}' +
                    '.sketch-font { color: ' + getOntologyColor('Sketch') + '}' +
                    // Patterns
                    '.architectural-pattern-font { color: ' + getOntologyColor('ArchitecturalPattern') + '}' +
                    '.role-font { color: ' + getOntologyColor('Role') + '}' +
                    // Rationale
                    '.design-option-font { color: ' + getOntologyColor('DesignOption') + '}' +
                    '.technology-font { color: ' + getOntologyColor('Technology') + '}' +
                    '.argument-font { color: ' + getOntologyColor('Argument') + '}' +
                    '.assumption-font { color: ' + getOntologyColor('Assumption') + '}' +
                    '.constraint-font { color: ' + getOntologyColor('Constraint') + '}' +
                    // Implementation
                    '.implementation-class-font { color: ' + getOntologyColor('ImplementationClass') + '}'
    )
    //Requirements
    d3.selectAll('.feature-font')
    .attr('title', featureDescription)
    d3.selectAll('.functional-requirement-font')
    .attr('title', functionalrequirementDescription)
    d3.selectAll('.non-functional-requirement-font')
    .attr('title', nonfunctionalrequirementDescription)
    d3.selectAll('.use-case-font')
    .attr('title', usecaseDescription)
    d3.selectAll('.user-story-font')
    .attr('title', userstoryDescription)
    
    // Architecture
    d3.selectAll('.architecture-fragment-font')
    .attr('title', architecturefragmentDescription)
    d3.selectAll('.logical-font')
    .attr('title', logicalDescription)
    d3.selectAll('.development-font')
    .attr('title', developmentDescription)
    d3.selectAll('.u-i-font')
    .attr('title', uiDescription)
    d3.selectAll('.physical-font')
    .attr('title', physicalDescription)

    // Implementation
    d3.selectAll('.implementation-class-font')
    .attr('title', implementationDescription)

    // Architecture structure and behavior
    d3.selectAll('.development-structure-font')
    .attr('title', developmentstructureDescription)
    d3.selectAll('.development-behavior-font')
    .attr('title', developmentbehaviorDescription)
    d3.selectAll('.u-i-structure-font')
    .attr('title', uistructureDescription)
    d3.selectAll('.u-i-behavior-font')
    .attr('title', uibehaviorDescription)
    d3.selectAll('.physical-structure-font')
    .attr('title', physicalstructureDescription)
    d3.selectAll('.logical-structure-font')
    .attr('title', logicalstructureDescription)
    d3.selectAll('.logical-behavior-font')
    .attr('title', logicalbehaviorDescription)

    // Rationale
    d3.selectAll('.design-option-font')
    .attr('title', designoptionDescription)
    d3.selectAll('.technology-font')
    .attr('title', technologyDescription)
    d3.selectAll('.argument-font')
    .attr('title', argumentDescription)
    d3.selectAll('.constraint-font')
    .attr('title', constraintDescription)
    d3.selectAll('.assumption-font')
    .attr('title', assumptionDescription)

    // Patterns
    d3.selectAll('.architectural-pattern-font')
    .attr('title', architecturalpatternDescription)
    d3.selectAll('.role-font')
    .attr('title', roleDescription)

    // Figure
    d3.selectAll('.figure-font')
    .attr('title', figureDescription)
    d3.selectAll('.diagram-font')
    .attr('title', diagramDescription)
    d3.selectAll('.sketch-font')
    .attr('title', sketchDescription)

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