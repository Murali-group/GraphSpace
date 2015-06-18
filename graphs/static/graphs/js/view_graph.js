/* 
This function is executed when the page finishes loading.
Consult the API: http://api.jquery.com/ready/
*/
$(document).ready(function() {

    if ($("#title").text().length > 0) {
      $("#graph_title").html("<h1>" + $("#title").text() + "</h1>");
      $(".side_menu").css("margin-top", -50);
    }

    // Cytoscape.js API: 
    // http://cytoscape.github.io/cytoscape.js/

    //Renders the cytoscape element on the page
    //with the given options
    window.cy = cytoscape({
      container: $('#csjs')[0],

      // ** NOTE: REPLACE - WITH _ SO CYTOSCAPEJS WILL RENDER PROPERTIES

      //Style properties of NODE body
      style: cytoscape.stylesheet()
      .selector('node[width]').css({
        'width': 'data(width)'
      })
      .selector('node[height]').css({
        'height': 'data(height)'
      })
      .selector('node[shape]').css({
        'shape': 'data(shape)'
      })
      .selector('node[background_color]').css({
        'background-color': 'data(background_color)'
      })
      .selector('node[background_blacken]').css({
        'background-blacken': 'data(background_blacken)'
      })
      .selector('node[background_opacity]').css({
        'border-opacity': 'data(background_opacity)'
      })
      .selector('node[border_width]').css({
        'border-width': 'data(border_width)'
      })
      .selector('node[border_style]').css({
        'border-style': 'data(border_style)'
      })
      .selector('node[border_color]').css({
        'border-color': 'data(border_color)'
      })
      .selector('node[border_opacity]').css({
        'border-opacity': 'data(border_opacity)'
      })

      //BACKGROUND IMAGE PROPERTIES
      .selector('node[background_image]').css({
        'background-image': 'data(background_image)'
      })
      .selector('node[background_image_opacity]').css({
        'background-image-opacity': 'data(background_image_opacity)'
      })
      .selector('node[background_fit]').css({
        'background-fit': 'data(background_fit)'
      })
      .selector('node[background_repeat]').css({
        'background-repeat': 'data(background_repeat)'
      })
      .selector('node[background_position_x]').css({
        'background-position-x': 'data(background_position_x)'
      })
      .selector('node[background_position_y]').css({
        'background-position-y': 'data(background_position_y)'
      })
      .selector('node[background_clip]').css({
        'background-clip': 'data(background_clip)'
      })

      //HAVE NOT DONE PIE CHART BACKGROUND

      //LABEL PROPERTIES
      .selector('node[color]').css({
        'color': 'data(color)'
      })
      .selector('node[content]').css({
        'content': 'data(content)'
      })
      .selector('node[font_family]').css({
        'font-family': 'data(font_family)'
      })
      .selector('node[font_size]').css({
        'font-size': 'data(font_size)'
      })
      .selector('node[font_style]').css({
        'font-style': 'data(font_style)'
      })
      .selector('node[font-weight]').css({
        'font-weight': 'data(font_weight)'
      })
      .selector('node[text-transform]').css({
        'text-transform': 'data(text_transform)'
      })
      .selector('node[text_wrap]').css({
        'text-wrap': 'data(text_wrap)'
      })
      .selector('node[text_max_width]').css({
        'text-max-width': 'data(text_max_width)'
      })
      .selector('node[edge_text_rotation]').css({
        'edge-text-rotation': 'data(edge_text_rotation)'
      })
      .selector('node[text-opacity]').css({
        'text-opacity': 'data(text_opacity)'
      })
      .selector('node[text_outline_color]').css({
        'text-outline-color': 'data(text_outline_color)'
      })
      .selector('node[text_outline_opacity]').css({
        'text-outline-opacity': 'data(text_outline_opacity)'
      })
      .selector('node[text_outline_width]').css({
        'text-outline-width': 'data(text_outline_width)'
      })
      .selector('node[text_shadow_blur]').css({
        'text-shadow-blur': 'data(text_shadow_blur)'
      })
      .selector('node[text_shadow_color]').css({
        'text-shadow-color': 'data(text_shadow_color)'
      })
      .selector('node[text_shadow_offset_x]').css({
        'text-shadow-offset-x': 'data(text_shadow_offset_x)'
      })
      .selector('node[text_shadow_offset_y]').css({
        'text-shadow-offset-y': 'data(text_shadow_offset_y)'
      })
      .selector('node[text_shadow_opacity]').css({
        'text-shadow-opacity': 'data(text_shadow_opacity)'
      })
      .selector('node[text_background_shape]').css({
        'text-background-shape': 'data(text_background_shape)'
      })
      .selector('node[text_border_width]').css({
        'text-border-width': 'data(text_border_width)'
      })
      .selector('node[text_border_style]').css({
        'text-border-style': 'data(text_border_style)'
      })
      .selector('node[text_border_color]').css({
        'text-border-color': 'data(text_border_color)'
      })
      .selector('node[min_zoomed_font_size]').css({
        'min-zoomed-font-size': 'data(min_zoomed_font_size)'
      })
      .selector('node[text_halign]').css({
        'text-halign': 'data(text_halign)'
      })
      .selector('node[text_valign]').css({
        'text-valign': 'data(text_valign)'
      })

      //EDGE LINE PROPERTIES
      .selector('edge[width]').css({
        'width': 'data(width)'
      })
      .selector('edge[curve_style]').css({
        'curve-style': 'data(curve_style)'
      })
      .selector('edge[haystack-radius]').css({
        'haystack-radius': 'data(haystack-radius)'
      })
      .selector('edge[control_point_step_size]').css({
        'control-point-step-size': 'data(control_point_step_size)'
      })
      .selector('edge[control_point_distance]').css({
        'control-point-distance': 'data(control_point_distance)'
      })
      .selector('edge[control_point_weight]').css({
        'control-point-weight': 'data(control_point_weight)'
      })
      .selector('edge[line_color]').css({
        'line-color': 'data(line_color)'
      })
      .selector('edge[line_style]').css({
        'line-style': 'data(line_style)'
      })

      //EDGE ARROW PROPERTIES
      .selector('edge[source_arrow_color]').css({
        'source-arrow-color': 'data(source_arrow_color)'
      })
      .selector('edge[source_arrow_shape]').css({
        'source-arrow-shape': 'data(source_arrow_shape)'
      })
      .selector('edge[source_arrow_fill]').css({
        'source-arrow-fill': 'data(source_arrow_fill)'
      })
      .selector('edge[mid_source_arrow_color]').css({
        'mid-source-arrow-color': 'data(mid_source_arrow_color)'
      })
      .selector('edge[mid_source_arrow_shape]').css({
        'mid-source-arrow-shape': 'data(mid_source_arrow_shape)'
      })
      .selector('edge[mid_source_arrow_fill]').css({
        'mid-source-arrow-fill': 'data(mid_source_arrow_fill)'
      })
      .selector('edge[target_arrow_color]').css({
        'target-arrow-color': 'data(target_arrow_color)'
      })
      .selector('edge[target_arrow_shape]').css({
        'target-arrow-shape': 'data(target_arrow_shape)'
      })
      .selector('edge[target_arrow_fill]').css({
        'target-arrow-fill': 'data(target_arrow_fill)'
      })
      .selector('edge[mid_target_arrow_color]').css({
        'mid-target-arrow-color': 'data(mid_target_arrow_color)'
      })
      .selector('edge[mid_target_arrow_shape]').css({
        'mid-target-arrow-shape': 'data(mid_target_arrow_shape)'
      })
      .selector('edge[mid_target_arrow_fill]').css({
        'mid-target-arrow-fill': 'data(mid_target_arrow_fill)'
      })

      .selector('node').css({
        'text-valign': 'center'
      })
    // .selector('edge')
    //   .css({
    //     'target-arrow-shape': 'data(arrow)',
    //     'line-color': 'data(color)',
    //     'source-arrow-color': 'data(color)',
    //     'target-arrow-color': 'data(color)',
    //   })
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
    
    // default layout set to be arbor
    layout: getLayoutFromQuery(),
    
    // draw graph, handle events etc.
    ready: function(){

      //Adding in the panzoom functionality 
      this.panzoom();
      
      // make the selection states of the elements mutable
      this.elements().selectify();

      setDefaultNodeProperties(graph_json['graph']['nodes'])
      // DONE SO OLD GRAPHS WILL DISPLAY
      //If the EDGES in graphs already in database don't have color have a default value
      for (var i = 0; i < graph_json['graph']['edges'].length; i++) {
        var edgeData = graph_json['graph']['edges'][i]['data'];

        if (edgeData['color'] == undefined) {
          edgeData['color'] = "black";
        } else {
          var hexCode = colourNameToHex(edgeData['color']);
           if (hexCode != false) {
            edgeData['color'] = hexCode;
           } else {
            if (isHexaColor(addCharacterToHex(edgeData['color']))) {
              edgeData['color'] = addCharacterToHex(edgeData['color']);
            }
           }
        }

        if (edgeData['directed'] == false) {
          edgeData['target_arrow_shape'] = 'none';
        } else {
          edgeData['target_arrow_shape'] = 'triangle';
        }
      }

      // load the graph to display
      this.load(graph_json.graph, function(e) {
        console.log('working');
      }, function() {
        console.log('done');
      });

      // enable user panning (hold the left mouse button to drag
      // the screen)
      this.userPanningEnabled(false);
      
      // display node data as a popup
      this.on('tap', function(evt){
        window.cy.elements().removeCss('color');
        // get target
        var target = evt.cyTarget;
        // target some element other than background (node/edge)
        if ( target !== this ) {
            var popup = target._private.data.popup

            window.cy.$('[id="' + target._private.data.id + '"]').css('color', 'red');

            if (popup == null || popup.length == 0) {
                return;
            }

            if (target._private.data.popup != null && target._private.data.popup.length > 0) {
              $("#dialog").html("<p>" + target._private.data.popup + "</p>");
            }
            if (target._private.group == 'edges') {
              // $.post("../../../retrieveIDs/", {
              //   'values': [target._private.data.source, target._private.data.target],
              //   "gid": decodeURIComponent(paths[paths.length - 2]),
              //   "uid": decodeURIComponent(paths[paths.length - 3]),
              //   "search_type": "full_search" 
              // }, function (data) {
              //   console.log(data);
              // });
              
              $('#dialog').dialog('option', 'title', target._private.data.source + "->" + target._private.data.target);
            } else {
              $('#dialog').dialog('option', 'title', target._private.data.content);
            }
            $("#dialog").dialog({
              'maxHeight': 500
            });
            $('#dialog').dialog('open');

        } else {
          window.cy.elements().removeCss('color');
        }
      });



      // //If ther are any terms to be searched for, highlight those terms, if found
      if (getQueryVariable('partial_search')) {
          // Initially set search to full matching
          $("#partial_search").attr('checked', true);
       } else if (getQueryVariable('full_search')){
          // Initially set search to full matching
          $("#full_search").attr('checked', true);
       } else {
          $("#partial_search").attr('checked', true);
       }

       searchOnLoad();

    } // end ready: function()
    });

    cy.boxSelectionEnabled(true);

    //setup popup dialog for displaying dialog when nodes/edges
    //are clicked for information.
    $('#dialog').dialog({ autoOpen: false });

    //these accordions make up the side menu
    $('#accordion_graph_details').accordion({
        collapsible: true,
        active: true,
        // heightStyle: "content"
    });

    $('#accordion_export').accordion({
        collapsible: true,
        active: false 
    });

    $("#accordion_search").accordion({
        collapsible: true,
        heightStyle: "content"
    });

    $('#accordion_owner').accordion({
        collapsible: true,
        active: false 
    });

    $('#accordion_sharing').accordion({
        collapsible: true,
        active: false,
        heightStyle: "content"
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

        if (data.Error) {
          return alert(data.Error);
        }

        var layoutUrl = window.location.pathname + "?layout=" + layoutName;

        var searchTerms = getHighlightedTerms();
        if (searchTerms[0].length > 0) {
          layoutUrl += '&partial_search=';
          for (var i = 0; i < searchTerms[0].length; i++) {
            if (i < searchTerms[0].length - 1) {
              layoutUrl += searchTerms[0][i] + ',';
            } else {
              layoutUrl += searchTerms[0][i];
            }
          }      
        } 

        if (searchTerms[1].length > 0) {
          layoutUrl += '&full_search=';
          for (var i = 0; i < searchTerms[1].length; i++) {
            if (i < searchTerms[1].length - 1) {
              layoutUrl += searchTerms[1][i] + ',';
            } else {
              layoutUrl += searchTerms[1][i];
            }
          }      
        } 
        window.location.replace(layoutUrl);
      });
    });

    //Searches for the element inside the graph
     $("#search_button").click(function (e) {
      e.preventDefault();
      if ($("#search").val().length > 0) {
        window.cy.elements().removeCss();
        searchValues($('input[name=match]:checked').val(), $("#search").val());
      }
     });

    if (getQueryVariable($('input[name=match]:checked').val())) {
    $("#searching").val(decodeURIComponent(getQueryVariable($('input[name=match]:checked').val())));
   }

    $("#pdf").click(function (e) {
      html2canvas($("#csjs").first(), {
        onrendered: function(canvas) {
          var imgData = canvas.toDataURL("image/jpeg");
          var pdf = new jsPDF('landscape');
          pdf.addImage(imgData, 'JPEG', 0, 0, 300, 210);
          pdf.save("download.pdf");
        }
      });
    });

    $(".help").click(function (e) {
      e.preventDefault();
      window.location.href = "../../../help/#graph_panels";
    });

    $("#sharing_panel").click(function(e) {
      e.preventDefault();
      window.location.href = "../../../help/#sharing_panel";
    });

    $(".highlight").click(function (e) {
      e.preventDefault();
      linkToGraph = $(this).attr('id') + ',';

      var labels = $("#search").val().split(',');

      if ($("#partial_search").is(':checked')) {
        if (labels.length > 0 && labels[0].length > 0) {
            linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
            linkToGraph += '&partial_search=';
            for (var i = 0; i < labels.length; i++) {
              if (labels[i].trim().length > 0) {
                linkToGraph += labels[i].trim() + ',';
              }
            } 
        }
      } else {
        if (labels.length > 0 && labels[0].length > 0) {
          linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
          linkToGraph += '&full_search=';
          for (var i = 0; i < labels.length; i++) {
            if (labels[i].trim().length > 0) {
              linkToGraph += labels[i].trim() + ',';
            }
          } 
        }
      }

      linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);

      $("#layout_link").attr('href', linkToGraph);
      $("#layout_link").text("Link to this graph with distinguished elements");
      $("#layout_link").css('text-decoration', 'underline');
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
        if (data.Error) {
          return alert(data.Error);
        }
        window.location.href = data.url;
      })
    });

    $(".layout_links").tooltip();

    $(".layout_buttons").click(function (e) {
      e.preventDefault();
      // var searchTerms = getHighlightedTerms();
      if (document.URL.indexOf('?') > -1) {
        var linkToGraph = document.URL.substring(0, document.URL.indexOf('?'));
      } else {
        var linkToGraph = document.URL;
      }

      linkToGraph += '?layout=' + $(this).attr('href') + ',';

      var labels = $("#search").val().split(',');

      if ($("#partial_search").is(':checked')) {
        if (labels.length > 0 && labels[0].length > 0) {
            linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
            linkToGraph += '&partial_search=';
            for (var i = 0; i < labels.length; i++) {
              if (labels[i].trim().length > 0) {
                linkToGraph += labels[i].trim() + ',';
              }
            } 
        }
      } else {
        if (labels.length > 0 && labels[0].length > 0) {
          linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
          linkToGraph += '&full_search=';
          for (var i = 0; i < labels.length; i++) {
            if (labels[i].trim().length > 0) {
              linkToGraph += labels[i].trim() + ',';
            }
          } 
        }
      }

      linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);

      if (e.target == this) {
        window.location.href = linkToGraph;
      }
    });

    $(".public").click(function (e) {
      e.preventDefault();

      var paths = document.URL.split('/');
      var publicLayout = $(this).val();
      var userId = $("#loggedIn").text();
      var ownerId = decodeURIComponent(paths[paths.length - 3]);
      var gid = decodeURIComponent(paths[paths.length - 2]);

      $.post('../../../shareLayoutWithGroups/', {
        'layoutId': $(this).val(),
        'gid': gid,
        'owner': ownerId,
        'uid': userId
      }, function (data) {
        if (data.Error) {
          return alert(data.Error);
        }
        window.location.reload();
      });
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
              } 
            } else {
              if (ownerId == userId || data['Group_Information'][i]['group_owner'] == userId) {
                group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label><input type="checkbox" class="group_val" style="margin-right: 30px;" value="' + data['Group_Information'][i]['group_id'] + '12345__43121__' + data['Group_Information'][i]['group_owner'] + '">' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
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

    // $("#share_layout_with_selected_groups").click(function(e) {
    //   var paths = document.URL.split('/')
    //   var ownerId = decodeURIComponent(paths[paths.length - 3])
    //   var gid = decodeURIComponent(paths[paths.length - 2])

    //   $.post('../../../shareLayoutWithGroups/', {
    //     'layoutId': $("#layoutId").text(),
    //     'gid': gid,
    //     'owner': ownerId
    //   }, function (data) {
    //     console.log(data);
    //     // window.location.reload();
    //   });
    // });


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

$("#clear_search").click(function (e) {
  e.preventDefault();
  clearSearchTerms();
});

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

function searchOnLoad() {

  if (getQueryVariable('partial_search')) {
    searchValues('partial_search', getQueryVariable('partial_search'));
    searchVals = getQueryVariable('partial_search').split(',');
    $("#search").val(searchVals);
  } else if (getQueryVariable('full_search')) {
    searchValues('full_search', getQueryVariable('full_search'));
    searchVals = getQueryVariable('full_search').split(',');
    $("#search").val(searchVals);
  }
}

//Function to search through graph elements in order to highlight the 
//appropriate one
function searchValues(search_type, labels) {

  //split paths
  var paths = document.URL.split('/');

  var partialDistinction = Array();
  var exactDistinction = Array();  

  // window.cy.eles.removeCss();

  $("#search_error_text").text("");

  $("#search_error").css("display", "none");

  //posts to server requesting the id's from the labels
  //so cytoscape will recognize the correct element
  $.post("../../../retrieveIDs/", {
    'values': labels,
    "gid": decodeURIComponent(paths[paths.length - 2]),
    "uid": decodeURIComponent(paths[paths.length - 3]),
    "search_type": search_type 
  }, function (data) {

    data = JSON.parse(data);

    var displayLink = false;

    var oldHtml = $("#search_terms").html();

    if (labels.length > 0) {
    //Split the labels so we can reference the labels
    labels = labels.split(',');

    for (var i = 0; i < labels.length; i++) {

      if (data[labels[i]].length == 0) {
        $("#search_error").css("display", "block");
        if (labels[i].trim().length == 0) {
          $("#search_error_text").append("Please enter node or edge name!<br>");
        } else {
          $("#search_error_text").append(labels[i] + " not found!<br>");
        }
        $("#accordion_search").accordion({
            collapsible: true,
            heightStyle: "content"
        });
        $("#search_terms").html(oldHtml);
      }
      for (var j = 0; j < data[labels[i]].length; j++) {
        if (window.cy.$('[id="' + data[labels[i]][j] + '"]').selected() == false) {
          // Select the specified element and don't allow the user to unselect it until button is clicked again
          if (window.cy.$('[id="' + data[labels[i]][j] + '"]').isEdge()) {
            window.cy.$('[id="' + data[labels[i]][j] + '"]').css({'line-color': 'blue', 'line-style': 'dotted', 'width': 10});
            displayLink = true;
          } else {
            window.cy.$('[id="' + data[labels[i]][j] + '"]').css({'border-width': 10, 'border-color': 'blue'});
            displayLink = true;
          }

          if (search_type == 'partial_search') {
            labels[i].replace(" ", "")
            if (partialDistinction.indexOf(labels[i]) == -1) {
              partialDistinction.push(labels[i]);
            }
          } else {
            if (exactDistinction.indexOf(labels[i]) == -1) {
              exactDistinction.push(labels[i]);
            }
          }
        }
      }
    }

    if ((displayLink == true && partialDistinction.length > 0) || (displayLink == true && exactDistinction.length > 0)) {

        var linkToGraph = document.URL.substring(0, document.URL.indexOf('?'));
        var layout = getQueryVariable('layout');
        var highlighted = getHighlightedTerms();

        if (layout) {
          linkToGraph += '?layout=' + layout;
        }


        if (search_type == 'partial_search') {
          if (layout) {
            linkToGraph += '&partial_search=';
          } else {
            linkToGraph += '?partial_search=';
          }
        } else if (search_type == 'full_search') {
          if (layout) {
            linkToGraph += '&full_search=';
          } else {
            linkToGraph += '?full_search=';
          }
        }


        for (var i = 0; i < labels.length; i++) {
          if (labels[i].trim().length > 0) {
            linkToGraph += labels[i].trim() + ',';
          }
        }

        linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);

        $("#url").attr('href', linkToGraph);
        $("#url").css('text-decoration', 'underline');
        $("#url").text("Link to this graph with distinguished elements");
        $(".test").css("height", $(".test").height + 30);
    }
  }
  });
}

/**
 * Get all the highlighted terms in the graph.
 */
function getHighlightedTerms() {
  // Create a url with all the highlighted terms
  var partialHighlightedTerms = new Array();
  var fullHighlightedTerms = new Array();

  // Go through all of the highlighted terms
  $(".search").each(function (index) {
      var value = $(this).attr('value').split('_');
      if (value[0] == 'partial' && partialHighlightedTerms.indexOf(value[1]) == -1) {
        partialHighlightedTerms.push(value[1]);
      } else if (value[0] == 'exact' && fullHighlightedTerms.indexOf(value[1]) == -1) {
        fullHighlightedTerms.push(value[1]);
      }
  });

  return [partialHighlightedTerms, fullHighlightedTerms];
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

// Returns all the id's that are > k value
function showOnlyK() {
  if ($("#input_k").val().length > 0) {
    var maxVal = parseInt($("#input_k").val());

    window.cy.elements().show();
    hideList = window.cy.filter('[k > ' + maxVal+ ']');
    hideList.hide();
  }
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
function unselectTerm(terms) {
  terms = terms.split(',');
  for (var i = 0; i < terms.length; i++) {
    window.cy.$('[id="' + terms[i] + '"]').removeCss();
  }
}

function getLayoutFromQuery() {

    //The following code retrieves the specified layout
    //of a graph to be displayed.
    //Some of them are pre-defined. Check Cytoscapejs.org
    var graph_layout = {
      name: 'arbor',
      padding: 10,
      fit:true,
      animate: true,
      maxSimulationTime: 1000
    };

    var query = getQueryVariable("layout");

    if (query == "default_breadthfirst") {
      graph_layout = {
        name: "breadthfirst",
        padding: 10,
        fit: true,
        avoidOverlap: true,
        animate: false
      }
    } else if (query == "default_concentric") {
       graph_layout = {
        name: "concentric",
        fit: true,
        padding: 10,
        avoidOverlap: true,
        animate: false
      }
    } else if (query == "default_circle") {
       graph_layout = {
        name: "circle",
        padding: 10,
        fit: true,
        avoidOverlap: true,
        animate: false
      }
    } else if (query == "default_dagre") {
       graph_layout = {
        name: "dagre",
        fit: true,
        padding: 10,
        animate: false,
        nodeSep: 50,
        edgeSep: 50
      }
    } else if (query == 'default_cose') {
      graph_layout = {
        name: "cose",
        padding: 10,
        fit: true,
        animate: false,
        nodeOverlap: 30
      }
    } else if (query == "default_cola") {
      graph_layout = {
        name: "cola",        
        fit: true,
        nodeSpacing: function( node ){ return 20; },
        padding: 10,
        animate: false,
        avoidOverlap: true
      }
    }  else if (query == "default_arbor") {
      graph_layout = {
        name: "arbor",
        padding: 30,
        fit: true,
        animate: true,
        maxSimulationTime: 1000
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
      // var layout = getQueryVariable('layout');
      // if (layout.hasOwnProperty('json')) {
      //   console.log(layout.json);
      //   graph_layout = {
      //     name: 'preset',
      //     positions: JSON.parse(layout.json)
      //   };
      // }

       if (layout && layout.json != null) {
        graph_layout = {
          name: 'preset',
          positions: JSON.parse(layout.json)
        };
      } else {
          alert("Layout does not exist!");
          var loc = window.location.href;
          var baseLoc = loc.substring(0, loc.indexOf("?"));
          window.location.href = baseLoc;
      }
    }

    return graph_layout;
}

function clearSearchTerms() {
  window.cy.elements().removeCss();
  $("#search").val("");
}

/** 
* Returns the HEX value of a color
*/
function colourNameToHex(colour)
{
    var colours = {"aliceblue":"#f0f8ff","antiquewhite":"#faebd7","aqua":"#00ffff","aquamarine":"#7fffd4","azure":"#f0ffff",
    "beige":"#f5f5dc","bisque":"#ffe4c4","black":"#000000","blanchedalmond":"#ffebcd","blue":"#0000ff","blueviolet":"#8a2be2","brown":"#a52a2a","burlywood":"#deb887",
    "cadetblue":"#5f9ea0","chartreuse":"#7fff00","chocolate":"#d2691e","coral":"#ff7f50","cornflowerblue":"#6495ed","cornsilk":"#fff8dc","crimson":"#dc143c","cyan":"#00ffff",
    "darkblue":"#00008b","darkcyan":"#008b8b","darkgoldenrod":"#b8860b","darkgray":"#a9a9a9","darkgreen":"#006400","darkkhaki":"#bdb76b","darkmagenta":"#8b008b","darkolivegreen":"#556b2f",
    "darkorange":"#ff8c00","darkorchid":"#9932cc","darkred":"#8b0000","darksalmon":"#e9967a","darkseagreen":"#8fbc8f","darkslateblue":"#483d8b","darkslategray":"#2f4f4f","darkturquoise":"#00ced1",
    "darkviolet":"#9400d3","deeppink":"#ff1493","deepskyblue":"#00bfff","dimgray":"#696969","dodgerblue":"#1e90ff",
    "firebrick":"#b22222","floralwhite":"#fffaf0","forestgreen":"#228b22","fuchsia":"#ff00ff",
    "gainsboro":"#dcdcdc","ghostwhite":"#f8f8ff","gold":"#ffd700","goldenrod":"#daa520","gray":"#808080","green":"#008000","greenyellow":"#adff2f",
    "honeydew":"#f0fff0","hotpink":"#ff69b4",
    "indianred ":"#cd5c5c","indigo":"#4b0082","ivory":"#fffff0","khaki":"#f0e68c",
    "lavender":"#e6e6fa","lavenderblush":"#fff0f5","lawngreen":"#7cfc00","lemonchiffon":"#fffacd","lightblue":"#add8e6","lightcoral":"#f08080","lightcyan":"#e0ffff","lightgoldenrodyellow":"#fafad2",
    "lightgrey":"#d3d3d3","lightgreen":"#90ee90","lightpink":"#ffb6c1","lightsalmon":"#ffa07a","lightseagreen":"#20b2aa","lightskyblue":"#87cefa","lightslategray":"#778899","lightsteelblue":"#b0c4de",
    "lightyellow":"#ffffe0","lime":"#00ff00","limegreen":"#32cd32","linen":"#faf0e6",
    "magenta":"#ff00ff","maroon":"#800000","mediumaquamarine":"#66cdaa","mediumblue":"#0000cd","mediumorchid":"#ba55d3","mediumpurple":"#9370d8","mediumseagreen":"#3cb371","mediumslateblue":"#7b68ee",
    "mediumspringgreen":"#00fa9a","mediumturquoise":"#48d1cc","mediumvioletred":"#c71585","midnightblue":"#191970","mintcream":"#f5fffa","mistyrose":"#ffe4e1","moccasin":"#ffe4b5",
    "navajowhite":"#ffdead","navy":"#000080",
    "oldlace":"#fdf5e6","olive":"#808000","olivedrab":"#6b8e23","orange":"#ffa500","orangered":"#ff4500","orchid":"#da70d6",
    "palegoldenrod":"#eee8aa","palegreen":"#98fb98","paleturquoise":"#afeeee","palevioletred":"#d87093","papayawhip":"#ffefd5","peachpuff":"#ffdab9","peru":"#cd853f","pink":"#ffc0cb","plum":"#dda0dd","powderblue":"#b0e0e6","purple":"#800080",
    "red":"#ff0000","rosybrown":"#bc8f8f","royalblue":"#4169e1",
    "saddlebrown":"#8b4513","salmon":"#fa8072","sandybrown":"#f4a460","seagreen":"#2e8b57","seashell":"#fff5ee","sienna":"#a0522d","silver":"#c0c0c0","skyblue":"#87ceeb","slateblue":"#6a5acd","slategray":"#708090","snow":"#fffafa","springgreen":"#00ff7f","steelblue":"#4682b4",
    "tan":"#d2b48c","teal":"#008080","thistle":"#d8bfd8","tomato":"#ff6347","turquoise":"#40e0d0",
    "violet":"#ee82ee",
    "wheat":"#f5deb3","white":"#ffffff","whitesmoke":"#f5f5f5",
    "yellow":"#ffff00","yellowgreen":"#9acd32"};

    if (colour in Object.keys(colours)) {
      return colours[colour]
    }
    return false;
}

/**
* Makes specific layout the default layout for a graph.
*/
$(".default").click(function(e) {
  var paths = document.URL.split('/')
  var ownerId = decodeURIComponent(paths[paths.length - 3])
  var gid = decodeURIComponent(paths[paths.length - 2])

  $.post('../../../setDefaultLayout/', {
    'layoutId': $(this).val(),
    'gid': gid,
    'uid': ownerId
  }, function (data) {
    if (data.Error) {
      return alert(data.Error);
    }
    window.location.reload();
  });
});

/**
* Makes specific layout the default layout for a graph.
*/
$(".removeDefault").click(function(e) {
  var paths = document.URL.split('/')
  var ownerId = decodeURIComponent(paths[paths.length - 3])
  var gid = decodeURIComponent(paths[paths.length - 2])

  $.post('../../../removeDefaultLayout/', {
    'layoutId': $(this).val(),
    'gid': gid,
    'uid': ownerId
  }, function (data) {
    if (data.Error) {
      return alert(data.Error);
    }
    window.location.reload();
  });
});

/**
* Sets default properties of node objects.
*/
function setDefaultNodeProperties(nodeJSON) {
  // DONE SO OLD GRAPHS WILL DISPLAY
  //If the nodes in graphs already in database don't have width or height
  // or unrecognized shape, have a default value
  for (var i = 0; i < nodeJSON.length; i++) {
    var nodeData = nodeJSON[i]['data'];

    //VALUES CONSISTENT AS OF CYTOSCAPEJS 2.3.9
    var acceptedShapes = ["rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star"];

    if (acceptedShapes.indexOf(nodeData['shape'].toLowerCase()) == -1) {

      if (nodeData['shape'].toLowerCase() == 'diamond') {
        nodeData['shape'] = 'octagon';
      } else if (nodeData['shape'] == 'square') {
        if (nodeData['content'].length == 0) {
          nodeData['shape'] = 'rectangle';
          nodeData['height'] = 20;
          nodeData['width'] = 20;
        } else {
          nodeData['shape'] = "rectangle"
        }
      } else {
        nodeData['shape'] = 'ellipse';
      }
    } else {
      nodeData['shape'] = nodeData['shape'].toLowerCase();
    }

    if (nodeData['background_color'] == undefined) {
      nodeData['background_color'] = "yellow";
    } else {
       var hexCode = colourNameToHex(nodeData['background_color']);
       if (hexCode != false) {
        nodeData['background_color'] = hexCode;
       } else {
        if (isHexaColor(addCharacterToHex(nodeData['background_color']))) {
          nodeData['background_color'] = addCharacterToHex(nodeData['background_color']);
        }
       }
    }
  }
}

$("#input_k").bind("change", function() {
  setInputK();
});

function setInputK() {
  if ($("#input_k").val() < 0) {
   $("#input_k").val(0);
  }
  if (parseInt($("#input_k").val()) > parseInt($("#input_max").val())) {
   $("#input_k").val($("#input_max").val());
   
  }
  setBarToValue($("#input_k"), "slider");
  $("#slider").slider({value: $("#input_k").val(), max: $('#input_max').val()});
}

$("#input_max").bind("change", function() {
  if ($(this).val() < 0) {
   $(this).val(0);
  }
  var slider_max = $("#slider_max").slider("option", "max");
  if ($(this).val() > slider_max) {
   $(this).val(slider_max);
  }
  setBarToValue(this, "slider_max");
  applyMax(graph_json.graph);
  setInputK();
});

function setBarToValue(inputId, barId) {
  var slider_max = $("#slider_max").slider("option", "max");
  if ($(inputId).val() > slider_max) {
    $(inputId).val(slider_max);
  }
  showOnlyK();
}

