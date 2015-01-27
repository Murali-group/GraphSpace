//Exports the specified graph to an image
//Appears in side window 
function export_graph(graphname) {
    var png = window.cy.png();

    var download = document.createElement('a');
    download.href = png;
    download.download = graphname + ".png";
    fireEvent(download, 'click')
}

//This is needed to launch events in Mozilla browser
function fireEvent(obj,evt){
  var fireOnThis = obj;
  if(document.createEvent ) {
    var evObj = document.createEvent('MouseEvents');
    evObj.initEvent( evt, true, false );
    fireOnThis.dispatchEvent( evObj );
  } else if( document.createEventObject ) {
    var evObj = document.createEventObject();
    fireOnThis.fireEvent( 'on' + evt, evObj );
  }
}

//Function to search through graph elements in order to highlight the 
//appropriate one
function searchValues(names) {
  //split paths
  paths = document.URL.split('/')
  if (document.URL.indexOf('search') > -1) {
      var searchUrl = document.URL.substring(0, document.URL.indexOf('search') - 1);
  } else {
    searchUrl = document.URL;
  }

  if ($("#url").text().length > 0) {
    searchUrl = $("#url").attr('href');
  }

  if (searchUrl.indexOf("layout") == -1 && searchUrl.indexOf("search") == -1) {
    searchUrl += '?search=';
  } else {
    if (searchUrl.indexOf('search') == -1) {
      searchUrl += '&search=';
    }
  }

  //posts to server requesting the id's from the labels
  //so cytoscape will recognize the correct element
  $.post("../../../retrieveIDs/", {
    'values': names,
    "gid": decodeURIComponent(paths[paths.length - 2]),
    "uid": decodeURIComponent(paths[paths.length - 3]) 
  }, function (data) {
    names = names.split(',');
    //Done to clean up information provided
    for (var i = 0; i < names.length; i++) {
      if (names[i].indexOf(' ') > -1) {
        searchUrl += encodeURIComponent(names[i]) + ',';
      } else {
        searchUrl += names[i] + ',';
      }
      names[i] = decodeURIComponent(names[i]);
      names[i] = names[i].replace(/:/, '-');  
      names[i] = names[i].trim()
    }

    var temp = "";
    //It selects those nodes that have labels as their ID's
    labels = JSON.parse(data)['Labels'];

    //For everthing else, we get correct id's from server and proceed to highlight those id's 
    //by correlating labels to id's
    for (var j = 0; j < labels.length; j++) {
      if (labels[j].length > 0) {
        if (window.cy.$('[id="' + labels[j].toUpperCase() + '"]').selected() == false || window.cy.$('[id="' + labels[j].toLowerCase() + '"]').selected() == false || window.cy.$('[id="' + labels[j] + '"]').selected() == false) {
          window.cy.$('[id="' + labels[j].toUpperCase() + '"]').select();
          window.cy.$('[id="' + labels[j].toLowerCase() + '"]').select();
          window.cy.$('[id="' + labels[j] + '"]').select();
          $("#search_terms").append('<button class="btn btn-danger terms" id="' + labels[j]  + '" value="' + labels[j] + '"">' + names[j] + " X" + '</button>');
          $("#search").val("");
          temp += labels[j] + ',';
          $("#url").attr('href', searchUrl + temp);
          $("#url").text("Direct Link to Highlighted Elements");
          $(".test").css("height", $(".test").height + 30);
        }
      }
    }
  });
}

//Small function to split terms based on the '_' character
function splitTerms(term) {
  return term.split("_");
}

//Gets query variables from the url
function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

//Unselects a specified term from graph
function unselectTerm(term) {
  window.cy.$('[id="' + term + '"]').unselect();
}

