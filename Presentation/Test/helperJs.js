function hideView(viewId, buttonId) {
    if(document.getElementById(viewId).style.display == 'none'){
        document.getElementById(viewId).style.display= 'block'
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
