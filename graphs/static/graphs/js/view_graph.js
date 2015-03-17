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
          // Select the specified element and don't allow the user to unselect it until button is clicked again
          window.cy.$('[id="' + ids[j] + '"]').select();
          window.cy.$('[id="' + ids[j] + '"]').unselectify();
          // Append a new button for every search term
          $("#search_terms").append('<li><a class="search"  id="' + ids[j]  + '" value="' + ids[j] + '">' + labels[j] + '</a></li>');
          $("#search").val("");
        }
      }
    }

    var linkToGraph = document.URL.substring(0, document.URL.indexOf('?'));
    var layout = getQueryVariable('layout');
    if (layout) {
      linkToGraph += '?layout=' + layout;
    }

    var terms = getHighlightedTerms();

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
  $(".search").each(function (index) {
    if (highlightedTerms.indexOf($(this).attr('id')) == -1) {
      highlightedTerms.push($(this).attr('id'));
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


// Gets the largest K value elements from the graph
// and only renders those values
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

// Checks to see if color is Hex
function isHexaColor(sNum){
  return (typeof sNum === "string") && sNum.length === 7
         && ! isNaN( parseInt(sNum.substring(1), 16) ) && sNum.substring(0,1) == '#' ;
}

//Appends # character if string is hex
function addCharacterToHex(sNum) {
  if (sNum.length == 6 && ! isNaN( parseInt(sNum, 16) )) {
    return '#' + sNum;
  } else {
    return sNum
  }
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
function showOnlyK() {
  var maxVal = parseInt($("#input_k").val());

  window.cy.elements().show();
  hideList = window.cy.filter('[k > ' + maxVal+ ']');
  hideList.hide();
}

//Gets all nodes and edges up do the max value set
//and only renders them
function applyMax(graph_layout) {
  var maxVal = parseInt($("#input_max").val());

  var newJSON = {
    "nodes": new Array(),
    "edges": new Array()
  };

  // List of node ids that should remain in the graph
  var nodeNames = Array();

  for (var i = 0; i < graph_json.graph['edges'].length; i++) {
    var edge_data = graph_json.graph['edges'][i];
    if (edge_data['data']['k'] <= maxVal) {
      newJSON['edges'].push(edge_data);
      nodeNames.push(edge_data['data']['source']);
      nodeNames.push(edge_data['data']['target']);
    }
  }

  for (var i = 0; i < graph_json.graph['nodes'].length; i++) {
    var node_data = graph_json.graph['nodes'][i];
    if (nodeNames.indexOf(node_data['data']['id']) > -1) {
      newJSON['nodes'].push(node_data);
    }
  }

  window.cy.load(newJSON);
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
      name: 'arbor',
      padding: 10,
      fit:true
    };

    var query = getQueryVariable("layout");
    if (query == "default_breadthfirst") {
      graph_layout = {
        name: "breadthfirst",
        padding: 10,
        fit: true
      }
    } else if (query == "default_concentric") {
       graph_layout = {
        name: "concentric",
        fit: true,
        padding: 10
      }
    } else if (query == "default_circle") {
       graph_layout = {
        name: "circle",
        padding: 10,
        fit: true
      }
    } else if (query == "default_dagre") {
       graph_layout = {
        name: "dagre",
        fit: true,
        padding: 10
      }
    } else if (query == 'default_cose') {
      graph_layout = {
        name: "cose",
        padding: 10,
        fit: true,
        idealEdgeLength: 250,
      }
    } else if (query == "default_cola") {
      graph_layout = {
        name: "cola",        
        fit: true,
        nodeSpacing: function( node ){ return 10; },
        padding: 10
      }
    }  else if (query == "default_arbor") {
      graph_layout = {
        name: "arbor",
        padding: 30,
        fit: true
      }
    }  else if (query == "default_springy") {
      graph_layout = {
        name: 'springy',

        animate: true, // whether to show the layout as it's running
        maxSimulationTime: 4000, // max length in ms to run the layout
        ungrabifyWhileSimulating: false, // so you can't drag nodes during layout
        fit: true, // whether to fit the viewport to the graph
        padding: 30, // padding on fit
        boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
        random: false, // whether to use random initial positions
        infinite: false, // overrides all other options for a forces-all-the-time mode
        ready: undefined, // callback on layoutready
        stop: undefined, // callback on layoutstop

        // springy forces
        stiffness: 400,
        repulsion: 400,
        damping: 0.5
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
      container: document.getElementById('csjs'),

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
          'font-size': 15,
          'border-color': '#000000',
          'border-width': 1,
          'width': 'data(width)',
          'height': 'data(height)'
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

      // DONE SO OLD GRAPHS WILL DISPLAY
      //If the nodes in graphs already in database don't have width or height
      // or unrecognized shape, have a default value
      for (var i = 0; i < graph_json['graph']['nodes'].length; i++) {
        var nodeData = graph_json['graph']['nodes'][i]['data'];
        if (nodeData['height'] == undefined) {
          nodeData['height'] = 50
        }

        if (nodeData['width'] == undefined) {
          nodeData['width'] = 50
        }

        //VALUES CONSISTENT AS OF CYTOSCAPEJS 2.3.9
        var acceptedShapes = ["rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star"];

        if (acceptedShapes.indexOf(nodeData['shape']) == -1) {
          nodeData['shape'] = 'ellipse';
        }

        if (nodeData['color'] == undefined) {
          nodeData['color'] = "yellow";
        } else {
          nodeData['color'] = addCharacterToHex(nodeData['color']);
          if (!isHexaColor(nodeData['color'])) {
            nodeData['color'] = "yellow";
          }
        }
      }

      // DONE SO OLD GRAPHS WILL DISPLAY
      //If the EDGES in graphs already in database don't have color have a default value
      for (var i = 0; i < graph_json['graph']['edges'].length; i++) {
        var edgeData = graph_json['graph']['edges'][i]['data'];

        if (edgeData['color'] == undefined) {
          edgeData['color'] = "black";
        } else {
          if (isHexaColor(addCharacterToHex(edgeData['color']))) {
            edgeData['color'] = addCharacterToHex(edgeData['color']);
          }
        }
      }

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

    window.cy.boxSelectionEnabled(true);

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
        heightStyle: "content"
    });

    $('#accordion_filters').accordion({
        collapsible: true,
        heightStyle: "content"
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
      var layout = [];
      for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
         var nodeData = {
          'x': nodes[i]._private.position.x,
          'y': nodes[i]._private.position.y,
          'id': nodes[i]._private.data.id
         };
         layout.push(nodeData);
      }

      //Posts information to the server regarding the current display of the graph,
      //including position
      $.post("layout/", {
        layout_id: "1",
        layout_name: layoutName,
        points: JSON.stringify(layout),
        loggedIn: $("#loggedIn").text(),
        "public": 0,
        "unlisted": 0
      }, function (data) {
        var layoutUrl = window.location.pathname + "?layout=" + layoutName;
        window.location.replace(layoutUrl);
      });
    });

    //Searches for the element inside the graph

    $("#search_button").click(function(e) {
      e.preventDefault();
      if ($("#search").val().length > 0) {
        searchValues($("#search").val());
      }
    });

    //Unhighlights terms when the buttons in the search box is clicked on
    $("#search_terms").on("click", ".search", function(e) {
      unselectTerm($(this).attr('id'));
      var toRemove  = encodeURIComponent($(this).val()) + ',';
      var origText = $("#url").text();
      origText = origText.replace(toRemove, '');
      $("#url").text(origText);
      $(this).remove();
      var toSearchFor = origText.indexOf('search=')
      var nextVal = origText.substring(toSearchFor).replace('search=', '');
      if ($(".search").length == 0) {
        $("#url").text("");
      }
    });

    $(".highlight").click(function (e) {
      e.preventDefault();
      var searchTerms = getHighlightedTerms();
      if (searchTerms.length > 0) {
        var linkHref = $(this).attr('id') + '&search=' + getHighlightedTerms();
      } else {
        var linkHref = $(this).attr('id');
      }

      $("#layout_link").attr('href', linkHref);
      $("#layout_link").text("Link to this graph with highlighted elements");
      $("#layout_link").width(20);
    });

    $(".change").click(function (e) {
      e.preventDefault();
      $("#change_modal").modal('toggle');
      $("#change_layout").val($(this).val());
    });

    $("#change_layout").click(function (e) {
      var paths = document.URL.split('/')
      var new_layout_name = $("#new_layout_name").val();

      if (new_layout_name.length == 0) {
        return alert("Enter a new layout name!");
      } else {
        $.post('../../../changeLayoutName/', {
          "gid": decodeURIComponent(paths[paths.length - 2]),
          "uid": decodeURIComponent(paths[paths.length - 3]),
          "loggedIn": $("#loggedIn").text(),
          "old_layout_name": $(this).val(),
          "new_layout_name": new_layout_name
        }, function (data) {
          window.location.href = data.url; 
        });
      }
    });

    $(".remove").click(function (e) {
      e.preventDefault();

      var paths = document.URL.split('/')
      var publicLayout = $(this).val();
      var userId = $("#loggedIn").text();
      var ownerId = decodeURIComponent(paths[paths.length - 3])
      var gid = decodeURIComponent(paths[paths.length - 2])

      $.post('../../../deleteLayout/', {
        'gid': gid,
        'owner': ownerId,
        'layout': publicLayout,
        'user_id': userId
      }, function (data) {
        window.location.href = data.url;
      })
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

    $(".public").click(function (e) {
      e.preventDefault();

      var paths = document.URL.split('/');
      var publicLayout = $(this).val();
      var userId = $("#loggedIn").text();
      var ownerId = decodeURIComponent(paths[paths.length - 3]);
      var gid = decodeURIComponent(paths[paths.length - 2]);

      $.post('../../../makeLayoutPublic/', {
        'gid': gid,
        'owner': ownerId,
        'layout': publicLayout,
        'user_id': userId
      }, function (data) {
        window.location.reload();
      });

      // $.post("../../../getGroupsWithLayout/", {
      //   "layout": publicLayout,
      //   "loggedIn": userId,
      //   "gid": gid,
      //   "owner": ownerId
      // }, function (data) {
      //   var layout_options = "";
      //   if (data['Group_Information'].length > 0) {
      //     for (var i = 0; i < data['Group_Information'].length; i++) {
      //       if (data['Group_Information'][i]['2'] == true) {
      //         if (ownerId == userId || data['Group_Information'][i]['1'] == userId) {
      //           layout_options += '<li class="list-group-item layout" style="font-size: 15px;"><label><input type="checkbox" class="layout_val" checked="checked" style="margin-right: 30px;" value="' + data['Group_Information'][i]['0'] + '12345__43121__' + data['Group_Information'][i][1] + '">' + data['Group_Information'][i][0] + " owned by: " + data['Group_Information'][i][1] + '</label></li>';
      //         } else {
      //           layout_options += '<li class="list-group-item layout" style="font-size: 15px;"><label>' + data['Group_Information'][i][0] + " owned by: " + data['Group_Information'][i][1] + '</label></li>';
      //         }
      //       } else {
      //         if (ownerId == userId || data['Group_Information'][i]['1'] == userId) {
      //           layout_options += '<li class="list-group-item layout" style="font-size: 15px;"><label><input type="checkbox" class="layout_val" style="margin-right: 30px;" value="' + data['Group_Information'][i][0] + '12345__43121__' + data['Group_Information'][i][1] + '">' + data['Group_Information'][i][0] + " owned by: " + data['Group_Information'][i][1] + '</label></li>';
      //         } else {
      //           layout_options += '<li class="list-group-item layout" style="font-size: 15px;"><label>' + data['Group_Information'][i][0] + " owned by: " + data['Group_Information'][i][1] + '</label></li>';
      //         }
      //       }
      //     }
      //   } else {
      //     layout_options += "You are not part of any groups"
      //   }

      //   layout_options += "<p style='display: none;' id='layoutId'>" + publicLayout + "</p>";

      //   $(".checked-list-box").html(layout_options);
      //   $(".layout_val").click(function(e) {
      //       $(this).prop('checked');
      //   });
      // });
    });

    $("#share_graph").click(function (e) {
      e.preventDefault();

      var paths = document.URL.split('/')
      var publicLayout = $(this).val();
      var userId = $("#loggedIn").text();
      var ownerId = decodeURIComponent(paths[paths.length - 3])
      var gid = decodeURIComponent(paths[paths.length - 2])

      $.post('../../../getGroupsForGraph/', {
        'gid': gid,
        'owner': ownerId,
      }, function (data) {
        var group_options = "";
        if (data['Group_Information'].length > 0) {
          for (var i = 0; i < data['Group_Information'].length; i++) {
            if (data['Group_Information'][i]['graph_shared'] == true) {
              if (ownerId == userId || data['Group_Information'][i]['group_owner'] == userId) {
                group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label><input type="checkbox" class="group_val" checked="checked" style="margin-right: 30px;" value="' + data['Group_Information'][i]['group_id'] + '12345__43121__' + data['Group_Information'][i]['group_owner'] + '">' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
              } else {
                group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label>' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
              }
            } else {
              if (ownerId == userId || data['Group_Information'][i]['group_owner'] == userId) {
                group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label><input type="checkbox" class="group_val" style="margin-right: 30px;" value="' + data['Group_Information'][i]['group_id'] + '12345__43121__' + data['Group_Information'][i]['group_owner'] + '">' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
              } else {
                group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label>' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
              }
            }
          }
        } else {
          group_options += "You are not part of any groups"
        }


        $(".checked-list-box").html(group_options);

        $(".group_val").click(function(e) {
          $(this).prop('checked');
        });

      });

    });

    $("#share_layout_with_selected_groups").click(function(e) {
      var paths = document.URL.split('/')
      var ownerId = decodeURIComponent(paths[paths.length - 3])
      var gid = decodeURIComponent(paths[paths.length - 2])

      var all_groups = {}
      var groups_to_share_with = [];
      var groups_not_to_share_with = [];

      $(".layout_val").each(function() {
          all_groups[$(this).val()] = $(this).is(":checked");
      });


      for (var key in all_groups) {
        if (all_groups[key] == true) {
          groups_to_share_with.push(key);
        } else {
          groups_not_to_share_with.push(key);
        }
      }

      console.log(groups_to_share_with);
      console.log(groups_not_to_share_with);

      $.post('../../../shareLayoutWithGroups/', {
        'layoutId': $("#layoutId").text(),
        'gid': gid,
        'owner': ownerId,
        'groups_to_share_with' : groups_to_share_with,
        'groups_not_to_share_with': groups_not_to_share_with
      }, function (data) {
        console.log(data);
        // window.location.reload();
      });
    });


    $("#share_graph_with_selected_groups").click(function (e) {
      var paths = document.URL.split('/')
      var ownerId = decodeURIComponent(paths[paths.length - 3])
      var gid = decodeURIComponent(paths[paths.length - 2])

      var all_groups = {}
      var groups_to_share_with = [];
      var groups_not_to_share_with = [];

      $(".group_val").each(function() {
        if (all_groups.hasOwnProperty($(this).val()) == false) {
          all_groups[$(this).val()] = $(this).is(":checked");
        }
      });


      for (var key in all_groups) {
        if (all_groups[key] == true) {
          groups_to_share_with.push(key);
        } else {
          groups_not_to_share_with.push(key);
        }
      }

      $.post('../../../shareGraphWithGroups/', {
        'gid': gid,
        'owner': ownerId,
        'groups_to_share_with' : groups_to_share_with,
        'groups_not_to_share_with': groups_not_to_share_with
      }, function (data) {
        window.location.reload();
      });
    });

    $("#input_k").val(getLargestK(graph_json.graph));
    $("#input_max").val(getLargestK(graph_json.graph));

    $("#slider_max").slider({
      step:1,
      min: 0,
      max: getLargestK(graph_json.graph),
      value: getLargestK(graph_json.graph),
      slide: function (event, ui) {
          $("#input_max").val(ui.value);
          m_val = ui.value;
          if (m_val < 0) {
            m_val = 0;
            $(this).slider({ value: 0 });
          } else {
            $(this).slider({value: m_val});
            $("#slider").slider({max: m_val});
            $("#input_k").val($("#slider").slider('value'));
          }
        },
        change: function (event, ui) {
            if (event.originalEvent) {
              applyMax(graph_json.graph)
            }
          }
    });

    $("#slider").slider({
      value: $("#slider_max").slider('value'),
      max: $("#slider_max").slider('value'),
      min: 0,
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
            showOnlyK();
          }
        }
    });
});
