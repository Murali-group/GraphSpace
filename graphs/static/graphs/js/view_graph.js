function export_graph(graphname) {
    var png = window.cy.png();

    var download = document.createElement('a');
    download.href = png;
    download.download = graphname + ".png";
    fireEvent(download, 'click')
}

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

function searchValues(names) {
  var splitNames = names.split(",");
  for (var i = 0; i < splitNames.length; i++) {
    splitNames[i] = splitNames[i].trim();
    window.cy.$("#" + splitNames[i]).select();
    // $("#search_terms").append('<button class="btn btn-primary" class="terms" value="' + splitNames[i] + '"">' + splitNames[i] + '</button>');
    $("#search").val("");
  }

}

function unselectTerm(term) {
  $("#" + term).unselect();
}

/* 
This function is executed when the page finishes loading.

Consult the API: http://api.jquery.com/ready/
*/
$(document).ready(function() {

    // Cytoscape.js API: 
    // http://cytoscape.github.io/cytoscape.js/
    // $('.csweb').cytoscape({

    var graph_layout = {
      name: 'concentric',
      padding: 10
    };
    if (layout != null) {
      graph_layout = {
        name: 'preset',
        positions: JSON.parse(layout.json)
      };
    }

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

            console.log('show_popup');

            $('#dialog').html(popup);
            if (target._private.group == 'edges') {
              $('#dialog').dialog('option', 'title', target._private.data.source + "->" + target._private.data.target);
            } else {
              $('#dialog').dialog('option', 'title', target.data('label'));
            }
            $('#dialog').dialog('open');
        }
      });

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
        collapsible: true
    });

    $("#save_layout").click(function(e) {
      e.preventDefault();

      var layoutName = $("#layout_name").val();
      if (layoutName && layoutName.length > 0) {
        layoutName = layoutName.replace(" ", "_");
      }

      var nodes = window.cy.elements('node');
      var layout = {};
      for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
         var nodeLabel = nodes[i]._private.data.label;
         var nodePosition = nodes[i]._private.position;
         // layout[nodeLabel] = nodePosition;
         layout[nodeLabel] = nodePosition;
      }

      $.post("layout/", {
        layout_id: "1",
        layout_name: layoutName,
        points: JSON.stringify(layout),
        "public": 0,
        "unlisted": 0
      }, function (data) {
        // $("#layout_name").val("");
        // $("#layout_modal").modal('hide');
        var layoutUrl = location.pathname + "?layout=" + layoutName;
        location.replace(layoutUrl);
        // console.log(data);
      });

    });

    $("#search_button").click(function(e) {
      e.preventDefault();
      if ($("#search").val().length > 0) {
        searchValues($("#search").val());
      }
    });

});