/* 
This function is executed when the page finishes loading.
Consult the API: http://api.jquery.com/ready/
*/
$(document).ready(function() {
    // Cytoscape.js API: 
    // http://cytoscape.github.io/cytoscape.js/

    //The following code retrieves the specified layout
    //of a graph to be displayed.
    //Some of them are pre-defined. Check Cytoscapejs.org
    var graph_layout = {
      name: 'concentric',
      padding: 10
    };

    var query = getQueryVariable("layout");
    if (query == "default_breadthfirst") {
      graph_layout = {
        name: "breadthfirst",
        padding: 10
      }
    } else if (query == "default_concentric") {
       graph_layout = {
        name: "concentric",
        padding: 10
      }
    } else if (query == "default_circle") {
       graph_layout = {
        name: "circle",
        padding: 10
      }
    } else if (query == 'default_cose') {
      graph_layout = {
        name: "cose",
        padding: 10,
        idealEdgeLength: 250,
      }
    } else if (query == "default_cola") {
      graph_layout = {
        name: "cola",
        padding: 10,
        idealEdgeLength: 250,
      }
    }  else if (query == "default_arbor") {
      graph_layout = {
        name: "cola",
        padding: 10,
        idealEdgeLength: 250,
      }
    }  else if (query == "default_springy") {
      graph_layout = {
        name: "cola",
        padding: 10,
        idealEdgeLength: 250,
      }
    } else {
      if (layout != null) {
        graph_layout = {
          name: 'preset',
          positions: JSON.parse(layout.json)
        };
      }
    }

    //Renders the cytoscape element on the page
    //with the given options
    window.cy = cytoscape( options = {
      container: document.getElementById('csweb'),

      style: cytoscape.stylesheet()
      .selector('node')
        .css({
          //name to display
          'content': 'data(label)', 
          'shape': 'data(shape)',
          'text-valign': 'center',
          'color': '#000000',
          'text-outline-width': 0,
          'background-color': 'data(color)', 
          'font-size': 10,
          'border-color': '#000000',
          'border-width': 1
        })
      .selector('edge')
        .css({
          'target-arrow-shape': 'triangle',
          'line-color': 'data(color)',
          'source-arrow-color': 'data(color)',
          'target-arrow-color': 'data(color)',
        })
      .selector('node:selected')
        .css({
          'border-width': 3,
          'border-color': '#ff0000'
        })
      .selector('edge:selected')
        .css({
          'width': 3,
          'line-color': '#ff0000',
          'target-arrow-color': '#ff0000',
          'source-arrow-color': '#ff0000'
        }),
    
    // default layout set to be concentric
    layout: graph_layout,
    
    // draw graph, handle events etc.
    ready: function(){
      var defaults = ({
          zoomFactor: 0.05, // zoom factor per zoom tick
          zoomDelay: 45, // how many ms between zoom ticks
          minZoom: 0.1, // min zoom level
          maxZoom: 10, // max zoom level
          fitPadding: 50, // padding when fitting
          panSpeed: 10, // how many ms in between pan ticks
          panDistance: 50, // max pan distance per tick
          panDragAreaSize: 75, // the length of the pan drag box in which the vector for panning is calculated (bigger = finer control of pan speed and direction)
          panMinPercentSpeed: 0.25, // the slowest speed we can pan by (as a percent of panSpeed)
          panInactiveArea: 8, // radius of inactive area in pan drag box
          panIndicatorMinOpacity: 0.5, // min opacity of pan indicator (the draggable nib); scales from this to 1.0
          autodisableForMobile: true, // disable the panzoom completely for mobile (since we don't really need it with gestures like pinch to zoom)

      });
      //Adding in the panzoom functionality 
      this.panzoom(defaults);
      // make the selection states of the elements mutable
      this.elements().selectify();
      // load the graph to display
      this.load(graph_json.graph);
      // enable user panning (hold the left mouse button to drag
      // the screen)
      this.userPanningEnabled(false);
      
      // display node data as a popup
      this.on('tap', function(evt){
        // get target
        var target = evt.cyTarget;

        // target some element other than background (node/edge)
        if ( target !== this ) {
            var popup = target._private.data

            if (popup == null) {
                console.log('popup null');
                return;
            }

            $('#dialog').html(popup);
            if (target._private.data.popup != null && target._private.data.popup.length > 0) {
              $("#dialog").html("<p>" + target._private.data.popup + "</p>");
            }
            if (target._private.group == 'edges') {
              $('#dialog').dialog('option', 'title', target._private.data.source + "->" + target._private.data.target);
            } else {
              $('#dialog').dialog('option', 'title', target.data('label'));
            }
            $('#dialog').dialog('open');
        }
      });


      //If ther are any terms to be searched for, highlight those terms, if found
      var searchTerms = getQueryVariable("search");
      if (searchTerms) {
        searchValues(searchTerms);
      }

    } // end ready: function()
    });


    //setup popup dialog for displaying dialog when nodes/edges
    //are clicked for information.
    $('#dialog').dialog({ autoOpen: false });

    //these accordions make up the side menu
    $('#accordion_graph_details').accordion({
        collapsible: true,
        active: false
    });

    $('#accordion_export').accordion({
        collapsible: true,
        active: false 
    });

    $("#accordion_search").accordion({
        collapsible: true,
        active: true
    });

    $('#accordion_owner').accordion({
        collapsible: true,
        active: false 
    });

    $('#accordion_sharing').accordion({
        collapsible: true,
        active: false 
    });

    $('#accordion_layouts').accordion({
        collapsible: true,
        heightStyle: "fill"
    });

    //When save layout button is clicked
    $("#save_layout").click(function(e) {
      e.preventDefault();

      //Replaces all spaces with '_' character for ease of saving
      var layoutName = $("#layout_name").val();
      if (layoutName && layoutName.length > 0) {
        layoutName = layoutName.replace(" ", "_");
      }

      //When save is clicked, it gets location of all the nodes and saves it
      //so that nodes can be placed in this location later on
      var nodes = window.cy.elements('node');
      var layout = {};
      for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
         var nodeId = nodes[i]._private.data.id;
         var nodePosition = nodes[i]._private.position;
         layout[nodeId] = nodePosition;
      }

      //Posts information to the server regarding the current display of the graph,
      //including position
      $.post("layout/", {
        layout_id: "1",
        layout_name: layoutName,
        points: JSON.stringify(layout),
        "public": 0,
        "unlisted": 0
      }, function (data) {
        var layoutUrl = location.pathname + "?layout=" + layoutName;
        location.replace(layoutUrl);
      });

    });

    //Searches for the element inside the grap

    $("#search_button").click(function(e) {
      e.preventDefault();
      if ($("#search").val().length > 0) {
        searchValues($("#search").val());
      }
    });

    //Unhighlights terms when the buttons in the search box is clicked on
    $("#search_terms").on("click", ".terms", function(e) {
      unselectTerm($(this).val());
      var toRemove  = encodeURIComponent($(this).val()) + ',';
      var origText = $("#url").text();
      origText = origText.replace(toRemove, '');
      $("#url").text(origText);
      $(this).remove();
      var toSearchFor = origText.indexOf('search=')
      var nextVal = origText.substring(toSearchFor).replace('search=', '');
      if ($(".terms").length == 0) {
        $("#url").text("");
      }
    });

    $(".layout_links").click(function (e) {
      e.preventDefault();
      $("#layout_link").attr('href', $(this).attr('id'));
      $("#layout_link").text("Direct Link to Layout");
      $("#layout_link").width(20);
    });

    $(".layout_links").tooltip();
});
