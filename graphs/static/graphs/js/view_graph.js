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
function searchValues(labels) {
  //split paths
  var paths = document.URL.split('/')

  //posts to server requesting the id's from the labels
  //so cytoscape will recognize the correct element
  $.post("../../../retrieveIDs/", {
    'values': labels,
    "gid": decodeURIComponent(paths[paths.length - 2]),
    "uid": decodeURIComponent(paths[paths.length - 3]) 
  }, function (data) {

    //Split the labels so we can reference the labels
    labels = labels.split(',');

    //It selects those nodes that have labels as their ID's
    ids = JSON.parse(data)['IDS'];

    //For everthing else, we get correct id's from server and proceed to highlight those id's 
    //by correlating labels to id's
    for (var j = 0; j < ids.length; j++) {
      if (ids[j].length > 0) {
        if (window.cy.$(window.cy.$('[id="' + ids[j] + '"]').selected() == false)) {
          // If it's an edge, highlight both the edge and the connecting nodes
          if (ids[j].indexOf('-') > -1) {
            var node_ids = ids[j].split('-');
            searchValues(node_ids[0]);
            searchValues(node_ids[1]);
          }
          //Otherwise just highlight the nodes themselves
          window.cy.$('[id="' + ids[j] + '"]').select();
          window.cy.$('[id="' + ids[j] + '"]').unselectify();
          $("#search_terms").append('<button class="btn btn-danger terms" id="' + ids[j]  + '" value="' + ids[j] + '"">' + labels[j] + " X" + '</button>');
          $("#search").val("");
        }
      }
    }

    var linkToGraph = document.URL.substring(0, document.URL.indexOf('?'));
    var layout = getQueryVariable('layout');
    if (layout) {
      linkToGraph += '?layout=' + layout + '&search=';
    } else {
      linkToGraph += '?search=';
    }

    linkToGraph += getHighlightedTerms();

    $("#url").attr('href', linkToGraph);
    $("#url").text("Direct Link to Highlighted Elements");
    $(".test").css("height", $(".test").height + 30);
  });
}

function getHighlightedTerms() {
  // Create a url with all the highlighted terms
  var highlightedTerms = new Array();
  var linkToGraph = ""
  // Go through all of the highlighted terms
  $(".terms").each(function (index) {
    if (highlightedTerms.indexOf($(this).val()) == -1) {
      highlightedTerms.push($(this).val());
    }
  });

  for (var i = 0; i < highlightedTerms.length; i++) {

    if (highlightedTerms[i].indexOf('-') > -1) {
      highlightedTerms[i] = highlightedTerms[i].replace('-', ':');
    }

    if (i == highlightedTerms.length - 1) {
      linkToGraph += highlightedTerms[i];
    } else {
      linkToGraph += highlightedTerms[i] + ',';
    }
  }

  return linkToGraph
}

function getLargestK(graph_json) {
  var edges = graph_json['edges'];

  var largestK = 0;
  for (var i = 0; i < edges.length; i++) {
    k_val = parseInt(edges[i]['data']['k']);
    if (k_val > largestK) {
      largestK = k_val;
    }
  }
  return largestK;
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

// Returns all the id's that are not <= k value
function showOnlyK(graph_layout) {
  var maxVal = parseInt($("#input_k").val());

  window.cy.elements().show();
  hideList = window.cy.filter('[k > ' + maxVal+ ']');
  hideList.hide();
}

//Unselects a specified term from graph
function unselectTerm(term) {
  window.cy.$('[id="' + term + '"]').selectify();
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

            if (target._private.data.hasOwnProperty('target') && target._private.data.hasOwnProperty('source')) {
              var edgeId = target._private.data.id.replace('-', ':');
              searchValues(edgeId);
            } else {
              searchValues(target._private.data.label);
            }
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

    $('#accordion_filters').accordion({
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
      var searchTerms = getHighlightedTerms();
      if (searchTerms.length > 0) {
        var linkHref = $(this).attr('id') + '&search=' + getHighlightedTerms();
      } else {
        var linkHref = $(this).attr('id');
      }

      $("#layout_link").attr('href', linkHref);
      $("#layout_link").text("Direct Link to Layout");
      $("#layout_link").width(20);
    });

    $(".layout_links").tooltip();

    $(".layout_buttons").click(function (e) {
      e.preventDefault();
      var searchTerms = getHighlightedTerms();
      if (searchTerms.length > 0) {
        var linkHref = $(this).attr('href') + '&search=' + getHighlightedTerms();
      } else {
        var linkHref = $(this).attr('href');
      }

      if (e.target == this) {
        window.location.href = linkHref;
      }

    });

    $("#input_k").val(getLargestK(graph_json.graph));
    $("#input_max").val(getLargestK(graph_json.graph));

    $("#slider").slider({
              value: getLargestK(graph_json.graph),
              min: 0,
              max: getLargestK(graph_json.graph),
              step: 1,
              slide: function (event, ui) {
                $("#input_k").val(ui.value);
                m_val = ui.value;
                if (m_val < 0) {
                  m_val = 0;
                  $(this).slider({ value: 0 });
                }
              },
              change: function (event, ui) {
                  if (event.originalEvent) {
                    showOnlyK(graph_layout);
                  }
                }});

    $("#slider_max").slider({
      step:1,
      min: 0,
      max: getLargestK(graph_json.graph),
      slide: function(event, ui) {
        var value = $( "#slider_max" ).slider( "value" );
        $("#input_max").val(value);
      }
    });

});
