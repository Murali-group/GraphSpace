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
            $('#colorpicker1').css('background-color', event.color.toString());
            $('#colorpicker1').val(event.color.toString());
            if (compareGraphPage.cyGraph) {
                compareGraphPage.setNodesColor('graph_1', event.color.toString());
                compareGraphPage.setNodesColor('common_1', $('#operatorcolorpicker').val());
                compareGraphPage.setNodesColor('common_2', $('#operatorcolorpicker').val());
            }
        });
        $('#colorpicker2').colorpicker();
        $('#colorpicker2').colorpicker().on('changeColor', function (event) {
            $('#colorpicker2').css('background-color', event.color.toString());
            $('#colorpicker2').val(event.color.toString());
            if (compareGraphPage.cyGraph) {
                compareGraphPage.setNodesColor('graph_2', event.color.toString());
                compareGraphPage.setNodesColor('common_1', $('#operatorcolorpicker').val());
                compareGraphPage.setNodesColor('common_2', $('#operatorcolorpicker').val());
            }
        });
        $('#operatorcolorpicker').colorpicker();
        $('#operatorcolorpicker').colorpicker().on('changeColor', function (event) {
            $('#operatorcolorpicker').css('background-color', event.color.toString());
            $('#operatorcolorpicker').val(event.color.toString());
            compareGraphPage.setNodesColor('common_1', event.color.toString());
            compareGraphPage.setNodesColor('common_2', event.color.toString());
        });
        if ( graph_1_id && graph_2_id && operation ){
            $('#dropdownMenu1').attr('value', graph_1_id);
            $('#dropdownMenu2').attr('value', graph_2_id);
            $('#operatorMenu1').attr('value', operation);
            $('#operatorMenu1').parent().find('a[row_id="'+ operation +'"]').click();
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
    convertToPostfix: function () {

    },
    loadGraphs: function () {
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
        var label = obj.parent().parent().siblings('button').children('i');
        if (label.text()) {
            label.text(label.attr('value'));
            obj.parent().parent().siblings('button').children('bold').text(obj.attr('data'));
        } else {
            obj.parent().parent().siblings("button[class*='dropdown-toggle']").text(obj.attr('data'));
            obj.parent().parent().siblings("button[class*='dropdown-toggle']").append('<span class="caret"></span>');
            compareGraphPage.compareGraphs();
        }
        obj.parent().parent().siblings("button[class*='dropdown-toggle']").attr("value", obj.attr('row_id'));
    },
    populateCompareDropdownMenu: function (data) {
        $.each(data, function (i, item) {
            if ($('#UserEmail').val() == item.owner_email && $(".compare-dropdown[mygraphs='false']").length) {
                $(".compare-dropdown").append('<li class="dropdown-header">My Graphs </li>');
                $(".compare-dropdown").attr('mygraphs', 'true');
            } else if (item.owner_email.startsWith("public") && $(".compare-dropdown[publicgraphs='false']").length) {
                $(".compare-dropdown").append('<li role="separator" class="divider"></li>');
                $(".compare-dropdown").append('<li class="dropdown-header">Public Graphs </li>');
                $(".compare-dropdown").attr('publicgraphs', 'true');
            } else if ($('#UserEmail').val() != item.owner_email && !item.owner_email.startsWith("public") && $(".compare-dropdown[mygraphs='false']").length) {
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
        compareGraphPage.cyGraph.filter(":parent[id='" + graph_parent + "']").style({
            'background-color': color,
            'background-opacity': 0,
            'border-opacity': 0,
            'border-color':color,
        });
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").style({'background-color': color, 'border-color': color});
        compareGraphPage.cyGraph.filter("node[parent='" + graph_parent + "']").connectedEdges().style({'line-color': color});
        compareGraphPage.cyGraph.filter("node[id='graph_1']").style({'background-opacity': 0, 'font-size': '1px'});
        compareGraphPage.cyGraph.filter("node[id='graph_2']").style({'background-opacity': 0, 'font-size': '1px'});
        compareGraphPage.cyGraph.filter("node[id='common_1']").style({'background-opacity': 0, 'font-size': '1px'});
        compareGraphPage.cyGraph.filter("node[id='common_2']").style({'background-opacity': 0, 'font-size': '1px'});
    },
    setGraph0Groups: function (graph_json, common_nodes) {
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
    setGraph1Groups: function (graph_json, common_nodes) {
        const len = graph_json['elements']['nodes'].length;
        var common_id = undefined;
        var duplicate_nodes = [];
        graph_json['elements']['nodes'][len] = {
            'data': {
                'id': 'graph_2',
                'label': 'Graph 2',
                'name': 'Graph 2'
            }
        };
        graph_json['elements']['nodes'][len + 1] = {'data': {'id': 'common_2', 'label': 'Common', 'name': 'Common'}};
        _.each(graph_json['elements']['nodes'], function (item) {
            if (item['data']['id'] != graph_json['elements']['nodes'][len]['data']['id'])
                item['data']['parent'] = graph_json['elements']['nodes'][len]['data']['id'];
            _.each(common_nodes, function (innerNode) {
                if (innerNode.length)
                    innerNode = (innerNode[0]['graph_id'] == compareGraphPage.graph_ids[1]) ? innerNode[0] : innerNode[1];
                if (item['data']['label'] == innerNode['label']) {
                    if (!common_id) {
                        common_id = item['data']['id'];
                        compareGraphPage.common_nodes['parent2'] = common_id;
                    }
                    item['data']['parent'] = 'common_2';

                    duplicate_nodes.push(item);
                }
            });
        });
        _.each(duplicate_nodes, function (node) {
            graph_json['elements']['nodes'].splice(graph_json['elements']['nodes'].indexOf(node),1);
        });
        graph_json['elements']['nodes'][len - duplicate_nodes.length + 1]['data']['parent'] = 'graph_2';
    },
    compareGraphs: function () {
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
                        $('#dropdownMenu1').parent().find('a[row_id="'+ graph_1_id +'"]').click();
                        $('#dropdownMenu2').parent().find('a[row_id="'+ graph_2_id +'"]').click();
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

        compareGraphPage.cyGraph.filter(":parent").style({
            'font-size': '0px',
        });
        compareGraphPage.cyGraph.filter(":edges").style({
            'text-outline-color': '#FFFFFF',
            'line-color': '#000000'
        });
        compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").layout({
            'name': 'grid',
            'animate': false,
            'padding': 10
        }).run();
        compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").layout({
            'name': 'grid',
            'animate': false,
            'padding': 10
        }).run();
        compareGraphPage.cyGraph.filter("node[parent='" + 'common_2' + "']").layout({
            'name': 'grid',
            'animate': false,
            'padding': 10
        }).run();

        compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").layout({
            'name': 'grid',
            'animate': false,
            'padding': 10
        }).run();

        let x_max = compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").max(function (ele, i, eles) {
            return ele.position()['x'];
        });
        let y_max = compareGraphPage.cyGraph.filter("node[parent='" + 'graph_1' + "']").max(function (ele, i, eles) {
            return ele.position()['y'];
        });
        y_max = Math.max(y_max.value, compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").max(function (ele, i, eles) {
            return ele.position()['y'];
        }).value);
        let cm_len_2 = compareGraphPage.cyGraph.filter("node[parent='" + 'common_2' + "']").max(function (ele, i, eles) {
            return ele.position()['x'];
        }).value - compareGraphPage.cyGraph.filter("node[parent='" + 'common_2' + "']").min(function (ele, i, eles) {
            return ele.position()['x'];
        }).value;

        let cm_len_1 = compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").max(function (ele, i, eles) {
            return ele.position()['x'];
        }).value - compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").min(function (ele, i, eles) {
            return ele.position()['x'];
        }).value;

        compareGraphPage.cyGraph.filter("node[parent='" + 'graph_2' + "']").layout({
            'name': 'grid', 'animate': false, 'padding': 10, transform: (node) => {
                let position = {};
                position.x = node.position('x') + x_max.value + 100;
                position.y = node.position('y');
                return position;
            }
        }).run();

        compareGraphPage.cyGraph.filter("node[parent='" + 'common_2' + "']").layout({
            'name': 'grid', 'animate': false, 'padding': 10, transform: (node) => {
                let position = {};
                position.x = node.position('x') + Math.abs(cm_len_2 / 2 - x_max.value) + 100;
                position.y = node.position('y') + y_max + 150;
                return position;
            }
        }).run();

        compareGraphPage.cyGraph.filter("node[parent='" + 'common_1' + "']").layout({
            'name': 'grid', 'animate': false, 'padding': 10, transform: (node) => {
                let position = {};
                position.x = node.position('x') + Math.abs(cm_len_1 / 2 - x_max.value) + 100;
                position.y = node.position('y') + y_max + 150;
                return position;
            }
        }).run();
    },
    CommonElementsHelper: function(nodes){

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
    compareGraphHelper: function () {
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


                    compareGraphPage.setGraph0Groups(compareGraphPage.graphs_json[0], response['nodes']);
                    compareGraphPage.setGraph1Groups(compareGraphPage.graphs_json[1], response['nodes']);
                    compareGraphPage.graphs_json[0]['elements']['nodes'] = compareGraphPage.graphs_json[0]['elements']['nodes'].concat(compareGraphPage.graphs_json[1]['elements']['nodes']);
                    compareGraphPage.graphs_json[0]['elements']['edges'] = compareGraphPage.graphs_json[0]['elements']['edges'].concat(compareGraphPage.graphs_json[1]['elements']['edges']);
                    compareGraphPage.styles_json[0]['style'] = compareGraphPage.styles_json[0]['style'].concat(compareGraphPage.styles_json[1]['style']);

                    compareGraphPage.cyGraph = compareGraphPage.constructCytoscapeGraph(compareGraphPage.graphs_json[0], compareGraphPage.styles_json[0]);

                    compareGraphPage.populateNodeData(response['nodes']);
                    compareGraphPage.populateEdgeData(response['edges']);
                    // compareGraphPage.setCommonElements(response['nodes']);
                    compareGraphPage.cyGraph.ready(function () {                 // Wait for cytoscape to actually load and map eles
                        compareGraphPage.cyGraph.nodes().forEach(function (ele) { // Your function call inside
                            console.log("loop", ele.id(), ele.position());
                        });
                        compareGraphPage.formatCyGraph();
                        compareGraphPage.cyGraph.panzoom();
                        compareGraphPage.cyGraph.reset().fit().center();
                    });

                    $('#nodes-total-badge').text(response['nodes'].length);
                    $('#edges-total-badge').text(response['edges'].length);

                    compareGraphPage.setNodesColor('graph_1', $('#colorpicker1').val());
                    compareGraphPage.setNodesColor('graph_2', $('#colorpicker2').val());

                    compareGraphPage.setNodesColor('common_1', $('#operatorcolorpicker').val());
                    compareGraphPage.setNodesColor('common_2', $('#operatorcolorpicker').val());

                    $('#nodes-table').DataTable().draw();
                    $('#edges-table').DataTable().draw();
                    $('.dataTables_length').addClass('bs-select');

                    $('#nodes-li').show();
                    $('#visualization-li').show();
                    $('#edges-li').show();
                    $('#visualization-li a:last').tab('show');
                    $('#visualization-li a:first').tab('show');
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
        location.replace("/compare");

    },
    populateNodeData: function (nodes) {
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
                // cyNode1 = compareGraphPage.cyGraph.getElementById(item[0]['label']);
                // cyNode2 = compareGraphPage.cyGraph.getElementById(item[1]['label']);

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

        layout = {
            name: 'grid',
            padding: 20,
            fit: true,
            animate: false
        };

        graph_json['elements']['nodes'] = _.map(graph_json['elements']['nodes'], function (node) {
            var newNode = {
                "data": node['data']
            };
            if ('position' in node) {
                newNode['position'] = node['position'];
                layout = {
                    name: 'preset'
                };
            }
            return newNode
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
                // this.layout({
                //             'name': 'grid',
                //             'animate': false,
                //         }).run();
                // this.reset();
                // this.fit();
                // this.center();
                // display node data as a popup
                this.on('tap', graphPage.onTapGraphElement);

            }
        });

    },
};