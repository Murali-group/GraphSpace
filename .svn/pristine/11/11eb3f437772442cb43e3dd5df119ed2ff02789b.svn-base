  //popup dialog related functions from Craig's code
  function show_popup(evt) {
      var data = evt.target.data;

      if (data.popup == null) {
          console.log('popup null');
          return;
      }

      console.log('show_popup');

      $('#dialog').html(data.popup);
      $('#dialog').dialog('option', 'title', data.label);
      $('#dialog').dialog('open');
  }

  // ##### may need later in time #####
  // function gen_node_details(node) {
  //     var body = node.popup;
  //     if (body == null)
  //         body = '';
  //     var label = node.label;
  //     if (label) 
  //         body = '<b>Label:</b> ' + label + "<hr>" + body;
  //     var graph_id = node.graph_id;
  //     if (graph_id) {
  //         body = '<b>Related Graph:</b> '
  //             + '<a href="http://holmes.cs.vt.edu/users/ategge@vt.edu/graphs/'
  //             + graph_id
  //             + '?pid=hsa04920-hsa04917" target="_blank">'
  //             + graph_id
  //             + '</a>'
  //             + '<hr>'
  //             + body;
  //     }
  //     return body;
  // }

  // function gen_edge_details(edge) {
  //     var body = edge.popup;
  //     if (body == null)
  //         body = '';
  //     var label = edge.label;
  //     if (label)
  //         body = '<b>Label:</b> ' + label + '<hr>' + body;
  //     return body;
  // }
  // ###############################
  // END popup dialog

  function add_data_schema() {
      console.log('add data schema');
      // define data schema of the graph
      // graph_json is the graph data retrieved from database
      // see views.py and view_graph.html
      graph_json.graph.dataSchema = {
             nodes : [
                { name : "label",           type : "string" },
                { name : "popup",           type : "string" },
                { name : "tooltip",         type : "string" },
                { name : "color",           type : "string" },
                { name : "size",            type : "string" },
                { name : "shape",           type : "string" },
                { name : "graph_id",        type : "string" },
                { name : "go_function_id",  type : "string" },
                { name : "borderWidth",     type : "double" },
                { name : "labelFontWeight", type : "string" }, 
                { name : "k",               type : "string" }
             ],
             edges : [
                { name : "width", type : "double" },
                { name : "label", type : "string" },
                { name : "popup", type : "string" },
                { name : "color", type : "string" },
                { name : "style", type : "string" },
                { name : "graph_id",        type : "string" },
                { name : "labelFontWeight", type : "string" },
                { name : "k", type: "string" }
             ]
          };
  }

  function cytoscapeweb_init() {
      // id of Cytoscape Web container div
      var div_id = "csweb";

      // initialization options
      var options = {
          // where you have the Cytoscape Web SWF
          swfPath: "/static/graphs/CytoscapeWeb",
          // where you have the Flash installer SWF
          flashInstallerPath: "/static/graphs/playerProductInstall"
      };

      console.log('initialize visualizer');
      // init cytoscapeweb Visualization object
      var visualizer = new org.cytoscapeweb.Visualization(div_id, options);
      // add mouse event handlers
      console.log('add mouse event listeners');
      visualizer.addListener("click", "nodes", function(evt) { show_popup(evt) });
      visualizer.addListener("click", "edges", function(evt) { show_popup(evt) });

      // visualizer.swf().setVisualStyle(style);

      add_data_schema();

      return visualizer;
  }



  // draw the network
  // vis - Cytoscape Web Visualization object initilized from
  //       cytoscapeweb_init()
  function draw(visualizer) {
      console.log('draw graph')
      // draw the given graph
      visualizer.draw({ network: graph_json.graph, 
      
          visualStyle: {
              nodes: {
                  color: { passthroughMapper: { attrName: 'color' } },
                  size:  { passthroughMapper: { attrName: 'size'  } },
                  shape: { passthroughMapper: { attrName: 'shape' } },
                  labelFontWeight: { passthroughMapper: { attrName: 'labelFontWeight' } },
                  borderWidth: { passthroughMapper: { attrName: 'borderWidth' } },
                  selectionGlowColor: "#ff0000",
                  selectionGlowStrength: 250
              },
              edges: {
                  width: { passthroughMapper: { attrName: 'width' } },
                  color: { passthroughMapper: { attrName: 'color' } },
                  style: { passthroughMapper: { attrName: 'style' } },
                  selectionGlowColor: "#ff0000",
                  selectionGlowStrength: 250
              }
          }
      });
  };

  function export_graph(type, url) {
      if (type === "pdf" || type === "png" || type === "svg") {
          vis.exportNetwork(type, url);
      }
  }

/* 
This function is executed when the page finishes loading.

Consult the API: http://api.jquery.com/ready/
*/
$(document).ready(function() {
    // initialize Cytoscapeweb Visualization object.
    window.vis = cytoscapeweb_init();

    // draw on the Visualization object
    draw(window.vis);

    //setup popup dialog for displaying dialog when nodes/edges
    //are clicked for information.
    $('#dialog').dialog({ autoOpen: false });

    //these accordions make up the side menu
    $('#accordion_graph_details').accordion({
        collapsible: true
    });

    $('#accordion_export').accordion({
        collapsible: true,
        active: false 
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
        active: false 
    });
});
