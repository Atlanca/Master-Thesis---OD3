
# class explanationGen():
#     def _init_(self):
#         self.test = 1
    
def flattenStructure(structure, flattenedList):
    for item in structure:
        flattenedList.append(item)



def generateRationalePatternSummary(structure=None):
    


    architectureComponents = "{count} {type}" 
    
    summaryText = "This tab describes the {pattern} and the most high level architecture related to it. "\
                  "This pattern is structured using {sumRoles} component types. These component types "\
                  "has {architectureComponents} implementing them.\n\n"
        
    relatedEntities = "Pattern component types: \n"\
                      "{componentTypes}\n\n"\
                      "Architectural entities: \n"\
                      "{architecturalEntities}\n\n"

    leftPanelDescription = "The panel to the left illustrates how the architectural pattern {pattern} relates to the architecture.\n\n"

    return summaryText + relatedEntities + leftPanelDescription

def generateRationaleChoiceSummary = ""

print(generateRationaleSummary())