/* 
This function is executed when the page finishes loading.
Consult the API: http://api.jquery.com/ready/
*/
$(document).ready(function() {

    var clock = Clock;
    var logger = Logger;
    // Cytoscape.js API: 

    // http://cytoscape.github.io/cytoscape.js/
    setDefaultNodeProperties(graph_json['graph']['nodes']);
    extractJSONProperties(graph_json.graph);
    getFeedback();

    if (task_view == "True") {

        //Start keeping track of time
        clock.start(); 

        //start tracking all movements
        $(document).on("click focus blur keydown change",function(e){
             logger.addEvent(e);
        });
    }

    //Renders the cytoscape element on the page
    //with the given options
    window.cy = cytoscape({
        container: $('#csjs')[0],

        elements: graph_json["graph"],

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
            .selector('node[background_width]').css({
                'background-width': 'data(background_width)'
            })
            .selector('node[background_height]').css({
                'background-height': 'data(background_height)'
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
            .selector('node[font_weight]').css({
                'font-weight': 'data(font_weight)'
            })
            .selector('node[text_transform]').css({
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
            .selector('node[text_opacity]').css({
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
            .selector('edge[haystack_radius]').css({
                'haystack-radius': 'data(haystack_radius)'
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
        ready: function() {

                //if there is a title, insert title at top of page
                if ($("#title").text().length > 0) {
                    $("#graph_title").html("<h1>" + $("#title").text() + "</h1>");
                    $(".side_menu").css("margin-top", -50);
                }

                //Adding in the panzoom functionality 
                this.panzoom();

                // make the selection states of the elements mutable
                this.elements().selectify();

                var testEdges = new Array();

                setDefaultNodeProperties(graph_json['graph']['nodes'])

                // DONE SO OLD GRAPHS WILL DISPLAY
                // NEW GRAPHS WILL HAVE EVERYTHING HANDLED AT UPLOAD TIME
                // THIS IS ONLY AS A SECONDARY CHECK

                //If the EDGES in graphs already in database don't have color have a default value
                for (var i = 0; i < graph_json['graph']['edges'].length; i++) {
                    var edgeData = graph_json['graph']['edges'][i]['data'];

                    //If edges don't have an ID, generate one
                    if (testEdges.indexOf(edgeData['id']) == -1) {
                        testEdges.push(edgeData['id']);
                    } else {
                        edgeData['id'] = edgeData['id'] + i;
                    }

                    //If edges don't have any color properties, choose default 
                    if (edgeData['line_color'] == undefined && edgeData['color'] == undefined) {
                        edgeData['line_color'] = "black";
                    } else {

                        //Color property maps to line_color
                        //DONE TO SUPPORT OLD GRAPHS
                        if (edgeData.hasOwnProperty('color')) {
                            edgeData['line_color'] = edgeData['color'];
                        }
                        //Converts the line color into Hexadecimal so CytoscapeJS can user it
                        var hexCode = colourNameToHex(edgeData['line_color']);
                        if (hexCode != false) {
                            edgeData['line_color'] = hexCode;
                        } else {
                            if (isHexaColor(addCharacterToHex(edgeData['line_color']))) {
                                edgeData['line_color'] = addCharacterToHex(edgeData['line_color']);
                            }
                        }
                    }

                    //DONE TO SUPPORT OLD GRAPHS: If "directed" property is not there, edge is undirected, otherwise it is directed
                    if (edgeData['target_arrow_shape'] == undefined || (edgeData['directed'] == false || edgeData['directed'] == 'false')) {
                        edgeData['target_arrow_shape'] = 'none';
                    } else if (edgeData['directed'] == true) {
                        edgeData['target_arrow_shape'] = 'triangle';
                    }
                }

                // load the graph to display
                this.load(graph_json.graph, function(e) {
                    console.log('working');
                }, function() {
                    console.log('done');
                    applyLayoutStyles();
                });

                // enable user panning (hold the left mouse button to drag
                // the screen)
                this.userPanningEnabled(false);

                // display node data as a popup
                this.on('tap', function(evt) {
                    window.cy.elements().removeCss('color');
                    // get target
                    var target = evt.cyTarget;
                    // target some element other than background (node/edge)
                    if (target !== this) {
                        var popup = target._private.data.popup

                        //When user clicks an element, turn that element red
                        window.cy.$('[id="' + target._private.data.id + '"]').css('color', 'red');

                        //If there is no embedded content, don't display anything
                        if (popup == null || popup.length == 0) {
                            return;
                        }

                        //Display embedded content if there is any
                        if (target._private.data.popup != null && target._private.data.popup.length > 0) {
                            $("#dialog").html("<p>" + target._private.data.popup + "</p>");
                        }
                        if (target._private.group == 'edges') {
                            $('#dialog').dialog('option', 'title', target._private.data.source + "->" + target._private.data.target);
                        } else {
                            $('#dialog').dialog('option', 'title', target._private.data.content);
                        }
                        $("#dialog").dialog({
                            'maxHeight': 500
                        });
                        $('#dialog').dialog('open');

                    } else {
                        //If another element was clicked, remove the red color from previously clicked element
                        window.cy.elements().removeCss('color');
                    }
                });

                //If ther are any terms to be searched for, highlight those terms, if found
                if (getQueryVariable('partial_search')) {
                    // Initially set search to full matching
                    $("#partial_search").attr('checked', true);
                } else if (getQueryVariable('full_search')) {
                    // Initially set search to full matching
                    $("#full_search").attr('checked', true);
                } else {
                    $("#partial_search").attr('checked', true);
                }

                //Searches through the graph for nodes/edges that match the search term
                searchOnLoad();

                //If num_paths in query, set the k value 
                if (getQueryVariable('num_paths')) {
                    if ($("#input_k").val()) {
                        $("#input_k").val(getQueryVariable("num_paths"));
                    }
                }

                //If max_paths in query, set the k value 
                if (getQueryVariable('max_paths')) {
                    if ($("#input_max").val()) {
                        $("#input_max").val(getQueryVariable("max_paths"));
                    }
                }

                //Re-render graph allowing for a maximum of k
                applyMax(graph_json.graph);

            } // end ready: function()
    });

    //Unselect all nodes/edges when button is clicked
    $("#unselect").click(function(e) {
        e.preventDefault();
        for (var j = 0; j < window.cy.nodes().length; j++) {
            var node = window.cy.nodes()[j];
            node.unselect();
        }

        for (var j = 0; j < window.cy.edges().length; j++) {
            var edge = window.cy.edges()[j];
            edge.unselect();
        }

        $('input:checkbox[name=colors]').each(function(index) {
            $(this).prop('checked', false);
        });
        $('input:checkbox[name=shapes]').each(function(index) {
            $(this).prop('checked', false);
        });
    });

    var modifiedColor;

    $("#selectionPalette").spectrum({
        showPalette: true,
        palette: [],
        showSelectionPalette: true, // true by default
        change: function(color) {
            modifiedColor = color.toHexString();

            for (var j = 0; j < window.cy.nodes().length; j++) {
                var node = window.cy.nodes()[j];

                if (node.selected()) {
                    node.style("background-color", modifiedColor);
                    node.style("border-color", modifiedColor);
                    node.style("text-outline-color", modifiedColor);
                }
            }
        }

    });

    var modifiedShape;

    $(".dropdown-menu li a").click(function() {
        modifiedShape = $(this).data("value");

        for (var j = 0; j < window.cy.nodes().length; j++) {
            var node = window.cy.nodes()[j];

            if (node.selected()) {
                node.style("shape", modifiedShape);
            }
        }
    });

    function travelDistance(center, nodePosition) {
        var a = Math.abs(center.x - nodePosition.x);
        var b = Math.abs(center.y - nodePosition.y);
        var ratio = b / a;

        var miniH = Math.sqrt(1 + ratio * ratio);

        var distance = 0.10 * Math.sqrt(a * a + b * b);
        var travelX = distance / miniH;
        var travelY = ratio * travelX;

        return {
            x: travelX,
            y: travelY
        };
    }

    function groupUngroup(type) {
        var center = {
            x: window.cy.width() / 2,
            y: window.cy.height() / 2
        };

        for (var j = 0; j < window.cy.nodes().length; j++) {
            var node = window.cy.nodes()[j];

            if (node.selected()) {
                var position = node.renderedPosition();
                var distance = travelDistance(center, position);

                if (position.x < center.x) {
                    if (type == 1) {
                        position.x += distance.x;
                    } else {
                        position.x -= distance.x;
                    }

                }
                if (position.x > center.x) {
                    if (type == 1) {
                        position.x -= distance.x;
                    } else {
                        position.x += distance.x;
                    }
                }

                if (position.y < center.y) {
                    if (type == 1) {
                        position.y += distance.y;
                    } else {
                        position.y -= distance.y;
                    }
                }
                if (position.y > center.y) {
                    if (type == 1) {
                        position.y -= distance.y;
                    } else {
                        position.y += distance.y;
                    }
                }

                node.renderedPosition(position);
            }
        }
    }

    function grabNodePositions() {
        //When save is clicked, it gets location of all the nodes and saves it
        //so that nodes can be placed in this location later on
        var nodes = window.cy.elements('node');
        var layout = [];
        for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
            var nodeData = {
                'x': nodes[i]._private.position.x,
                'y': nodes[i]._private.position.y,
                'id': nodes[i]._private.data.id,
                'background_color': nodes[i]._private['style']['background-color']['strValue'],
                'shape': nodes[i]._private['style']['shape']['strValue']
            };
            layout.push(nodeData);
        }
        return layout;
    }

    function move(direction) {
        var distance = 15;

        for (var j = 0; j < window.cy.nodes().length; j++) {
            var node = window.cy.nodes()[j];

            if (node.selected()) {
                var position = node.renderedPosition();

                switch (direction) {
                    case "up":
                        position.y -= distance;
                        break;
                    case "down":
                        position.y += distance;
                        break;
                    case "left":
                        position.x -= distance;
                        break;
                    case "right":
                        position.x += distance;
                        break;
                    default:
                        position.x += 0;
                }
                node.renderedPosition(position);
            }
        }
    }

    $("#group").click(function(e) {
        e.preventDefault();
        groupUngroup(1);
    });

    $("#ungroup").click(function(e) {
        e.preventDefault();
        groupUngroup(2);
    });

    $("#upArrow").click(function(e) {
        e.preventDefault();
        move("up");
    });
    $("#leftArrow").click(function(e) {
        e.preventDefault();
        move("left");
    });
    $("#rightArrow").click(function(e) {
        e.preventDefault();
        move("right");
    });
    $("#downArrow").click(function(e) {
        e.preventDefault();
        move("down");
    });

    function intersect(a, b) {
        var t;
        if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
        return a.filter(function(e) {
            if (b.indexOf(e) !== -1) return true;
        });
    }

    //Allow a user to select multiple elements by dragging cursor across
    cy.boxSelectionEnabled(true);

    //setup popup dialog for displaying dialog when nodes/edges
    //are clicked for information.
    $('#dialog').dialog({
        autoOpen: false
    });

    $("#guidelines").accordion({
        collapsible:true,
        active:false
    });

    $("#notes").accordion({
        collapsible:true,
        active:false,
        heightStyle: "content"
    });

    $('#accordion_design').accordion({
        collapsible: true,
        heightStyle: "auto",
        // autoHeight: false,
        clearStyle: true,
        // active: 0
    });

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

        var layout = grabNodePositions();

        var queryString = location.href.split(location.host)[1].split("?")[0];
        //Posts information to the server regarding the current display of the graph,
        //including position
        $.post(queryString + "/layout/", {
            layout_name: layoutName,
            points: JSON.stringify(layout),
            loggedIn: $("#loggedIn").text(),
            "public": 0,
            "unlisted": 0
        }, function(data) {
            console.log(data);
            if (data.Error) {
                return alert(data.Error);
            }

            var layoutUrl = window.location.pathname;

            //Get rid of trailing '/' character
            if (layoutUrl.charAt(layoutUrl.length - 1) == "/") {
                layoutUrl = layoutUrl.substring(0, layoutUrl.length - 1);
            }

            //If layout, append layout URL
            layoutUrl += "?layout=" + layoutName + "&layout_owner=" + $("#loggedIn").text();

            //Get all highlighted terms and append them to the 
            //url of each layout.
            //Done so the highlighted elements stay highlighted
            //when user clicks a layout
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

            //Get all highlighted terms and append them to the 
            //url of each layout.
            //Done so the highlighted elements stay highlighted
            //when user clicks a layout        
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
    $("#search_button").click(function(e) {
        e.preventDefault();
        if ($("#search").val().length > 0) {
            // window.cy.elements().removeCss();
            searchValues($('input[name=match]:checked').val(), $("#search").val());
        }
    });



    //Highlights appropriate radio button based on search term
    if (getQueryVariable($('input[name=match]:checked').val())) {
        $("#searching").val(decodeURIComponent(getQueryVariable($('input[name=match]:checked').val())));
    }

    //Goes to appropriate help section
    $(".help").click(function(e) {
        e.preventDefault();
        window.location.href = "../../../help/#graph_panels";
    });

    $("#sharing_panel").click(function(e) {
        e.preventDefault();
        window.location.href = "../../../help/#sharing_panel";
    });

    //if there are multiple search terms, append the search term
    //to the URL.  Be sure to track for if its a partial or exact search
    $(".highlight").click(function(e) {
        e.preventDefault();
        linkToGraph = "?layout=" + $(this).val() + "&layout_owner=" + $(this).attr("id");

        //Get all labels form search term
        var labels = $("#search").val().split(',');

        //If partial is checked append all search terms,
        //otherwise append all search terms for full search
        if ($("#partial_search").is(':checked')) {
            if (labels.length > 0 && labels[0].length > 0) {
                // linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
                linkToGraph += '&partial_search=';
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].trim().length > 0 && i < labels.length - 1) {
                        linkToGraph += labels[i].trim() + ',';
                    } else {
                        linkToGraph += labels[i].trim();
                    }
                }
            }
        } else {
            //The exact search is being used
            if (labels.length > 0 && labels[0].length > 0) {
                // linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
                linkToGraph += '&full_search=';
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].trim().length > 0 && i < labels.length - 1) {
                        linkToGraph += labels[i].trim() + ',';
                    } else {
                        linkToGraph += labels[i].trim();
                    }
                }
            }
        }

        //When appropriate icon is clicked, show link
        //otherwise hide it.
        $("#layout_link").attr('href', linkToGraph);
        if ($("#layout_link").html().length > 0) {
            $("#layout_link").html("");
        } else {
            $("#layout_link").html("<p>Link to this graph with distinguished elements</p><hr>");
        }
        $("#layout_link").css('text-decoration', 'underline');
        $("#layout_link").width(20);
    });

    //Shows modal that allows user to change name of layout
    $(".change").click(function(e) {
        e.preventDefault();
        $("#change_modal").modal('toggle');
        $("#change_layout").val($(this).val());
    });

    //Changes the name of the current layout
    $("#change_layout").click(function(e) {
        var new_layout_name = $("#new_layout_name").val();

        var gid = $("#gid").text();
        var uid = $("#uid").text();
        var loggedIn = $("#loggedIn").text();
        var old_layout_name = $(this).val()

        if (new_layout_name.length == 0) {
            return alert("Enter a new layout name!");
        } else {
            $.post('../../../changeLayoutName/', {
                "gid": gid,
                "uid": uid,
                "loggedIn": loggedIn,
                "old_layout_name": old_layout_name,
                "new_layout_name": new_layout_name
            }, function(data) {
                if (data.Error) {
                    alert(data.Error);
                    return;
                }
                window.location.href = data.url;
            });
        }
    });

    //Deletes the current layout from graph
    $(".remove").click(function(e) {
        e.preventDefault();

        var publicLayout = $(this).val();
        var userId = $(this)[0]["id"];
        var gid = $("#gid").text();
        var uid = $("#uid").text();

        $.post('../../../deleteLayout/', {
            'gid': gid,
            'owner': uid,
            'layout': publicLayout,
            'layout_owner': userId
        }, function(data) {
            if (data.Error) {
                return alert(data.Error);
            }
            window.location.href = data.url;
        })
    });

    //Tells what each icon for layout does
    $(".layout_links").tooltip();

    //If clicked, graph re-renders with correct layout
    //including all search terms
    $(".layout_buttons").click(function(e) {
        e.preventDefault();

        var linkToGraph = $(this).attr('href');

        if (linkToGraph == undefined) {
            //Get hardcoded automatic layout ** doesn't need layout_owner **
            linkToGraph = window.location.pathname + "?layout=" + $(this).attr("id");
        }
        var labels = $("#search").val().split(',');

        //Appends partial search terms as part of query string
        if ($("#partial_search").is(':checked')) {
            if (labels.length > 0 && labels[0].length > 0) {
                // linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
                linkToGraph += '&partial_search=';
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].trim().length > 0 && i < labels.length - 1) {
                        linkToGraph += labels[i].trim() + ',';
                    } else {
                        linkToGraph += labels[i].trim();
                    }
                }
            }
        } else {
            if (labels.length > 0 && labels[0].length > 0) {
                // linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
                linkToGraph += '&full_search=';
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].trim().length > 0 && i < labels.length - 1) {
                        linkToGraph += labels[i].trim() + ',';
                    } else {
                        linkToGraph += labels[i].trim();
                    }
                }
            }
        }

        if (e.target == this) {
            window.location.href = linkToGraph;
        }
    });

    //If clicked, it shares layouts with all groups
    $(".public").click(function(e) {
        e.preventDefault();

        var paths = document.URL.split('/');
        var publicLayout = $(this).val();
        var userId = $(this).attr("id");
        var gid = $("#gid").text();
        var uid = $("#uid").text();

        $.post('../../../shareLayoutWithGroups/', {
            'layoutId': $(this).val(),
            'gid': gid,
            'uid': uid,
            'loggedIn': userId
        }, function(data) {
            if (data.Error) {
                return alert(data.Error);
            }
            window.location.reload();
        });
    });

    //Reveals modal of all groups user is a member/owner of
    $("#share_graph").click(function(e) {
        e.preventDefault();

        var paths = document.URL.split('/')
        var publicLayout = $(this).val();
        var userId = $("#loggedIn").text();
        var gid = $("#gid").text();
        var uid = $("#uid").text();

        $.post('../../../getGroupsForGraph/', {
            'gid': gid,
            'owner': uid,
        }, function(data) {
            var group_options = "";
            if (data['Group_Information'].length > 0) {
                //Used for modal to determine if graph is shared with group or not
                for (var i = 0; i < data['Group_Information'].length; i++) {
                    if (data['Group_Information'][i]['graph_shared'] == true) {
                        if (uid == userId || data['Group_Information'][i]['group_owner'] == userId) {
                            group_options += '<li class="list-group-item groups" style="font-size: 15px;"><label><input type="checkbox" class="group_val" checked="checked" style="margin-right: 30px;" value="' + data['Group_Information'][i]['group_id'] + '12345__43121__' + data['Group_Information'][i]['group_owner'] + '">' + data['Group_Information'][i]['group_id'] + " owned by: " + data['Group_Information'][i]['group_owner'] + '</label></li>';
                        }
                    } else {
                        if (uid == userId || data['Group_Information'][i]['group_owner'] == userId) {
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

    //Shares graphs with specified groups user is a member/owner of
    $("#share_graph_with_selected_groups").click(function(e) {
        var paths = document.URL.split('/')
        var gid = $("#gid").text();
        var uid = $("#uid").text();

        var all_groups = {}
        var groups_to_share_with = [];
        var groups_not_to_share_with = [];

        $(".group_val").each(function() {
            if (all_groups.hasOwnProperty($(this).val()) == false) {
                all_groups[$(this).val()] = $(this).is(":checked");
            }
        });

        //If user clicks a group to share with, get all those groups and send
        //to server so multiple groups can share one graph with one request
        for (var key in all_groups) {
            if (all_groups[key] == true) {
                groups_to_share_with.push(key);
            } else {
                groups_not_to_share_with.push(key);
            }
        }

        $.post('../../../shareGraphWithGroups/', {
            'gid': gid,
            'owner': uid,
            'groups_to_share_with': groups_to_share_with,
            'groups_not_to_share_with': groups_not_to_share_with
        }, function(data) {
            window.location.reload();
        });
    });

    //Hides appropriate nodes based on k value
    $("#input_k").val(getLargestK(graph_json.graph));

    //Shows up to maximum k values 
    $("#input_max").val(getLargestK(graph_json.graph));

    //When user slides, it changes value of slider as well
    //as updates graph to reflect max k values allowed in subgraph
    $("#slider_max").slider({
        step: 1,
        min: 0,
        max: getLargestK(graph_json.graph),
        value: getLargestK(graph_json.graph),
        slide: function(event, ui) {
            $("#input_max").val(ui.value);
            m_val = ui.value;
            if (m_val < 0) {
                m_val = 0;
                $(this).slider({
                    value: 0
                });
            } else {
                $(this).slider({
                    value: m_val
                });
                $("#slider").slider({
                    max: m_val
                });
                $("#input_k").val($("#slider").slider('value'));
            }
        },
        change: function(event, ui) {
            if (event.originalEvent) {
                applyMax(graph_json.graph)
            }
        }
    });

    //When user slides, it changes value of slider as well
    //as updates graph to reflect max k values allowed in subgraph
    $("#slider").slider({
        value: $("#slider_max").slider('value'),
        max: $("#slider_max").slider('value'),
        min: 0,
        step: 1,
        slide: function(event, ui) {
            $("#input_k").val(ui.value);
            m_val = ui.value;
            if (m_val < 0) {
                m_val = 0;
                $(this).slider({
                    value: 0
                });
            }
        },
        change: function(event, ui) {
            if (event.originalEvent) {
                showOnlyK();
            }
        }
    });

    var colorValues = []
    $('input:checkbox[name=colors]').click(function() {
        colorValues = $('input:checkbox[name=colors]:checked').map(function() {
            return "#" + this.id
        }).get();

        combineSelections("background-color", colorValues, "shape", shapeValues);

    });

    var shapeValues = []
    $('input:checkbox[name=shapes]').click(function() {
        shapeValues = $('input:checkbox[name=shapes]:checked').map(function() {
            return this.id
        }).get();

        combineSelections("shape", shapeValues, "background-color", colorValues);
    });

    //Clears search terms
    $("#clear_search").click(function(e) {
        e.preventDefault();
        clearSearchTerms();
        $("#search_error").text("");
        $("#search_error").css("display", "none");
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
    function fireEvent(obj, evt) {
        var fireOnThis = obj;
        if (document.createEvent) {
            var evObj = document.createEvent('MouseEvents');
            evObj.initEvent(evt, true, false);
            fireOnThis.dispatchEvent(evObj);
        } else if (document.createEventObject) {
            var evObj = document.createEventObject();
            fireOnThis.fireEvent('on' + evt, evObj);
        }
    }

    //When graph is loaded, go through query string
    //and highlight appropriate variables
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

    //Go through graph and find the k value of a label 
    function findKValueOfLabel(label) {
        for (edge in graph_json['graph']['edges']) {
            if (graph_json['graph']['edges'][edge]['data']['id'] == label) {
                return graph_json['graph']['edges'][edge]['data']['k'];
            }
        }

        for (node in graph_json['graph']['nodes']) {
            if (graph_json['graph']['nodes'][node]['data']['id'] == label) {
                return graph_json['graph']['nodes'][node]['data']['k'];
            }
        }
    }

    //Function to search through graph elements in order to highlight the 
    //appropriate one
    function searchValues(search_type, labels) {

        labelCheck = labels.split(",");

        var newLabels = "";

        //Get the labels from array to a string seperated by commas
        for (var i = 0; i < labelCheck.length; i++) {
            if (labelCheck[i].length > 0) {
                if (newLabels.length == 0) {
                    newLabels += labelCheck[i];
                } else {
                    newLabels += "," + labelCheck[i];
                }
            }
        }


        labels = newLabels;

        //split paths
        var paths = document.URL.split('/');

        //Keep track of partial/exact search
        var partialDistinction = Array();
        var exactDistinction = Array();

        $("#search_error_text").text("");

        $("#search_error").css("display", "none");

        //posts to server requesting the id's from the labels
        //so cytoscape will recognize the correct element
        $.post("../../../retrieveIDs/", {
            'values': labels,
            "gid": $("#gid").text(),
            "uid": $("#uid").text(),
            "search_type": search_type
        }, function(data) {
            data = JSON.parse(data);

            var displayLink = false;

            var oldHtml = $("#search_terms").html();

            if (labels.length > 0) {
                //Split the labels so we can reference the labels
                labels = labels.split(',');
                var k_problems = [];
                for (var i = 0; i < labels.length; i++) {
                    //if the labels that are retrieved from server doesn't exist
                    if (data[labels[i]].length == 0) {
                        if (labels[i].trim().length == 0) {
                            $("#search_error_text").append("Please enter node or edge name!<br>");
                        } else {
                            $("#search_error_text").append(labels[i] + " not found!<br>");
                        }
                        $("#search_error").css("display", "block");
                        $("#accordion_search").accordion({
                            collapsible: true,
                            heightStyle: "content"
                        });
                        $("#search_terms").html(oldHtml);
                    }

                    //Get the value of k if it exists
                    var k_val = $("#input_k").val();

                    //Go through all data that is returned from the server and make sure that the k value is <= to what is being shown 
                    for (var j = 0; j < data[labels[i]].length; j++) {
                        if (findKValueOfLabel(data[labels[i]][j]) !== undefined && findKValueOfLabel(data[labels[i]][j]) !== null && k_val !== undefined && findKValueOfLabel(data[labels[i]][j]) > k_val) {
                            k_problems.push(findKValueOfLabel(data[labels[i]][j]));
                        }

                        if (window.cy.$('[id="' + data[labels[i]][j] + '"]').selected() == false) {
                            // Select the specified element and don't allow the user to unselect it until button is clicked again
                            if (window.cy.$('[id="' + data[labels[i]][j] + '"]').isEdge()) {
                                window.cy.$('[id="' + data[labels[i]][j] + '"]').css({
                                    'line-color': 'blue',
                                    'line-style': 'dotted',
                                    'width': 10
                                });
                                displayLink = true;
                            } else {
                                window.cy.$('[id="' + data[labels[i]][j] + '"]').css({
                                    'border-width': 10,
                                    'border-color': 'blue'
                                });
                                displayLink = true;
                            }

                            //displayLink will display the link to get to this graph (for sharing purposes)

                            //Populate the appropriate array according to the search
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

                //If there are any errors, report them to the user
                if (k_problems.length > 0) {
                    var message = "";
                    $("#search_error").css("display", "block");

                    var maxProblem = 0;
                    for (var a = 0; a < k_problems.length; a++) {
                        maxProblem = Math.max(maxProblem, k_problems[a]);
                    }

                    if (k_problems.length > 0) {
                        message = "A node or edge matches the search term but is not visible.";
                    } else {
                        message = "Multiple nodes or edges match the search term but some of them are not visible.";
                    }

                    if (maxProblem > $("#input_max").val()) {
                        message += " Please set 'Number of paths' and 'Maximum number of paths' to at least " + maxProblem + " to view all of the searched terms.";
                    } else {
                        message += " Please set 'Number of paths' to at least " + maxProblem + " to view all of the searched terms."
                    }

                    $("#search_error_text").append(message);
                }

                //If link is to be displayed and there are matching elements, generate link including search queries
                if ((displayLink == true && partialDistinction.length > 0) || (displayLink == true && exactDistinction.length > 0)) {

                    var linkToGraph = document.URL.substring(0, document.URL.indexOf('?'));
                    var layout = getQueryVariable('layout');
                    var layout_owner = getQueryVariable("layout_owner");
                    var highlighted = getHighlightedTerms();

                    if (layout) {
                        linkToGraph += '?layout=' + layout + "&layout_owner=" + layout_owner;
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

                    $("#url").attr('href', linkToGraph);
                    $("#url").css('text-decoration', 'underline');
                    $("#url").html("<p id='testing1'>Link to this graph with distinguished elements</p>");
                    $(".test").css("height", $(".test").height + 30);
                } else {
                    $("#url").html("");
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
        $(".search").each(function(index) {
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
    function isHexaColor(sNum) {
        return (typeof sNum === "string") && sNum.length === 7 && !isNaN(parseInt(sNum.substring(1), 16)) && sNum.substring(0, 1) == '#';
    }

    //Appends # character if string is hex
    function addCharacterToHex(sNum) {
        if (sNum.length == 6 && !isNaN(parseInt(sNum, 16))) {
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
    function getQueryVariable(variable) {
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            if (pair[0] == variable) {
                return pair[1];
            }
        }
        return (false);
    }

    /**
     * Get all properties of the JSON
     */
    function extractJSONProperties(graphJson) {
        var nodePropertyDictionary = {};
        // var edgePropertyDictionary = {};

        //Get all the node properties
        for (var i = 0; i < graphJson.nodes.length; i++) {
            var node = graphJson.nodes[i].data;

            var keys = Object.keys(node);

            for (var j in keys) {
                var key = keys[j];
                if (key == "shape" || key == "background_color") {
                    if (nodePropertyDictionary.hasOwnProperty(key)) {
                        var curArray = nodePropertyDictionary[key];
                        if (curArray.indexOf(node[key]) == -1) {
                            curArray.push(node[key]);
                            nodePropertyDictionary[key] = curArray;
                        }
                    } else {
                        nodePropertyDictionary[key] = [node[key]];
                    }
                }
            }
        }

        // //Get all the edge properties
        // for (var i = 0; i < graphJson.edges.length; i++) {
        //     var edge = graphJson.edges[i].data;
        //     var keys = Object.keys(edge);

        //     for (var j in keys) {
        //         var key = keys[j];
        //         if (edgePropertyDictionary.hasOwnProperty(key)) {
        //             var curArray = edgePropertyDictionary[key];
        //             curArray.push(edge[key]);
        //             edgePropertyDictionary[key] = curArray;
        //         } else {
        //             edgePropertyDictionary[key] = [edge[key]];
        //         }
        //     }
        // }

        var layoutPropertyDictionary = {};
        if (layout && layout["json"] != null) {
            var parsed_json = JSON.parse(layout.json);
            for (var i in parsed_json) {
                var node_obj = parsed_json[i];
                var colorKey = "background_color";
                var shapeKey = "shape";

                if (layoutPropertyDictionary.hasOwnProperty(colorKey)) {
                    var curArray = layoutPropertyDictionary[colorKey];

                    if (node_obj.hasOwnProperty(colorKey)) {
                        if (curArray.indexOf(node_obj[colorKey]) == -1) {
                            curArray.push(node_obj[colorKey]);
                            layoutPropertyDictionary[colorKey] = curArray;
                        }
                    } else {
                        layoutPropertyDictionary[colorKey] = nodePropertyDictionary[colorKey];
                    }
                } else {
                    layoutPropertyDictionary[colorKey] = nodePropertyDictionary[colorKey];
                }

                if (layoutPropertyDictionary.hasOwnProperty(shapeKey)) {
                    var curArray = layoutPropertyDictionary[shapeKey];

                    if (node_obj.hasOwnProperty(shapeKey)) {
                        if (curArray.indexOf(node_obj[shapeKey]) == -1) {
                            curArray.push(node_obj[shapeKey]);
                            layoutPropertyDictionary[shapeKey] = curArray;
                        }
                    } else {
                        layoutPropertyDictionary[shapeKey] = nodePropertyDictionary[shapeKey];
                    }
                } else {
                    layoutPropertyDictionary[shapeKey] = nodePropertyDictionary[shapeKey];
                }

            }
        } else {
            layoutPropertyDictionary = nodePropertyDictionary;
        }

        //Go through and display all the different properties in template
        for (var key in layoutPropertyDictionary) {
            var subtitle = "";
            if (key == "background_color") {
                subtitle = "Background Color";
                $("#selection").append("<p data-intro='You can select multiple nodes that have the same background color.' data-step='3' style='text-align: left; font-weight: bold;'>" + subtitle + "</p>");
            } else {
                subtitle = "Shape";
                $("#selection").append("<p data-intro='You can select multiple nodes that have the same shape.' data-step='4' style='text-align: left; font-weight: bold;'>" + subtitle + "</p>");
            }
            var valueArray = layoutPropertyDictionary[key];
            var checkboxString = "<p style='text-align: left;'>";

            for (var index in valueArray) {
                var value = valueArray[index];
                if (key == "background_color") {
                    value = colourNameToHex(value);

                    if (value == false) {
                        value = valueArray[index];
                    }
                    checkboxString += '<input id="' + value.substring(1) + '" type="checkbox" value="select_color" name="colors">&nbsp;<canvas class="canvas" id="' + value.substring(1) + '" width="20" height="20"></canvas>&nbsp;&nbsp;&nbsp;';
                } else {
                    checkboxString += '<input id="' + value + '" type="checkbox" value="select_shape" name="shapes">&nbsp;' + value[0].toUpperCase() + value.slice(1) + '&nbsp;&nbsp;&nbsp;';
                }
                if ((index + 1) % 3 == 0) {
                    checkboxString += "<br><br>";
                }
            }
            checkboxString += "</p>";
            $("#selection").append(checkboxString);

            $(".canvas").each(function() {
                $(this)[0].getContext("2d").fillStyle = "#" + $(this)[0].id;
                $(this)[0].getContext("2d").fillRect(0, 0, 20, 20);
            });
        }
    };

    function combineSelections(selection1, selectionArray1, selection2, selectionArray2) {

        var matching_shape_nodes = []

        var shapes = []
        for (var i = 0; i < selectionArray1.length; i++) {
            var shape = selectionArray1[i];
            for (var j = 0; j < window.cy.nodes().length; j++) {
                var node = window.cy.nodes()[j];

                var nodeShape = node.style(selection1);
                if (selectionArray1.indexOf(nodeShape) != -1) {
                    shapes.push(nodeShape);
                    matching_shape_nodes.push(node["_private"]["data"]["id"]);
                }
            }
        }

        var matching_color_nodes = []
        var colors = []
        for (var i = 0; i < selectionArray2.length; i++) {
            var color = selectionArray2[i];
            for (var j = 0; j < window.cy.nodes().length; j++) {
                var node = window.cy.nodes()[j];

                var nodeColor = node.style(selection2);
                if (selectionArray2.indexOf(nodeColor) != -1) {
                    colors.push(nodeColor);
                    matching_color_nodes.push(node["_private"]["data"]["id"]);
                }
            }
        }

        matching_nodes = []
        if (selectionArray2.length > 0 && selectionArray1.length > 0) {
            matching_nodes = intersect(matching_shape_nodes, matching_color_nodes);
        } else if (selectionArray2.length > 0) {
            matching_nodes = matching_color_nodes;
        } else {
            matching_nodes = matching_shape_nodes;
        }

        cy.nodes().unselect();

        for (var i = 0; i < matching_nodes.length; i++) {
            cy.$("#" + matching_nodes[i]).select();
        }
    }

    // Returns all the id's that are > k value
    function showOnlyK() {
        if ($("#input_k").val()) {
            if ($("#input_k").val().length > 0) {
                var maxVal = parseInt($("#input_k").val());

                window.cy.elements().show();
                hideList = window.cy.filter('[k > ' + maxVal + ']');
                hideList.hide();
            }
        }
    }

    //Gets all nodes and edges up do the max value set
    //and only renders them
    function applyMax(graph_layout) {
        var maxVal = parseInt($("#input_max").val());

        if (!maxVal) {
            return;
        }
        var newJSON = {
            "nodes": new Array(),
            "edges": new Array()
        };

        // List of node ids that should remain in the graph
        var nodeNames = Array();

        //Get all edges that meet the max quantifier
        for (var i = 0; i < graph_json.graph['edges'].length; i++) {
            var edge_data = graph_json.graph['edges'][i];
            if (edge_data['data']['k'] <= maxVal) {
                newJSON['edges'].push(edge_data);
                nodeNames.push(edge_data['data']['source']);
                nodeNames.push(edge_data['data']['target']);
            }
        }

        //Get all nodes that meet the max quantifier
        for (var i = 0; i < graph_json.graph['nodes'].length; i++) {
            var node_data = graph_json.graph['nodes'][i];
            if (nodeNames.indexOf(node_data['data']['id']) > -1) {
                newJSON['nodes'].push(node_data);
            }
        }

        window.cy.load(newJSON);
        showOnlyK();
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
            name: 'random',
            padding: 10,
            fit: true,
            animate: false,
            // maxSimulationTime: 1000
        };

        $("#auto").addClass('active');
        $("#manual").removeClass('active');

        $('#builtin').addClass('active');
        $('#custom').removeClass('active');

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
        } else if (query == 'default_cose') {
            graph_layout = {
                name: "cose"
            }
        } else if (query == "default_grid") {
            graph_layout = {
                name: "grid"
            }
        } else {

            $("#auto").removeClass('active');
            $("#manual").addClass('active');

            $('#builtin').removeClass('active');
            $('#custom').addClass('active');

            if (layout && layout.json != null) {
                graph_layout = {
                    name: 'preset',
                    positions: JSON.parse(layout.json)
                };
            } else if (query) {
                alert("Layout does not exist or has not been shared yet!");
                var loc = window.location.href;
                var baseLoc = loc.substring(0, loc.indexOf("?"));
                window.location.href = baseLoc;
            }
        }

        return graph_layout;
    }

    /*
     * Clears all search term from graph.
     */
    function clearSearchTerms() {
        window.cy.elements().removeCss();
        $("#search").val("");
        showOnlyK();
        // applyMax(graph_json);
        $("#testing1").html("");
    }

    /** 
     * Returns the HEX value of a color
     */
    function colourNameToHex(colour) {
        var colours = {
            "aliceblue": "#f0f8ff",
            "antiquewhite": "#faebd7",
            "aqua": "#00ffff",
            "aquamarine": "#7fffd4",
            "azure": "#f0ffff",
            "beige": "#f5f5dc",
            "bisque": "#ffe4c4",
            "black": "#000000",
            "blanchedalmond": "#ffebcd",
            "blue": "#0000ff",
            "blueviolet": "#8a2be2",
            "brown": "#a52a2a",
            "burlywood": "#deb887",
            "cadetblue": "#5f9ea0",
            "chartreuse": "#7fff00",
            "chocolate": "#d2691e",
            "coral": "#ff7f50",
            "cornflowerblue": "#6495ed",
            "cornsilk": "#fff8dc",
            "crimson": "#dc143c",
            "cyan": "#00ffff",
            "darkblue": "#00008b",
            "darkcyan": "#008b8b",
            "darkgoldenrod": "#b8860b",
            "darkgray": "#a9a9a9",
            "darkgreen": "#006400",
            "darkkhaki": "#bdb76b",
            "darkmagenta": "#8b008b",
            "darkolivegreen": "#556b2f",
            "darkorange": "#ff8c00",
            "darkorchid": "#9932cc",
            "darkred": "#8b0000",
            "darksalmon": "#e9967a",
            "darkseagreen": "#8fbc8f",
            "darkslateblue": "#483d8b",
            "darkslategray": "#2f4f4f",
            "darkturquoise": "#00ced1",
            "darkviolet": "#9400d3",
            "deeppink": "#ff1493",
            "deepskyblue": "#00bfff",
            "dimgray": "#696969",
            "dodgerblue": "#1e90ff",
            "firebrick": "#b22222",
            "floralwhite": "#fffaf0",
            "forestgreen": "#228b22",
            "fuchsia": "#ff00ff",
            "gainsboro": "#dcdcdc",
            "ghostwhite": "#f8f8ff",
            "gold": "#ffd700",
            "goldenrod": "#daa520",
            "gray": "#808080",
            "green": "#008000",
            "greenyellow": "#adff2f",
            "honeydew": "#f0fff0",
            "hotpink": "#ff69b4",
            "indianred ": "#cd5c5c",
            "indigo": "#4b0082",
            "ivory": "#fffff0",
            "khaki": "#f0e68c",
            "lavender": "#e6e6fa",
            "lavenderblush": "#fff0f5",
            "lawngreen": "#7cfc00",
            "lemonchiffon": "#fffacd",
            "lightblue": "#add8e6",
            "lightcoral": "#f08080",
            "lightcyan": "#e0ffff",
            "lightgoldenrodyellow": "#fafad2",
            "lightgrey": "#d3d3d3",
            "lightgreen": "#90ee90",
            "lightpink": "#ffb6c1",
            "lightsalmon": "#ffa07a",
            "lightseagreen": "#20b2aa",
            "lightskyblue": "#87cefa",
            "lightslategray": "#778899",
            "lightsteelblue": "#b0c4de",
            "lightyellow": "#ffffe0",
            "lime": "#00ff00",
            "limegreen": "#32cd32",
            "linen": "#faf0e6",
            "magenta": "#ff00ff",
            "maroon": "#800000",
            "mediumaquamarine": "#66cdaa",
            "mediumblue": "#0000cd",
            "mediumorchid": "#ba55d3",
            "mediumpurple": "#9370d8",
            "mediumseagreen": "#3cb371",
            "mediumslateblue": "#7b68ee",
            "mediumspringgreen": "#00fa9a",
            "mediumturquoise": "#48d1cc",
            "mediumvioletred": "#c71585",
            "midnightblue": "#191970",
            "mintcream": "#f5fffa",
            "mistyrose": "#ffe4e1",
            "moccasin": "#ffe4b5",
            "navajowhite": "#ffdead",
            "navy": "#000080",
            "oldlace": "#fdf5e6",
            "olive": "#808000",
            "olivedrab": "#6b8e23",
            "orange": "#ffa500",
            "orangered": "#ff4500",
            "orchid": "#da70d6",
            "palegoldenrod": "#eee8aa",
            "palegreen": "#98fb98",
            "paleturquoise": "#afeeee",
            "palevioletred": "#d87093",
            "papayawhip": "#ffefd5",
            "peachpuff": "#ffdab9",
            "peru": "#cd853f",
            "pink": "#ffc0cb",
            "plum": "#dda0dd",
            "powderblue": "#b0e0e6",
            "purple": "#800080",
            "red": "#ff0000",
            "rosybrown": "#bc8f8f",
            "royalblue": "#4169e1",
            "saddlebrown": "#8b4513",
            "salmon": "#fa8072",
            "sandybrown": "#f4a460",
            "seagreen": "#2e8b57",
            "seashell": "#fff5ee",
            "sienna": "#a0522d",
            "silver": "#c0c0c0",
            "skyblue": "#87ceeb",
            "slateblue": "#6a5acd",
            "slategray": "#708090",
            "snow": "#fffafa",
            "springgreen": "#00ff7f",
            "steelblue": "#4682b4",
            "tan": "#d2b48c",
            "teal": "#008080",
            "thistle": "#d8bfd8",
            "tomato": "#ff6347",
            "turquoise": "#40e0d0",
            "violet": "#ee82ee",
            "wheat": "#f5deb3",
            "white": "#ffffff",
            "whitesmoke": "#f5f5f5",
            "yellow": "#ffff00",
            "yellowgreen": "#9acd32"
        };

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

        var gid = $("#gid").text();

        if (gid.charAt(gid.length - 1) == '/') {
            gid = gid.substring(0, gid.length - 1);
        }

        var uid = $("#uid").text();

        $.post('../../../setDefaultLayout/', {
            'layoutOwner': $(this).attr("id"),
            'layoutId': $(this).val(),
            'gid': gid,
            'uid': uid
        }, function(data) {
            if (data.Error) {
                return alert(data.Error);
            }
            window.location.href = window.location.href.split('?')[0];
        });
    });

    /**
     * Makes specific layout the default layout for a graph.
     */
    $(".removeDefault").click(function(e) {
        var paths = document.URL.split('/')
        var gid = $("#gid").text();
        var uid = $("#uid").text();

        $.post('../../../removeDefaultLayout/', {
            'layoutOwner': $(this).attr("id"),
            'layoutId': $(this).val(),
            'gid': gid,
            'uid': uid
        }, function(data) {
            if (data.Error) {
                return alert(data.Error);
            }
            window.location.reload();
        });
    });

    $("#finished").click(function() {
        retrieveTaskCode();
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

            //VALUES CONSISTENT AS OF CYTOSCAPEJS 2.5.0
            //DONE TO SUPPORT OLD GRAPHS AND SETS A MINIMUM SETTINGS TO AT LEAST DISPLAY GRAPH IF USER
            //DOESN'T HAVE ANY OTHER SETTINGS TO ALTER HOW THE NODES IN GRAPH LOOKS
            var acceptedShapes = ["rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star", "diamond", "vee", "rhomboid", "polygon"];

            //If the node has a shape, make sure that shape is recognized by CytoscapeJS
            //Otherwise, make shape an ellipse
            if (nodeData.hasOwnProperty('shape') == true && acceptedShapes.indexOf(nodeData['shape'].toLowerCase()) == -1) {

                //TO SUPPORT OLD GRAPHS THAT HAD THESE SHAPES
                if (nodeData['shape'] == 'square') {
                    nodeData['shape'] = "rectangle"
                } else {
                    //Make default shape an ellipse
                    nodeData['shape'] = 'ellipse';
                }

                //If shape is not found, default to ellipse
                if (acceptedShapes.indexOf(nodeData["shape"]) == -1) {
                    nodeData["shape"] = "ellipse";
                }
            } else if (nodeData.hasOwnProperty('shape') == false) {
                nodeData['shape'] = "ellipse";
            } else {
                nodeData['shape'] = nodeData['shape'].toLowerCase();
            }

            //Pick default color if nothing is provided
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

            //Set border color to be black by default
            if (nodeData["border_color"] == undefined) {
                nodeData["border_color"] = "#888";
            }

            if (nodeData['text_halign'] == undefined) {
                nodeData["text_halign"] = "center";
            }

            if (nodeData["text_valign"] == undefined) {
                nodeData["text_valign"] = "center";
            }
        }
        return nodeJSON;
    };

    /*
     * When input_k bar is changed, update the nodes shown in the graph.
     */
    $("#input_k").bind("change", function() {
        setInputK();
    });

    /*
     * Updates the text box when the user slides the bar.
     */
    function setInputK() {
        if ($("#input_k").val() < 0) {
            $("#input_k").val(0);
        }
        if (parseInt($("#input_k").val()) > parseInt($("#input_max").val())) {
            $("#input_k").val($("#input_max").val());

        }
        setBarToValue($("#input_k"), "slider");
        $("#slider").slider({
            value: $("#input_k").val(),
            max: $('#input_max').val()
        });
    }

    /**
     * When the input max bar changes from user, invoke changes to the graph 
     * as well as position the slider in its appropriate value.
     */
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

    function grabNodePositions2() {
        //When save is clicked, it gets location of all the nodes and saves it
        //so that nodes can be placed in this location later on
        var nodes = window.cy.elements('node');
        var layout = [];
        for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
            var nodeData = {
                'x': nodes[i]._private.position.x,
                'y': nodes[i]._private.position.y,
                'id': nodes[i]._private.data.id,
                'background_color': nodes[i]._private['style']['background-color']['strValue'],
                'shape': nodes[i]._private['style']['shape']['strValue']
            };
            layout.push(nodeData);
        }
        return layout;
    };

    function grabNodePositions2Dictionary() {
        //When save is clicked, it gets location of all the nodes and saves it
        //so that nodes can be placed in this location later on
        var nodes = window.cy.elements('node');
        var layout = {};
        for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
            layout[nodes[i]._private.data.id] = {
                'x': nodes[i]._private.position.x,
                'y': nodes[i]._private.position.y,
                'background_color': nodes[i]._private['style']['background-color']['strValue'],
                'shape': nodes[i]._private['style']['shape']['strValue']           
            };
        }
        return layout;
    }

    /**
     * Launches task on Amazon Mechanical Turk.
     */
    $(".launch_task").click(function(e) {

        var graph_id = $(this).attr("id");
        var user_id = $(this).val();

        if (graph_id.length == 0 || user_id.length == 0) {
            return alert("Something went wrong.");
        }

        var layoutArray = [];
        for (var i = 0; i < 5; i++) {
            var layout = window.cy.makeLayout({
                name: "random"
            });
            layout.on('layoutstop', function() {
                console.log('done');
            });
            layout.run();

            layoutArray.push(grabNodePositions2());
        }

        $.post('../../../launchTask/', {
            'graph_id': $(this).attr("id"),
            'user_id': $(this).val(),
            'layout_array': JSON.stringify(layoutArray)
        }, function(data) {
            if (data.Error) {
                return alert(data.Error);
            } else {
                alert("Task launched!");
                window.location.reload();
            }
        });
    });

    /**
     * If the user enters a value greater than the max value allowed, change value of bar to max allowed value.
     * inputId the id of the input bar
     * barId  the id of the max paths shown bar.
     */
    function setBarToValue(inputId, barId) {
        var slider_max = $("#slider_max").slider("option", "max");
        if ($(inputId).val() > slider_max) {
            $(inputId).val(slider_max);
        }
        showOnlyK();
    }

    /**
     * Retrieves new task code. Called when task is completed.
     */
    function retrieveTaskCode() {

        var gid = $("#gid").text();
        var uid = $("#uid").text();

        if (gid.length == 0 || uid.length == 0) {
            return alert("Something is not right...");
        }

        //Save layout
        var current_layout = grabNodePositions2();
        var loggedIn = "MTURK_Worker";

        parsed_json = JSON.parse(layout.json);
        var changedLayout = grabNodePositions2Dictionary();

        var numChanges = 0;

        var numKeys = Object.keys(current_layout);

        for (var key in changedLayout) {

            new_node_obj = changedLayout[key];
            node_obj = parsed_json[key];

            if (node_obj != undefined && node_obj != undefined) {
                if (node_obj["x"] != new_node_obj["x"]) {
                    numChanges ++;
                }

                if (node_obj["y"] != new_node_obj["y"]) {
                    numChanges ++;
                }

                 if (node_obj["background_color"] != new_node_obj["background_color"]) {
                    numChanges ++;
                }

                 if (node_obj["shape"] != new_node_obj["shape"]) {
                    numChanges ++;
                }
            }

            
        }

        if (numChanges < 5) {
            $("#code").val("Not enough work done to complete task!");
            $("#codeModal").modal('toggle');
            $("#exit").text("Try again");
            $("#exit").click(function() {
                window.location.reload();
            });
            return;
        }

        var timeSpent = clock.stop();
        var events = logger.getEvents();

        console.log("Features are: NumChanges: " + numChanges + ", Time Spent: " + timeSpent + ", events: " + events.length);

        $.post("../../../retrieveTaskCode/", {
            "graph_id": gid,
            "user_id": uid,
            "layout_name": task_layout_name,
            "numChanges": numChanges,
            "timeSpent": timeSpent,
            "numEvents": events.length
        }, function(data) {
            if (data.hasOwnProperty("Message")) {
                $("#code").val(data.Message);
                $("#codeModal").modal('toggle');

                var queryString = location.href.split(location.host)[1].split("?")[0];
                //Posts information to the server regarding the current display of the graph,
                //including position
                $.post(queryString + "/layout/update/", {
                    layout_name: task_layout_name,
                    points: JSON.stringify(current_layout),
                    loggedIn: loggedIn,
                    "public": 0,
                    "unlisted": 0
                }, function(data) {
                    console.log(data);
                    if (data.Error) {
                        return alert(data.Error);
                    }
                });

                $("#exit").click(function() {
                    var pathArray = location.href.split('/');
                    var protocol = pathArray[0];
                    var host = pathArray[2];
                    var url = protocol + '//' + host;
                    window.location.href = url
                });
            } else {
                return alert(data.Error);
            }
        });
    };

    $("#tutorial_start").click(function() {
        clock.pause();
        $("#pause").find('span').toggleClass("glyphicon glyphicon-pause").toggleClass("glyphicon glyphicon-play");
        introJs().start();
    })

    // $("#reverse").click(function () {
    //     clock.reverse(retrieveTaskCode);
    // });

    // $("#pause").click(function() {
    //     if ($(this).find('span').attr('class') == "glyphicon glyphicon-pause") {
    //         clock.pause();
    //         $(this).find('span').toggleClass("glyphicon glyphicon-pause").toggleClass("glyphicon glyphicon-play");
    //     } else {
    //         clock.start(retrieveTaskCode);
    //         $(this).find('span').toggleClass("glyphicon glyphicon-play").toggleClass("glyphicon glyphicon-pause");
    //     }
    // });

    // $("#forward").click(function() {
    //     clock.forward(retrieveTaskCode);
    // });

    function applyLayoutStyles() {
        if (layout) {
            parsed_json = JSON.parse(layout.json);
            for (var i in parsed_json) {
                node_obj = parsed_json[i];

                if (node_obj.hasOwnProperty("background_color")) {
                    window.cy.$('[id="' + i + '"]').css('background-color', node_obj["background_color"]);
                }

                if (node_obj.hasOwnProperty("shape")) {
                    window.cy.$('[id="' + i + '"]').css('shape', node_obj["shape"]);
                }
            }
        }
    };

    $("#send_feedback").click(function() {
        var feedback = $("#feedback").val();

        var graph_id = $("#gid").text();
        var user_id = $("#uid").text();
        var layout_owner = "MTURK_Worker";

        $.post("../../../saveFeedback/", {
            "graph_id": graph_id,
            "user_id": user_id,
            "layout_owner": layout_owner,
            "layout_name": task_layout_name,
            "feedback": feedback
        }, function(data) {
            if (data.Error) {
                alert(data.Error);
            } else {
                console.log("Submitted feedback");
            }
        });
    });

    function getFeedback() {

        if (typeof task_layout_name !== 'undefined') {
            var graph_id = $("#gid").text();
            var user_id = $("#uid").text();
            var layout_owner = "MTURK_Worker";

            $.post("../../../getFeedback/", {
                "graph_id": graph_id,
                "user_id": user_id,
                "layout_owner": layout_owner,
                "layout_name": task_layout_name
            }, function(data) {
                if (data.Error) {
                    console.log(data.Error);
                } else {
                    for (var i = 0; i < data.Message.length; i++) {
                        $("#note_text").append("<p>" + (i + 1) + ": " + data.Message[i] + "</p>");
                    }
                }
            });
        }
    };
});