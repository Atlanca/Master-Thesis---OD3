function requestFeatureRoleData(explanation, data) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://localhost:5000/"+explanation+"/" + data)
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            featureRoleGenerateGraph("graph_" + explanation, JSON.parse(this.responseText));
        }
    };
    xhttp.send()
}

function requestSideDescription(individual) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://localhost:5000/getSideDescription/" + individual)
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById('sideDescription').innerHTML = this.responseText
        }
    };
    xhttp.send()
}

function requestFeatureRoleData(explanation, data) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://localhost:5000/"+explanation+"/" + data)
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            featureRoleGenerateGraph("graph_" + explanation, JSON.parse(this.responseText));
        }
    };
    xhttp.send()
}

function requestRelationsData(explanation, data) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://localhost:5000/"+explanation+"/" + data)
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            relationGenerateGraph("graph_" + explanation, JSON.parse(this.responseText));
        }
    };
    xhttp.send()
}

function requestExplanation(explanationFunction, explanationMethodName, inputId, title) {
    inputText = document.getElementById(inputId).value

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "http://localhost:5000/getExplanationView")
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("explanation").innerHTML = this.responseText;
            explanationFunction(explanationMethodName, inputText)
        }
    };

    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("explanationType=" + explanationMethodName + "&inputData=" + inputText + "&title=" + title)
}

function requestFeatureExplanation(inputId){
    requestExplanation(requestFeatureRoleData, 'explainFeatureRole', inputId, 'Explanation of feature role')
}

function requestArchitectureRoleExplanation(inputId){
    requestExplanation(requestRelationsData, 'relationsByArchitecturalRole', inputId, 'Relations by architectural roles')
}

function requestDesignOptionExplanation(inputId){
    requestExplanation(requestRelationsData, 'relationsByDesignOption', inputId, 'Relations by design options')
}

// function requestArchitectureRoleExplanation(inputId){
//     requestExplanation(requestRelationsData, 'relationsByArchitecturalRole', inputId, 'Relations by architectural role')
// }


function hideView(viewId, buttonId) {
    if(document.getElementById(viewId).style.display == 'none'){
        document.getElementById(viewId).style.display = 'block'
        document.getElementById(buttonId).innerHTML = "hide"
    }else{
        document.getElementById(viewId).style.display= 'none'
        document.getElementById(buttonId).innerHTML = "show"
    }
    
}
function openTab(evt, tabName) {
    var i;
    var x = document.getElementsByClassName("tab");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";  
    }

    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < x.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" w3-amber", "");
    }

    document.getElementById(tabName).style.display = "block";  
    evt.currentTarget.className += " w3-amber";
}

function showSearch(){
    document.getElementById("resultsContainer").style.display = "block";
}

function switchSearchView(searchViewName, searchLabel){
    var i;
    var view = document.getElementsByClassName("searchView")
    for (i = 0; i < switchSearchView.length; i++) {
        view[i].style.display = "none";
    }

    document.getElementById(searchViewName).style.display = "block";
    document.getElementById('searchLabel').innerHTML = searchLabel;
}
