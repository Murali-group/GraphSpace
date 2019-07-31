/**
 * Created by jahan on 10/07/19.
 */

var compareGraphPage = {
    cyGraph: undefined,
    graph_ids: [],
    graphs_json: [],
    styles_json: [],
    common_nodes: undefined,
    edge_name_to_id: {},
    timeout: null,
    init: function () {
        /**
         * This function is called to setup the upload graph page.
         * It will initialize all the event listeners.
         */

        $('#nodes-li').hide();
        $('#edges-li').hide();
        $('#visualization-li').hide();
        compareGraphPage.loadGraphs();
        $('#graphVisualizationTabBtn').click(function (e) {
            window.setTimeout(function () {
                $('#cyGraphContainer').css('height', '99%');
            }, 100);
            compareGraphPage.cyGraph.fit().center();
        });
        $("#search-place-holder").on("keyup", function () {
            var value = $(this).val().toLowerCase();
            $(".dropdown-menu li").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
        $("#dropdownMenu1").on("focusin", function () {
            var value = "";
            $("#search-place-holder").val("");
            $(".dropdown-menu li").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
        $("#dropdownMenu2").on("focusin", function () {
            var value = "";
            $("#search-place-holder").val("");
            $(".dropdown-menu li").filter(function () {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
        });
        $('#colorpicker1').colorpicker();
        $('#colorpicker1').colorpicker().on('changeColor', function (event) {
            // $('#colorpicker1').css('background-color', event.color.toString());
            // $('#colorpicker1').val(event.color.toString());
            // if (compareGraphPage.cyGraph) {
            //     compareGraphPage.setNodesColor('graph_1', event.color.toString());
            //     compareGraphPage.setNodesColor('common_1', $('#operatorcolorpicker').val());
            // }
            compareGraphPage.colorPickerHelper($('#colorpicker1'), event, 'graph_1', $('#operatorcolorpicker'));
        });
        $('#colorpicker2').colorpicker();
        $('#colorpicker2').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker2'), event, 'graph_2', $('#operatorcolorpicker'));
        });
        $('#colorpicker3').colorpicker();
        $('#colorpicker3').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker3'), event, 'graph_1', $('#operatorcolorpicker1'));
        });
        $('#colorpicker4').colorpicker();
        $('#colorpicker4').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker4'), event, 'graph_2', $('#operatorcolorpicker1'));
        });
        $('#colorpicker5').colorpicker();
        $('#colorpicker5').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker5'), event, 'graph_3', $('#operatorcolorpicker1'));
        });
        $('#colorpicker6').colorpicker();
        $('#colorpicker6').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker6'), event, 'graph_4', $('#operatorcolorpicker1'));
        });
        $('#colorpicker7').colorpicker();
        $('#colorpicker7').colorpicker().on('changeColor', function (event) {
            compareGraphPage.colorPickerHelper($('#colorpicker7'), event, 'graph_5', $('#operatorcolorpicker1'));
        });

        $('#operatorcolorpicker').colorpicker();
        $('#operatorcolorpicker').colorpicker().on('changeColor', function (event) {
            $('#operatorcolorpicker').css('background-color', event.color.toString());
            $('#operatorcolorpicker').val(event.color.toString());
            compareGraphPage.setNodesColor('common_1', event.color.toString());
        });
        $('#operatorcolorpicker1').colorpicker();
        $('#operatorcolorpicker1').colorpicker().on('changeColor', function (event) {
            $('#operatorcolorpicker1').css('background-color', event.color.toString());
            $('#operatorcolorpicker1').val(event.color.toString());
            compareGraphPage.setNodesColor('common_1', event.color.toString());
        });
        if (graph_1_id && graph_2_id && operation) {
            $('#dropdownMenu1').attr('value', graph_1_id);
            $('#dropdownMenu2').attr('value', graph_2_id);
            $('#operatorMenu1').attr('value', operation);
            $('#operatorMenu1').parent().find('a[row_id="' + operation + '"]').click();
        }

    },
    colorPickerHelper: function (obj, event, graph_id, common) {
        /**
         * This function is called to whenever a color is selected
         * using the color picker.
         */
        obj.css('background-color', event.color.toString());
        obj.val(event.color.toString());
        if (compareGraphPage.cyGraph) {
            compareGraphPage.setNodesColor(graph_id, event.color.toString());
            compareGraphPage.setNodesColor('common_1', common.val());
        }
    },
    validateExpression: function (infix) {
        var balance = 0;
        // remove white spaces to simplify regex
        infix = infix.replace(/ /g, '');
        var regex = /[\+\-]?\w+(([\+\-\*\/\&\|\!]|(\<\=?|\>\=?|\=\=|\!=))[\+\-]?\w+)*/;

        // if it has empty parenthesis then is not valid
        if (infix.match(/\(\)/)) {
            return false;
        }

        // validate parenthesis balance
        for (var i = 0; i < infix.length; i++) {
            if (infix[i] == '(') {
                balance++;
            } else if (infix[i] == ')') {
                balance--;
            }

            if (balance < 0) {
                return false;
            }
        }

        if (balance > 0) {
            return false;
        }

        // remove all the parenthesis
        infix = infix.replace(/[\(\)]/g, '');

        return infix.match(regex)[0] == infix;
    },
    loadGraphs: function () {
        /**
         * This function is called when compare graph page is loaded.
         * It sends ajax request to fetch My graphs, Shared Graphs and Public graphs.
         */
        var params = {'data': {'sort': 'updated_at', 'order': 'desc', 'offset': 0, 'limit': 10}};
        query = '';
        params.data["owner_email"] = $('#UserEmail').val();

        apis.graphs.search(params.data, query,
            successCallback = function (response) {
                // This method is called when graphs are successfully fetched.
                compareGraphPage.populateCompareDropdownMenu(response['graphs']);
            },
            errorCallback = function () {
                // This method is called when error occurs while fetching graphs.
                params.error('Error');
            }
        );
        delete params.data.owner_email;
        params.data["member_email"] = $('#UserEmail').val();

        apis.graphs.search(params.data, query,
            successCallback = function (response) {
                // This method is called when graphs are successfully fetched.
                compareGraphPage.populateCompareDropdownMenu(response['graphs']);
            },
            errorCallback = function () {
                // This method is called when error occurs while fetching graphs.
                params.error('Error');
            }
        );
        delete params.data.member_email;

        params.data["is_public"] = 1;
        apis.graphs.search(params.data, query,
            successCallback = function (response) {
                // This method is called when graphs are successfully fetched.
                compareGraphPage.populateCompareDropdownMenu(response['graphs']);
            },
            errorCallback = function () {
                // This method is called when error occurs while fetching graphs.
                params.error('Error');
            }
        );
    },
    setDropdownMenu: function (obj) {
        /**
         * This helper function changes the header values of dropdown menu to
         * correspond to the selected value.
         * It called in populateCompareDropdownMenu().
         */
        var label = obj.parent().parent().siblings('button').children('i');
        if (label.text()) {
            label.text(label.attr('value'));
            obj.parent().parent().siblings('button').children('bold').text(obj.attr('data'));
        } else {
            obj.parent().parent().siblings("button[class*='dropdown-toggle']").text(obj.attr('data'));
            obj.parent().parent().siblings("button[class*='dropdown-toggle']").append('<span class="caret"></span>');

            if (obj.parent().parent().siblings("button[class*='dropdown-toggle']")[0].id == 'operatorMenu1') {
                compareGraphPage.compareGraphs();
            } else compareGraphPage.compareGraphsMultiple();
        }
        obj.parent().parent().siblings("button[class*='dropdown-toggle']").attr("value", obj.attr('row_id'));
    },
    populateCompareDropdownMenu: function (data) {
        /**
         * This helper function populates the dropdown menu with graphs available to user.
         * It is called in loadGraphs() when compare graph page is loaded.
         */
        $.each(data, function (i, item) {
            if ($('#UserEmail').val() == item.owner_email && $(".compare-dropdown[mygraphs='false']").length) {
                $(".compare-dropdown").append('<li class="dropdown-header">My Graphs </li>');
                $(".compare-dropdown").attr('mygraphs', 'true');
            } else if (item.owner_email.startsWith("public") && $(".compare-dropdown[publicgraphs='false']").length) {
                $(".compare-dropdown").append('<li role="separator" class="divider"></li>');
                $(".compare-dropdown").append('<li class="dropdown-header">Public Graphs </li>');
                $(".compare-dropdown").attr('publicgraphs', 'true');
            } else if ($('#UserEmail').val() != item.owner_email && !item.owner_email.startsWith("public") && $(".compare-dropdown[sharedgraphs='false']").length) {
                $(".compare-dropdown").append('<li role="separator" class="divider"></li>');
                $(".compare-dropdown").append('<li class="dropdown-header">Shared Graphs </li>');
                $(".compare-dropdown").attr('sharedgraphs', 'true');
            }
            $(".compare-dropdown").append('<li><a row_id="' + item.id + '" data="'
                + item.name + '" onclick="compareGraphPage.setDropdownMenu($(this));">'
                + item.name + '</a></li>')
        });
    },
    setNodesColor: function (graph_parent, color) {
        /**
         * Params
         * graph_parent :  identifies the group of nodes
         * color :  color for the group of nodes
         *
         * This function color a group of nodes according to the graph_parent id.
         * It is called when comparison is executed and whenever user changes node
         * color dynamically using the colorpickers.
         */
        compareGraphPage.cyGraph.filter(":parent[id='" + graph_parent + "']").style({
            'background-color': color,
            'background-opacity': 0,
            'border-opacity': 0,
            'border-color': color,
        });
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").style({
            'background-color': color,
            'border-color': color
        });
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").connectedEdges().style({'line-color': color});
        compareGraphPage.cyGraph.filter("node[id='graph_1']").style({'background-opacity': 0, 'font-size': '1px'});
        compareGraphPage.cyGraph.filter("node[id='graph_2']").style({'background-opacity': 0, 'font-size': '1px'});
        compareGraphPage.cyGraph.filter("node[id='common_1']").style({'background-opacity': 0, 'font-size': '1px'});
    },
    setNodesColorMultiple: function (graph_parent, color) {
        /**
         * Params
         * graph_parent :  identifies the group of nodes
         * color :  color for the group of nodes
         *
         * This function color a group of nodes according to the graph_parent id.
         * It is called when comparison is executed and whenever user changes node
         * color dynamically using the colorpickers.
         */
        compareGraphPage.cyGraph.filter(":parent[id='" + graph_parent + "']").style({
            'background-color': color,
            'background-opacity': 0,
            'border-opacity': 0,
            'border-color': color,
        });
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").style({
            'background-color': color,
            'border-color': color
        });
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").connectedEdges().style({'line-color': color});

        for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {
            compareGraphPage.cyGraph.filter("node[id='graph_'" + (i + 1) + "]").style({
                'background-opacity': 0,
                'font-size': '1px'
            });
        }
        compareGraphPage.cyGraph.filter("node[id='common_1']").style({'background-opacity': 0, 'font-size': '1px'});
    },
    setGraph0Groups: function (graph_json, common_nodes) {
        /**
         * Not used anymore. For historical compatibility and reference.
         * Will be removed in final draft
         */
        const len = graph_json['elements']['nodes'].length;
        var common_id = undefined;
        graph_json['elements']['nodes'][len] = {
            'data': {
                'id': 'graph_1',
                'label': 'Graph 1',
                'name': 'Graph 1'
            }
        };
        graph_json['elements']['nodes'][len + 1] = {'data': {'id': 'common_1', 'label': 'Common', 'name': 'Common'}};
        _.each(graph_json['elements']['nodes'], function (item) {
            if (item['data']['id'] != graph_json['elements']['nodes'][len]['data']['id'])
                item['data']['parent'] = graph_json['elements']['nodes'][len]['data']['id'];
            _.each(common_nodes, function (innerNode) {
                if (innerNode.length)
                    innerNode = (innerNode[0]['graph_id'] == compareGraphPage.graph_1_id) ? innerNode[0] : innerNode[1];
                if (item['data']['label'] == innerNode['label']) {
                    if (!common_id) {
                        common_id = item['data']['id'];
                        compareGraphPage.common_nodes['parent1'] = common_id;
                    }
                    item['data']['parent'] = 'common_1';
                }
            });
        });
    },
    setGraphGroups: function (graph_json, common_nodes, graph_id) {
        /**
         * Params
         * graph_json :  nodes & edges datastructure
         * common_nodes :  nodes indentified by the comparison function
         * graph_id :   identity of graph
         *
         * This function assigns a group to elements of a graph based on its ID.
         * This is required later to identify which graph  nodes/edges belong to
         * (as Cytoscape.js only supports 1 instance per canvas - all graphs needs
         * to be merged into a single graph grouping helps in identifying elements
         * of individual graphs).
         * Also, removes duplicate entries for common_nodes from the merged graph.
         *
         * It is called in compareGraphHelper() during comparison operation.
         */
        const len = graph_json['elements']['nodes'].length;
        var common_id = undefined;
        var duplicate_nodes = [];
        graph_json['elements']['nodes'][len] = {
            'data': {
                'id': 'graph_' + (graph_id + 1),
                'label': 'Graph ' + (graph_id + 1),
                'name': 'Graph ' + (graph_id + 1)
            }
        };
        _.each(graph_json['elements']['nodes'], function (item) {
            if (item['data']['id'] != graph_json['elements']['nodes'][len]['data']['id'])
                item['data']['parent'] = graph_json['elements']['nodes'][len]['data']['id'];
            _.each(common_nodes, function (innerNode) {
                if (innerNode.length)
                    innerNode = (innerNode[0]['graph_id'] == compareGraphPage.graph_ids[graph_id]) ? innerNode[0] : innerNode[1];
                if (item['data']['label'] == innerNode['label']) {
                    if (compareGraphPage.graph_ids[graph_id] != compareGraphPage.graph_ids[0])
                        duplicate_nodes.push(item);
                    if (compareGraphPage.graph_ids[graph_id] == compareGraphPage.graph_ids[0]) {
                        if (!common_id) {
                            common_id = item['data']['id'];
                            compareGraphPage.common_nodes['parent1'] = common_id;
                        }
                        item['data']['parent'] = 'common_1';
                    }
                }
            });
        });
        // if (compareGraphPage.graph_ids[graph_id] != compareGraphPage.graph_ids[0]) {
        _.each(duplicate_nodes, function (node) {
            graph_json['elements']['nodes'].splice(graph_json['elements']['nodes'].indexOf(node), 1);
        });
        // }
        graph_json['elements']['nodes'][len - duplicate_nodes.length]['data']['parent'] = 'graph_2';
    },
    setGraphGroupsMultiple: function (graph_json, common_nodes, graph_id) {
        /**
         * Params
         * graph_json :  nodes & edges datastructure
         * common_nodes :  nodes indentified by the comparison function
         * graph_id :   identity of graph
         *
         * This function assigns a group to elements of a graph based on its ID.
         * This is required later to identify which graph  nodes/edges belong to
         * (as Cytoscape.js only supports 1 instance per canvas - all graphs needs
         * to be merged into a single graph grouping helps in identifying elements
         * of individual graphs).
         * Also, removes duplicate entries for common_nodes from the merged graph.
         *
         * It is called in compareGraphHelperMultiple() during comparison operation.
         */
        const len = graph_json['elements']['nodes'].length;
        var common_id = undefined;
        var duplicate_nodes = [];
        graph_json['elements']['nodes'][len] = {
            'data': {
                'id': 'graph_' + (graph_id + 1),
                'label': 'Graph ' + (graph_id + 1),
                'name': 'Graph ' + (graph_id + 1)
            }
        };
        _.each(graph_json['elements']['nodes'], function (item) {
            if (item['data']['id'] != graph_json['elements']['nodes'][len]['data']['id'])
                item['data']['parent'] = graph_json['elements']['nodes'][len]['data']['id'];
            _.each(common_nodes, function (innerNode) {
                if (item['data']['name'] == innerNode['name']) {
                    if (compareGraphPage.graph_ids[graph_id] != compareGraphPage.graph_ids[0])
                        duplicate_nodes.push(item);
                    if (compareGraphPage.graph_ids[graph_id] == compareGraphPage.graph_ids[0]) {
                        if (!common_id) {
                            common_id = item['data']['id'];
                            compareGraphPage.common_nodes['parent1'] = common_id;
                        }
                        item['data']['parent'] = 'common_1';
                    }
                }
            });
        });
        // if (compareGraphPage.graph_ids[graph_id] != compareGraphPage.graph_ids[0]) {
        _.each(duplicate_nodes, function (node) {
            graph_json['elements']['nodes'].splice(graph_json['elements']['nodes'].indexOf(node), 1);
        });
        // }
        graph_json['elements']['nodes'][len - duplicate_nodes.length]['data']['parent'] = 'graph_2';
    },
    compareGraphsMultiple: function () {
        /**
         * This function is called when the user initiates graph comparison.
         * Sends AJAX requests to load all the graphs selected by the user,
         * it then calls compareGraphHelperMultiple().
         *
         * Returns error whenever AJAX requests fail.
         */
        let graph_ids = []
        let count = 0;
        for (let i = 0; i < 5; i++) {
            if ($('#dropdownMenu' + (i + 3)).attr('value'))
                graph_ids[i] = compareGraphPage.graph_ids[i] = $('#dropdownMenu' + (i + 3)).attr('value');
            if (graph_ids[i])
                count++;
        }
        operation = $('#operatorMenu2').attr('value');
        for (let i = 0; i < count; i++) {
            apis.graphs.getByID(graph_ids[i],
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    compareGraphPage.graphs_json[i] = response['graph_json'];
                    compareGraphPage.styles_json[i] = response['style_json'];
                    $('#dropdownMenu' + (i + 3)).parent().find('a[row_id="' + graph_ids[i] + '"]').click();
                    if (count == 1) {
                        console.log('All Graphs Loaded!');
                        compareGraphPage.compareGraphHelperMultiple();
                    }
                    count--;
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    params.error('Error');
                }
            );
        }
    },
    compareGraphs: function () {
        /**
         * This function is called when the user initiates graph comparison.
         * Sends AJAX requests to load all the graphs selected by the user,
         * it then calls compareGraphHelpe().
         *
         * Returns error whenever AJAX requests fail.
         */
        graph_1_id = compareGraphPage.graph_ids[0] = $('#dropdownMenu1').attr('value');
        graph_2_id = compareGraphPage.graph_ids[1] = $('#dropdownMenu2').attr('value');

        operation = $('#operatorMenu1').attr('value');
        apis.graphs.getByID(compareGraphPage.graph_ids[0],
            successCallback = function (response) {
                // This method is called when graphs are successfully fetched.
                compareGraphPage.graphs_json[0] = response['graph_json'];
                compareGraphPage.styles_json[0] = response['style_json'];
                apis.graphs.getByID(compareGraphPage.graph_ids[1],
                    successCallback = function (response) {
                        // This method is called when graphs are successfully fetched.
                        compareGraphPage.graphs_json[1] = response['graph_json'];
                        compareGraphPage.styles_json[1] = response['style_json'];
                        compareGraphPage.compareGraphHelper();
                        $('#dropdownMenu1').parent().find('a[row_id="' + graph_1_id + '"]').click();
                        $('#dropdownMenu2').parent().find('a[row_id="' + graph_2_id + '"]').click();
                    },
                    errorCallback = function () {
                        // This method is called when error occurs while fetching graphs.
                        params.error('Error');
                    }
                );
            },
            errorCallback = function () {
                // This method is called when error occurs while fetching graphs.
                params.error('Error');
            }
        );
    },
    formatCyGraph: function () {
        /**
         * May be needed for future changes.
         * Does graph formatting!
         */
        compareGraphPage.cyGraph.filter(":parent").style({
            'font-size': '0px',
        });
        /*compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").layout({
            'name': 'cola',
            'animate': false,
            'padding': 10
        }).run();
        compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").layout({
            'name': 'cola',
            'animate': false,
            'padding': 10
        }).run();

        compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").layout({
            'name': 'cola',
            'animate': false,
            'padding': 10
        }).run();*/

        let x_max = compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").max(function (ele, i, eles) {
            return ele.position()['x'];
        });
        let y_max = compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").max(function (ele, i, eles) {
            return ele.position()['y'];
        });
        y_max = Math.max(y_max.value, compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").max(function (ele, i, eles) {
            return ele.position()['y'];
        }).value);

        let cm_len_1 = compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").max(function (ele, i, eles) {
            return ele.position()['x'];
        }).value - compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").min(function (ele, i, eles) {
            return ele.position()['x'];
        }).value;

        compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").layout({
            'name': 'cola', 'padding': 10, transform: (node) => {
                let position = {};
                position.x = node.position('x') + x_max.value + 300;
                position.y = node.position('y');
                return position;
            }
        }).run();

        compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").layout({
            'name': 'cola', 'padding': 10, transform: (node) => {
                let position = {};
                position.x = node.position('x') + Math.abs(cm_len_1 / 2 - x_max.value) + 300;
                position.y = node.position('y') + y_max + 550;
                return position;
            }
        }).run();
    },
    setCommonElements: function (nodes) {
        $.each(nodes, function (i, node) {
            if (node.length > 1) {
                let id_1 = compareGraphPage.cyGraph.nodes("[label = '" + node[0]['label'] + "']").id();
                let id_2 = compareGraphPage.cyGraph.nodes("[label = '" + node[1]['label'] + "']").id();

                edges = compareGraphPage.cyGraph.nodes("[id = '" + id_1 + "']").connectedEdges();
                $.each(edges, function (i, edge) {
                    if (edge.data('source') == id_1) {
                        edge.move({source: id_2});
                    } else
                        edge.move({target: id_2});
                });
                compareGraphPage.cyGraph.remove("node[id = '" + id_1 + "']");
            }
        });

    },
    compareGraphHelperMultiple: function () {
        /**
         * This function is called in compareGraphMultiple().
         * Sends AJAX request to execute Comparison functionality in backend.
         * The AJAX request returns a list of nodes and edges identified by the comparison operation.
         * Additionally, this function populates the Nodes and Edges table.
         */
        let data = {};
        for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {
            data['graph_id_' + (i + 1)] = compareGraphPage.graph_ids[i];
        }
        operation = $('#operatorMenu2').attr('value');
        data['operation'] = operation;
        data['multiple'] = true;
        apis.compare.get(data,
            successCallback = function (response) {
                console.log('Success');
                compareGraphPage.common_nodes = response['nodes'];
                for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {
                    compareGraphPage.setGraphGroupsMultiple(compareGraphPage.graphs_json[i], response['nodes'], i);
                    if (i > 0) {
                        compareGraphPage.graphs_json[0]['elements']['nodes'] =
                            compareGraphPage.graphs_json[0]['elements']['nodes']
                                .concat(compareGraphPage.graphs_json[i]['elements']['nodes']);
                        compareGraphPage.graphs_json[0]['elements']['edges'] =
                            compareGraphPage.graphs_json[0]['elements']['edges']
                                .concat(compareGraphPage.graphs_json[i]['elements']['edges']);
                    }

                }

                compareGraphPage.cyGraph = compareGraphPage.constructCytoscapeGraph(compareGraphPage.graphs_json[0], compareGraphPage.styles_json[0]);
                for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {
                    compareGraphPage.setNodesColor('graph_' + (i + 1), $('#colorpicker' + (i + 3)).val());
                }

                compareGraphPage.cyGraph.once('render', function () {  // Wait for cytoscape to actually load and map eles
                    compareGraphPage.cyGraph.panzoom();
                    window.setTimeout(function () {
                        compareGraphPage.cyGraph.reset().fit().center();
                        $('#cyGraphContainer').css('height', '99%');
                        $('#visualization-li a:last').tab('show');
                        $('#visualization-li a:first').tab('show');
                    }, 100);
                });

                compareGraphPage.populateNodeDataMulti(response['nodes']);
                compareGraphPage.populateEdgeData(response['edges']);

                $('#nodes-total-badge').text(response['nodes'].length);
                $('#edges-total-badge').text(response['edges'].length);
                compareGraphPage.tabHelper();

            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                $.notify({message: "You are not authorized to access one or more graphs selected for comparison."}, {type: 'danger'});
            });
    },
    tabHelper: function () {
        /**
         * Helper function to unhide information tabs in compare graph page.
         * Additionally, initialize node and edge table as DataTable.
         */
        $('#nodes-table').DataTable().draw();
        $('#edges-table').DataTable().draw();
        $('.dataTables_length').addClass('bs-select');

        $('#nodes-li').show();
        $('#visualization-li').show();
        $('#edges-li').show();
        $('#visualization-li a:last').tab('show');
        $('#visualization-li a:first').tab('show');
    },
    compareGraphHelper: function () {
        /**
         * This function is called in compareGraph().
         * Sends AJAX request to execute Comparison functionality in backend.
         * The AJAX request returns a list of nodes and edges identified by the comparison operation.
         * Additionally, this function populates the Nodes and Edges table.
         */
        operation = $('#operatorMenu1').attr('value');
        if (operation && compareGraphPage.graph_ids[0] && compareGraphPage.graph_ids[1]) {
            $('#nodes-table > thead').find("th").remove();
            $('#edges-table > thead').find("th").remove();
            $('#nodes-table > thead > tr').append('<th><h4 style="text-align:center">Graph 1</h4></th>');
            $('#nodes-table > thead > tr').append('<th><h4 style="text-align:center">Graph 2</h4></th>');

            $('#edges-table > thead > tr').append('<th><h4 style="text-align:center">Graph 1</h4></th>');
            $('#edges-table > thead > tr').append('<th><h4 style="text-align:center">Graph 2</h4></th>');

            apis.compare.get({
                    'graph_1_id': compareGraphPage.graph_ids[0],
                    'graph_2_id': compareGraphPage.graph_ids[1],
                    'operation': operation
                },
                successCallback = function (response) {
                    // $('#nodes-table').DataTable();
                    compareGraphPage.common_nodes = response['nodes'];

                    compareGraphPage.setGraphGroups(compareGraphPage.graphs_json[0], response['nodes'], 0);
                    compareGraphPage.setGraphGroups(compareGraphPage.graphs_json[1], response['nodes'], 1);
                    compareGraphPage.graphs_json[0]['elements']['nodes'] = compareGraphPage.graphs_json[0]['elements']['nodes'].concat(compareGraphPage.graphs_json[1]['elements']['nodes']);
                    compareGraphPage.graphs_json[0]['elements']['edges'] = compareGraphPage.graphs_json[0]['elements']['edges'].concat(compareGraphPage.graphs_json[1]['elements']['edges']);
                    compareGraphPage.styles_json[0]['style'] = compareGraphPage.styles_json[0]['style'].concat(compareGraphPage.styles_json[1]['style']);

                    compareGraphPage.cyGraph = compareGraphPage.constructCytoscapeGraph(compareGraphPage.graphs_json[0], compareGraphPage.styles_json[0]);

                    compareGraphPage.populateNodeData(response['nodes']);
                    compareGraphPage.populateEdgeData(response['edges']);
                    // compareGraphPage.setCommonElements(response['nodes']);
                    compareGraphPage.cyGraph.ready(function () {                 // Wait for cytoscape to actually load and map eles
                        // compareGraphPage.formatCyGraph();
                        compareGraphPage.cyGraph.panzoom();
                        window.setTimeout(function () {
                            $('#cyGraphContainer').css('height', '99%');
                            $('#visualization-li a:last').tab('show');
                            $('#visualization-li a:first').tab('show');
                        }, 100);
                    });

                    compareGraphPage.cyGraph.once('render', function () {                 // Wait for cytoscape to actually load and map eles
                        window.setTimeout(function () {
                            compareGraphPage.cyGraph.reset().fit().center();
                            $('#cyGraphContainer').css('height', '99%');
                            $('#visualization-li a:last').tab('show');
                            $('#visualization-li a:first').tab('show');
                        }, 100);
                    });

                    $('#nodes-total-badge').text(response['nodes'].length);
                    $('#edges-total-badge').text(response['edges'].length);

                    compareGraphPage.setNodesColor('graph_1', $('#colorpicker1').val());
                    compareGraphPage.setNodesColor('graph_2', $('#colorpicker2').val());
                    compareGraphPage.setNodesColor('common_1', $('#operatorcolorpicker').val());
                    compareGraphPage.tabHelper();
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group_to_graph relationship.
                    $.notify({message: "You are not authorized to access one or more graphs selected for comparison."}, {type: 'danger'});
                });
        } else {
            $.notify({message: "Please select correct parameters for Graph comparison."}, {type: 'danger'});
        }
    },
    resetData: function () {
        /**
         * Hard reset compare page.
         */
        location.replace("/compare");

    },
    populateNodeDataMulti: function (nodes) {
        /**
         * This function sets up the headers and body of the nodes table.
         * This setup needs to be done dynamically as table columns are variable
         * depending on the number of graphs selected for comparison operation.
         * It is called in compareGraphHelperMulti() during graphs comparison.
         */
        $('#nodes-table > thead').find("th").remove();
        $('#edges-table > thead').find("th").remove();
        for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {
            $('#nodes-table > thead > tr').append('<th><h4 style="text-align:center">Graph' + (i + 1) + '</h4></th>');
            $('#edges-table > thead > tr').append('<th><h4 style="text-align:center">Graph' + (i + 1) + '</h4></th>');
        }

        var trHTML = '';
        var cyNode = undefined;
        $('#nodes-table').DataTable().clear().destroy();
        $('#nodes-comparison-table').find("tr:gt(0)").remove();
        if (nodes.length && !nodes[0].length) {
            $('#nodes-table > thead').find("th:gt(0)").remove();
            $('#nodes-table').parent().attr('align', 'center');
            $('#nodes-table').attr('style', 'width:800px;');

        } else $('#nodes-table').attr('style', '');
        $.each(nodes, function (i, item) {
            if (item.length) {
                // Use 'name' field instead - for testing use 'label'
                cyNode = compareGraphPage.cyGraph.nodes("[label = '" + item['label'] + "']");
                for (let i = 0; i < compareGraphPage.graph_ids.length; i++) {

                    trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item['name']
                        + '<br> <b class="compare-table-td"> Label : </b>' + item['label'];
                    if (cyNode.length && cyNode.data() && cyNode.data()['popup']) {
                        trHTML += '<br>' + cyNode1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                    }

                    trHTML += '</td><td> <b class="compare-table-td">Name : </b>' + item[1]['name']
                        + '<br> <b class="compare-table-td"> Label : </b>' + item[1]['label'];

                    if (cyNode2.length && cyNode2.data() && cyNode2.data()['popup']) {
                        trHTML += '<br>' + cyNode2.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                    }
                    trHTML += '</td></tr>';
                }

            } else {
                // Use 'name' field instead - for testing use 'label'
                cyNode1 = compareGraphPage.cyGraph.getElementById(item['label']);

                trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item['label'];

                if (cyNode1.length && cyNode1.data() && cyNode1.data()['popup']) {
                    trHTML += '<br>' + cyNode1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }
                trHTML += '</td></tr>';
            }

        });
        $('#nodes-comparison-table').append(trHTML);
    },
    populateNodeData: function (nodes) {
        /**
         * This function sets up the headers and body of the nodes table.
         * This setup needs to be done dynamically as table columns are variable
         * depending on the number of graphs selected for comparison operation.
         * It is called in compareGraphHelperMulti() during graphs comparison.
         */
        var trHTML = '';
        var cyNode1 = undefined;
        var cyNode2 = undefined;
        $('#nodes-table').DataTable().clear().destroy();
        $('#nodes-comparison-table').find("tr:gt(0)").remove();
        if (nodes.length && !nodes[0].length) {
            $('#nodes-table > thead').find("th:gt(0)").remove();
            $('#nodes-table').parent().attr('align', 'center');
            $('#nodes-table').attr('style', 'width:800px;');

        } else $('#nodes-table').attr('style', '');
        $.each(nodes, function (i, item) {
            if (item.length) {
                // Use 'name' field instead - for testing use 'label'
                cyNode1 = compareGraphPage.cyGraph.nodes("[label = '" + item[0]['label'] + "']");
                cyNode2 = compareGraphPage.cyGraph.nodes("[label = '" + item[1]['label'] + "']");

                trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item[0]['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item[0]['label'];
                if (cyNode1.length && cyNode1.data() && cyNode1.data()['popup']) {
                    trHTML += '<br>' + cyNode1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }

                trHTML += '</td><td> <b class="compare-table-td">Name : </b>' + item[1]['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item[1]['label'];

                if (cyNode2.length && cyNode2.data() && cyNode2.data()['popup']) {
                    trHTML += '<br>' + cyNode2.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }
                trHTML += '</td></tr>';

            } else {
                // Use 'name' field instead - for testing use 'label'
                cyNode1 = compareGraphPage.cyGraph.getElementById(item['label']);

                trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item['label'];

                if (cyNode1.length && cyNode1.data() && cyNode1.data()['popup']) {
                    trHTML += '<br>' + cyNode1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }
                trHTML += '</td></tr>';
            }

        });
        $('#nodes-comparison-table').append(trHTML);
    },
    populateEdgeData: function (edges) {
        /**
         * This function sets up the headers and body of the edges table.
         * This setup needs to be done dynamically as table columns are variable
         * depending on the number of graphs selected for comparison operation.
         * It is called in compareGraphHelperMulti() during graphs comparison.
         */
        var trHTML = '';
        var cyEdge1 = undefined;
        var cyEdge2 = undefined;
        $('#edges-table').DataTable().clear().destroy();
        $('#edges-comparison-table').find("tr:gt(0)").remove();
        if (edges.length && !edges[0].length) {
            $('#edges-table > thead').find("th:gt(0)").remove();
            $('#edges-table').parent().attr('align', 'center');
            $('#edges-table').attr('style', 'width:800px;');
        } else $('#edges-table').attr('style', '');
        $.each(edges, function (i, item) {

            if (item.length) {
                cyEdge1 = compareGraphPage.cyGraph.getElementById(compareGraphPage.edge_name_to_id[item[0]['name']]);
                cyEdge2 = compareGraphPage.cyGraph.getElementById(compareGraphPage.edge_name_to_id[item[1]['name']]);

                trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item[0]['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item[0]['label'];

                if (cyEdge1.length && cyEdge1.data() && cyEdge1.data()['popup']) {
                    trHTML += '<br>' + cyEdge1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }

                trHTML += '</td><td> <b class="compare-table-td">Name : </b>' + item[1]['name']
                    + '<br> <b class="compare-table-td"> Label : </b>' + item[1]['label'];

                if (cyEdge2.length && cyEdge2.data() && cyEdge2.data()['popup']) {
                    trHTML += '<br>' + cyEdge2.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }

                trHTML += '</td></tr>';

            } else {
                cyEdge1 = compareGraphPage.cyGraph.getElementById(compareGraphPage.edge_name_to_id[item['name']]);

                trHTML += '<tr><td><b class="compare-table-td" >Name : </b>' + item['name'];

                if (cyEdge1.length && cyEdge1.data() && cyEdge1.data()['popup']) {
                    trHTML += '<br>' + cyEdge1.data()['popup'].replace(/<\s*hr\s*\/>/gi, '');
                }
                trHTML += '</td></tr>';
            }
        });
        $('#edges-comparison-table').append(trHTML);
    },
    constructCytoscapeGraph: function (graph_json, style_json) {
        /**
         * Sets up a Cytoscape instance to represent the graph.
         * It is called in compareGraphHelper() and compareGraphHelperMultiple().
         * Additionally, translates nodes/edges to for better visualization.
         * It uses the Cola layout for rendering the graphs.
         */
        layout = {
            name: 'cola',
        };
        let y_max = 0;
        let y_min = Infinity;
        let x_max = 0;
        let c_max = 0;
        let c_min = Infinity;
        graph_json['elements']['nodes'] = _.map(graph_json['elements']['nodes'], function (node) {
            var newNode = {
                "data": node['data']
            };
            if ('position' in node) {
                newNode['position'] = node['position'];
                if (node['data']['parent'] == 'graph_1') {
                    x_max = (x_max > node['position']['x']) ? x_max : node['position']['x'];
                }
                if (node['data']['parent'] == 'common_1') {
                    c_max = (c_max > node['position']['x']) ? c_max : node['position']['x'];
                    c_min = (c_min < node['position']['x']) ? c_min : node['position']['x'];
                }
                y_max = (y_max > node['position']['y']) ? y_max : node['position']['y'];
                y_min = (y_min < node['position']['y']) ? y_min : node['position']['y'];
                /*layout = {
                    name: 'preset'
                };*/
            }

            return newNode
        });

        _.map(graph_json['elements']['nodes'], function (node) {
            if ('position' in node) {

                if (node['data']['parent'] == 'graph_2') {
                    node['position']['x'] = node['position']['x'] + x_max + 100;
                }
                if (node['data']['parent'] == 'common_1') {
                    node['position']['x'] = node['position']['x'] + Math.abs((c_max - c_min) / 2 - x_max) + 100;
                    node['position']['y'] = node['position']['y'] + y_max + 50;
                }
            }
        });


        graph_json['elements']['edges'] = _.map(graph_json['elements']['edges'], function (edge) {
            compareGraphPage.edge_name_to_id[edge['data']['name']] = edge['data']['id'];
            return {
                "data": edge['data']
            }
        });

        return cytoscape({
            container: document.getElementById('cyGraphContainer'),
            boxSelectionEnabled: true,
            autounselectify: false,
            wheelSensitivity: 0.2,
            minZoom: 1e-2,
            maxZoom: 1e2,
            elements: graph_json['elements'],
            layout: layout,

            //Style properties of NODE body
            style: _.concat(defaultStylesheet, cytoscapeGraph.parseStylesheet(style_json), selectedElementsStylesheet),

            ready: function () {

                //setup popup dialog for displaying dialog when nodes/edges
                //are clicked for information.
                $('#dialog').dialog({
                    autoOpen: false
                });
                // display node data as a popup
                this.on('tap', graphPage.onTapGraphElement);

            }
        });

    },
};