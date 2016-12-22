/**
 * Created by adb on 25/11/16.
 */

var apis = {
    graphs: {
        ENDPOINT: '/javascript/graphs/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.graphs.ENDPOINT, data, successCallback, errorCallback)
        },
        add: function (data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.graphs.ENDPOINT, data, successCallback, errorCallback)
        },
        getByID: function (id, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        update: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.graphs.ENDPOINT + id, data, successCallback, errorCallback)
        },
        delete: function (id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        getSharedGroups: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.graphs.ENDPOINT + id + '/groups', data, successCallback, errorCallback)
        },
        shareGraph: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.graphs.ENDPOINT + id + '/groups', data, successCallback, errorCallback)
        },
        unshareGraph: function (graph_id, group_id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.graphs.ENDPOINT + graph_id + '/groups/' + group_id, undefined, successCallback, errorCallback)
        }
    },
    nodes: {
        ENDPOINT: '/javascript/nodes/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.nodes.ENDPOINT, data, successCallback, errorCallback)
        },
    },
    edges: {
        ENDPOINT: '/javascript/edges/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.edges.ENDPOINT, data, successCallback, errorCallback)
        },
    },
    layouts: {
        ENDPOINT: '/javascript/layouts/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.layouts.ENDPOINT, data, successCallback, errorCallback)
        },
        add: function (data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.layouts.ENDPOINT, data, successCallback, errorCallback)
        },
        getByID: function (id, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.layouts.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        update: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.layouts.ENDPOINT + id, data, successCallback, errorCallback)
        },
        delete: function (id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.layouts.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
    },
    jsonRequest: function (method, url, data, successCallback, errorCallback) {
        $.ajax({
            headers: {
                'Accept': 'application/json'
            },
            method: method,
            data: method == 'GET' ? data : JSON.stringify(data),
            url: url,
            success: successCallback,
            error: errorCallback
        });
    }

};

var graphsPage = {
    init: function () {
        /**
         * This function is called to setup the graphs page.
         * It will initialize all the event listeners.
         */
        console.log('Loading Graphs Page....');

        $('#ok').click(function () {
            $('table').bootstrapTable('refresh');
        });

        $('#clear').click(function () {
            $('input.graphs-table-search').val('');
            $('table').bootstrapTable('refresh');
        });

        $('input.graphs-table-search').keypress(function (e) {
            if (e.which == 13) {
                $("#ok").trigger("click");
                return false;
            }
        });

        $('#ConfirmRemoveGraphBtn').click(graphsPage.graphsTable.onRemoveGraphConfirm);

        utils.initializeTabs();
    },
    graphsTable: {
        searchTag: function (e) {
            searchedTag = $(e).text();
            tags = _.uniq(_.pull(_.split($('#tagSearchBar').val(), ','), '', undefined));

            if (_.indexOf(tags, searchedTag) == -1) {
                console.log(tags);
                tags.push(searchedTag);
                $('#tagSearchBar').val(_.join(tags, ','));
                $("#ok").trigger("click");
            }
        },
        graphNameFormatter: function (value, row) {
            return $('<a>').attr('href', '/graphs/' + row.id).text(value)[0].outerHTML;
        },
        tagsFormatter: function (value, row) {
            links = "";
            for (i in row.tags) {
                links += $('<a>').attr('href', '#').html($('<span>').attr('class', 'label label-info tag-btn').attr('onclick', 'graphsPage.graphsTable.searchTag(this);').text(row.tags[i].name)[0])[0].outerHTML + '&nbsp;';
            }
            return links
        },
        ownerEmailFormatter: function (value, row) {
            if (_.startsWith(row.owner_email, 'public_user_')) {
                return "Anonymous User";
            } else {
                return row.owner_email;
            }
        },
        visibilityFormatter: function (value, row) {
            if (row.is_public === 1) {
                return "<i class='fa fa-globe fa-lg'></i> Public";
            } else {
                return "<i class='fa fa-lock fa-lg'></i> Private";
            }
        },
        queryParams: function (params) {
            //var params = {};
            $('#toolbar').find('input[name]').each(function () {
                params[$(this).attr('name')] = $(this).val();
            });
            return params;
        },
        operationsFormatter: function (value, row, index) {
            if (row.owner_email === $('#UserEmail').val()) {
                return [
                    '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Remove">',
                    'Remove <i class="glyphicon glyphicon-remove"></i>',
                    '</a>'
                ].join('');
            } else {
                return '';
            }
        },
        operationEvents: {
            'click .remove': function (e, value, row, index) {
                $('#deleteGraphModal').data('graph-id', row.id).modal('show');
            }
        },
        onRemoveGraphConfirm: function (e) {
            e.preventDefault();
            apis.graphs.delete($('#deleteGraphModal').data('graph-id'),
                successCallback = function (response) {
                    // This method is called when graph is successfully deleted.
                    // The entry from the table is deleted.
                    $('table').bootstrapTable('remove', {
                        field: 'id',
                        values: [$('#deleteGraphModal').data('graph-id')]
                    });
                    $('#deleteGraphModal').modal('hide');
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group_to_graph relationship.
                    alert(xhr.responseText);
                });
        },
    },
    sharedGraphsTable: {
        getGraphsByGroupMember: function (params) {
            /**
             * This is the custom ajax request used to load graphs in sharedGraphsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["names"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') === -1;
                }), function (str) {
                    return '%' + str + '%';
                });

                params.data["nodes"] = params.data["names"];
                params.data["edges"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') !== -1;
                }), function (str) {
                    edge = _.split(str, ':');
                    return '%' + edge[0] + '%:%' + edge[1] + '%';
                });
            }

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["member_email"] = $('#UserEmail').val();

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    params.success(response);
                    $('#sharedGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    params.error('Error');
                }
            );
        },
    },
    publicGraphsTable: {
        getPublicGraphs: function (params) {
            /**
             * This is the custom ajax request used to load graphs in publicGraphsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["names"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') === -1 || _.trim(s) !== '';
                }), function (str) {
                    return '%' + str + '%';
                });

                params.data["nodes"] = params.data["names"];
                params.data["edges"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') !== -1;
                }), function (str) {
                    edge = _.split(str, ':');
                    return '%' + edge[0] + '%:%' + edge[1] + '%';
                });
            }

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["is_public"] = 1;

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    params.success(response);
                    $('#publicGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    params.error('Error');
                }
            );
        },
    },
    ownedGraphsTable: {
        getGraphsByOwner: function (params) {
            /**
             * This is the custom ajax request used to load graphs in ownedGraphsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["names"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') === -1;
                }), function (str) {
                    return '%' + str + '%';
                });

                params.data["nodes"] = params.data["names"];
                params.data["edges"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') !== -1;
                }), function (str) {
                    edge = _.split(str, ':');
                    return '%' + edge[0] + '%:%' + edge[1] + '%';
                });
            }

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["owner_email"] = $('#UserEmail').val();

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    params.success(response);
                    $('#ownedGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    params.error('Error');
                }
            );
        }
    },
};

var uploadGraphPage = {
    init: function () {
        /**
         * This function is called to setup the upload graph page.
         * It will initialize all the event listeners.
         */

        $('.browse').click(function () {
            var file = $(this).parent().parent().parent().find('.file');
            file.trigger('click');
        });
        $('.file').change(function () {
            $(this).parent().find('.form-control').val($(this).val().replace(/C:\\fakepath\\/i, ''));
        });

        //Upload the graph
        $("#UploadGraphBtn").click(function (e) {
            e.preventDefault();

            if (_.trim($("#GraphNameInput").val()).length == 0) {
                return $.notify({
                    message: 'Please enter graph name!',
                }, {
                    type: 'warning'
                });
            }
            var graph = $("#graphname").val();

            if (_.trim($("#GraphFileInput").val()).length == 0) {
                return $.notify({
                    message: 'Please upload a valid file!',
                }, {
                    type: 'warning'
                });
            }
            $("#UploadGraphForm").submit();
        });

    }
};

var graphPage = {
    cyGraph: undefined,
    timeout: null,
    init: function () {
        /**
         * This function is called to setup the graph page.
         * It will initialize all the event listeners.
         */
        graphPage.cyGraph = graphPage.contructCytoscapeGraph();
        $('#saveLayoutBtn').click(function () {
            graphPage.saveLayout($('#layoutNameInput').val());
        });

        $('#layoutEditorBtn').click(function () {
            graphPage.layoutEditor.init();
        });

        $('#exitLayoutEditorBtn').click(function () {
            $('#exitLayoutBtn').removeClass('hidden');
            $('#saveLayoutModal').modal('show');
        });

        $('#exitLayoutBtn, #saveLayoutBtn').click(function () {
            cytoscapeGraph.showGraphInformation(graphPage.cyGraph);
        });

        $('#saveLayoutModalBtn').click(function () {
            $('#exitLayoutBtn').addClass('hidden');
            $('#saveLayoutModal').modal('show');
        });

        $("#unselectBtn").click(function (e) {
            //Unselect all nodes/edges when button is clicked
            e.preventDefault();
            cytoscapeGraph.unSelectAllNodes(graphPage.cyGraph);
            cytoscapeGraph.unSelectAllEdges(graphPage.cyGraph);

            $('input:checkbox[name=colors]').each(function (index) {
                $(this).prop('checked', false);
            });
            $('input:checkbox[name=shapes]').each(function (index) {
                $(this).prop('checked', false);
            });
        });

    },
    export: function (format) {
        cytoscapeGraph.export(graphPage.cyGraph, format, $('#GraphName').val());
    },
    onSelectLayoutBtnClick: function (e) {
        if ($(e).hasClass('auto-layout')) {
            graphPage.applyLayout(cytoscapeGraph.getAutomaticLayoutSettings($(e).data('layout-id')));
        } else {
            apis.layouts.getByID($(e).data('layout-id'),
                successCallback = function (response) {
                    graphPage.applyLayout({
                        name: 'preset',
                        positions: JSON.parse(response['json'])
                    });
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group_to_graph relationship.
                    alert("Layout does not exist or has not been shared yet!");
                });
        }
    },
    applyLayout: function (layout) {
        graphPage.cyGraph.layout(layout);
    },
    saveLayout: function (layoutName) {
        if (_.trim(layoutName).length === 0) {
            return $.notify({
                message: 'Please enter a valid layout name!',
            }, {
                type: 'warning'
            });
        }

        layout_json = cytoscapeGraph.getLayout(graphPage.cyGraph);

        apis.layouts.add({
                "owner_email": $('#UserEmail').val(),
                "graph_id": $('#GraphID').val(),
                "name": layoutName,
                "json": layout_json
            },
            successCallback = function (response) {
                $('#saveLayoutModal').modal('toggle');
            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert(xhr.responseText);
            })
    },
    onShareGraphWithPublicBtn: function (e, graph_id) {

        apis.graphs.update(graph_id, {
                'is_public': 1
            },
            successCallback = function (response) {
                // This method is called when group_to_graph relationship is successfully deleted.
                // The entry from the table is deleted.
                $(e).parent().find('.unshare-graph-btn').removeClass('hidden');
                $(e).addClass('hidden');

            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert(xhr.responseText);
            });


    },
    onUnshareGraphWithPublicBtn: function (e, graph_id) {

        apis.graphs.update(graph_id, {
                'is_public': 0
            },
            successCallback = function (response) {
                // This method is called when group_to_graph relationship is successfully deleted.
                // The entry from the table is deleted.
                $(e).parent().find('.share-graph-btn').removeClass('hidden');
                $(e).addClass('hidden');

            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert(xhr.responseText);
            });


    },
    onShareGraphWithGroupBtn: function (e, graph_id, group_id) {

        apis.graphs.shareGraph(graph_id, {
                'group_id': group_id
            },
            successCallback = function (response) {
                // This method is called when group_to_graph relationship is successfully deleted.
                // The entry from the table is deleted.
                $(e).parent().find('.unshare-graph-btn').removeClass('hidden');
                $(e).addClass('hidden');

            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert(xhr.responseText);
            });


    },
    onUnshareGraphWithGroupBtn: function (e, graph_id, group_id) {

        apis.graphs.unshareGraph(graph_id, group_id,
            successCallback = function (response) {
                // This method is called when group_to_graph relationship is successfully deleted.
                // The entry from the table is deleted.
                $(e).parent().find('.share-graph-btn').removeClass('hidden');
                $(e).addClass('hidden');

            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert(xhr.responseText);
            });
    },
    onInputSearchEdgesAndNodes: function (e) {
        clearTimeout(graphPage.timeout);

        // Unselecting all elements before selecting searched elements.
        _.each(graphPage.cyGraph.elements(), function (element) {
            element.unselect();
        });

        graphPage.timeout = setTimeout(function () { // Wait for User to Stop Typing, Using JavaScript

            nodes = _.map(_.filter(_.pull(_.split(_.trim($(e).val()), ','), ''), function (s) {
                return s.indexOf(':') === -1;
            }), function (str) {
                return '%' + _.trim(str) + '%';
            });

            edges = _.map(_.filter(_.split(_.trim($(e).val()), ','), function (s) {
                return s.indexOf(':') !== -1;
            }), function (str) {
                edge = _.split(str, ':');
                return '%' + edge[0] + '%:%' + edge[1] + '%';
            });
            if (_.trim($(e).val()).length > 0) {
                apis.nodes.get({
                        "graph_id": $('#GraphID').val(),
                        "names": nodes,
                        "labels": nodes
                    },
                    successCallback = function (response) {
                        _.each(response.nodes, function (node) {
                            graphPage.cyGraph.$('#' + node.name).select();
                        });

                    },
                    errorCallback = function (xhr, status, errorThrown) {
                        alert(xhr.responseText);
                    });
                apis.edges.get({
                        "graph_id": $('#GraphID').val(),
                        "edges": edges
                    },
                    successCallback = function (response) {
                        _.each(response.edge, function (edge) {
                            graphPage.cyGraph.edges('[edgeId=' + edge.id + ']').select();
                        });

                    },
                    errorCallback = function (xhr, status, errorThrown) {
                        alert(xhr.responseText);
                    });
            }

            graphPage.timeout = null;
        }, 1000);
    },
    onSearchNodesEdgesBtnClick: function (e) {
        console.debug($(e).parent().parent().find('input')[0]);
    },
    searchNodeAndEdges: function (e) {
        $(e).val()
    },
    contructCytoscapeGraph: function (layout) {
        if (!layout) {
            layout = {
                name: 'random',
                padding: 10,
                fit: true,
                animate: false
            };
        }
        return cytoscape({
            container: document.getElementById('cyGraphContainer'),
            boxSelectionEnabled: true,
            autounselectify: false,
            elements: graph_json['graph'],
            layout: layout,

            //Style properties of NODE body
            style: stylesheet
        });

    },
    nodesTable: {
        getNodesByGraphID: function (params) {
            /**
             * This is the custom ajax request used to load nodes in nodesTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["names"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') === -1;
                }), function (str) {
                    return '%' + str + '%';
                });
                params.data["labels"] = params.data["names"];
            }

            params.data["graph_id"] = $('#GraphID').val();

            apis.nodes.get(params.data,
                successCallback = function (response) {
                    // This method is called when nodes are successfully fetched.
                    params.success(response);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching nodes.
                    params.error('Error');
                }
            );
        }
    },
    edgesTable: {
        getEdgesByGraphID: function (params) {
            /**
             * This is the custom ajax request used to load nodes in edgesTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["names"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') === -1;
                }), function (str) {
                    return '%' + str + '%';
                });
                params.data["edges"] = _.map(_.filter(_.split(params.data["search"], ','), function (s) {
                    return s.indexOf(':') !== -1;
                }), function (str) {
                    edge = _.split(str, ':');
                    return '%' + edge[0] + '%:%' + edge[1] + '%';
                });
            }

            params.data["graph_id"] = $('#GraphID').val();

            apis.edges.get(params.data,
                successCallback = function (response) {
                    // This method is called when edges are successfully fetched.
                    params.success(response);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching edges.
                    params.error('Error');
                }
            );
        }
    },
    layoutEditor: {
        undoRedoManager: null,
        init: function () {

            graphPage.layoutEditor.undoRedoManager = new UndoManager(
                onUndo = function (item) {
                    console.log(item);
                    if (item) {
                        cytoscapeGraph.setRenderedNodePositions(graphPage.cyGraph, item);
                        $('#redoBtn').removeClass('disabled');
                    } else {
                        $('#undoBtn').addClass('disabled');
                    }
                },
                onRedo = function (item) {
                    if (item) {
                        cytoscapeGraph.setRenderedNodePositions(graphPage.cyGraph, item);
                        $('#undoBtn').removeClass('disabled');
                    } else {
                        $('#redoBtn').addClass('disabled');
                    }
                },
                onUpdate = function (item) {
                    $('#undoBtn').removeClass('disabled');
                }
            );

            graphPage.layoutEditor.undoRedoManager.update(cytoscapeGraph.getRenderedNodePositionsMap(graphPage.cyGraph));
            $('#undoBtn').addClass('disabled');

            var colors = _.uniq(_.map(graphPage.cyGraph.nodes(), function (node) {
                return node.data('background_color');
            }));

            var shapes = _.uniq(_.map(graphPage.cyGraph.nodes(), function (node) {
                return node.data('shape');
            }));

            $('#selectShapes').html('');
            $('#selectColors').html('');
            _.each(shapes, function (shape) {
                $('#selectShapes').append(
                    $('<label>', {class: "checkbox-inline"}).css({'margin-left': '10px'}).append(
                        $('<input>', {
                            id: shape,
                            type: 'checkbox',
                            value: shape,
                            name: 'shapes'
                        })).append(_.capitalize(shape)));
            });
            _.each(colors, function (color) {
                $('#selectColors').append(
                    $('<label>', {class: "checkbox-inline zero-padding"}).css({
                        'margin-left': '10px',
                        'margin-right': '10px'
                    }).append(
                        $('<input>', {
                            id: color,
                            type: 'checkbox',
                            value: color,
                            name: 'colors'
                        })).append($('<p>', {
                        class: 'select-color-box'
                    }).css('background', color)));
            });

            $('input:checkbox[name=shapes], input:checkbox[name=colors] ').change(function () {
                var selectedShapes = _.map($('input:checkbox[name=shapes]:checked'), function (elem) {
                    return $(elem).val();
                });
                var selectedColors = _.map($('input:checkbox[name=colors]:checked'), function (elem) {
                    return $(elem).val();
                });

                console.log(selectedColors, selectedShapes);

                if ($(this).attr('name') === 'colors') {
                    var attributeName = 'background_color';
                } else {
                    var attributeName = 'shape';
                }
                var attributeValue = $(this).val();
                var isSelected = $(this).is(":checked");

                _.each(graphPage.cyGraph.nodes(), function (node) {

                    if (attributeValue == node.data(attributeName)) {
                        if (isSelected) {
                            node.select();
                        } else {
                            if (_.indexOf(selectedColors, node.data('background_color')) === -1 && _.indexOf(selectedShapes, node.data('shape')) === -1) {
                                node.unselect();
                            }
                        }
                    }

                });

            });

            $('.arrange_nodes').click(function () {
                cytoscapeGraph.applyLayoutToCollection(
                    graphPage.cyGraph,
                    graphPage.cyGraph.collection(cytoscapeGraph.getAllSelectedNodes(graphPage.cyGraph)),
                    $(this).data('layout')
                );
                graphPage.layoutEditor.undoRedoManager.update(cytoscapeGraph.getRenderedNodePositionsMap(graphPage.cyGraph));
            });

            $('#undoBtn').click(function () {
                graphPage.layoutEditor.undoRedoManager.undo();
            });

            $('#redoBtn').click(function () {
                graphPage.layoutEditor.undoRedoManager.redo();
            });

            cytoscapeGraph.hideGraphInformation(graphPage.cyGraph);

            $("#startTourBtn").click(function () {
                var intro = introJs();
                intro.setOptions({
                    'scrollToElement': true,
                    'showStepNumbers': false,
                    'disableInteraction': true,
                    'overlayOpacity': 0.5
                });
                intro.start();
            });
        }
    }

};

var cytoscapeGraph = {
    getLayout: function (cy) {
        /*
         *  gets location of all the nodes so that it can be save later.
         *  cy: cytoscape graph object
         */
        var nodes = cy.elements('node');
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
    },
    export: function (cy, format, filename) {
        filename = filename ? filename : 'graph';
        var file = (format === 'jpg') ? cy.jpg({'full': true}) : (format === 'png' ? cy.png({'full': true}) : "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(cy.json()['elements'], null, 4)));
        $('<a>').attr('href', file).attr('download', filename + '.' + format)[0].click()
    },
    getAutomaticLayoutSettings: function (layout_name) {
        //The following code retrieves the specified layout
        //of a graph to be displayed.
        //Some of them are pre-defined. Check Cytoscapejs.org
        var graph_layout = {
            name: 'random',
            padding: 10,
            fit: true,
            animate: false
        };

        if (layout_name == "breadthfirst") {
            graph_layout = {
                name: "breadthfirst",
                padding: 10,
                fit: true,
                avoidOverlap: true,
                animate: false
            }
        } else if (layout_name == "concentric") {
            graph_layout = {
                name: "concentric",
                fit: true,
                padding: 10,
                avoidOverlap: true,
                animate: false
            }
        } else if (layout_name == "circle") {
            graph_layout = {
                name: "circle",
                padding: 10,
                fit: true,
                avoidOverlap: true,
                animate: false
            }
        } else if (layout_name == 'cose') {
            graph_layout = {
                name: "cose"
            }
        } else if (layout_name == "grid") {
            graph_layout = {
                name: "grid"
            }
        } else if (layout_name == "cola") {
            graph_layout = {
                name: "cola",
                flow: {axis: 'y', minSeparation: 30},
                edgeSymDiffLength: 6
            }
        }
        return graph_layout;
    },
    hideGraphInformation: function (cy) {
        /*
         Function to hide information about the graph that the layout editor doesn't need to see.
         */
        cy.style()
            .selector('node').style({
                'font-size': "0px"
            })
            .selector('edge').style({
                'line-color': 'black',
                'line-style': 'solid',
                'width': .1
            })
            .update(); // update the elements in the graph with the new style

    },
    showGraphInformation: function (cy) {
        /*
         Function to Show information about the graph that the layout editor hid from the users.
         */
        cy.style(stylesheet);
    },
    getRenderedNodePositionsMap: function (cy) {
        var result = {};
        _.each(cy.nodes(), function (node) {
            result[node.id()] = node.renderedPosition();
        });
        return result;
    },
    setRenderedNodePositions: function (cy, positions) {
        _.each(cy.nodes(), function (node) {
            node.renderedPosition(positions[node.id()]);
        });
    },
    unSelectAllNodes: function (cy) {
        _.each(cy.nodes(), function (node) {
            node.unselect();
        });
    },
    unSelectAllEdges: function (cy) {
        _.each(cy.edges(), function (edge) {
            edge.unselect();
        });
    },
    getAllSelectedNodes: function (cy) {
        return _.filter(cy.nodes(), function (node) {
            return node.selected();
        });
    },
    applyLayoutToCollection: function (cy, collection, layout_name) {
        if (layout_name === "circle") {
            collection.layout(
                {
                    name: "circle",
                    fit: false,
                    avoidOverlap: false,
                    padding: 0
                });
        } else if (layout_name === "fill_circle") {
            collection.layout(
                {
                    name: "concentric",
                    fit: false,
                    avoidOverlap: false,
                    padding: 40
                });
        } else if (layout_name === "grid") {
            collection.layout(
                {
                    name: "grid",
                    fit: false,
                    avoidOverlap: true,
                    condense: true
                });
        } else if (layout_name === "square") {
            cytoscapeGraph.runSquareLayoutOnCollection(cy, collection);
        } else if (layout_name === "horizontal") {
            cytoscapeGraph.runHorizontalVerticalLayoutOnCollection(cy, collection, "horizontal");
        } else if (layout_name === "vertical") {
            cytoscapeGraph.runHorizontalVerticalLayoutOnCollection(cy, collection, "vertical");
        } else if (layout_name === "release") {
            cytoscapeGraph.runSqueezeReleaseOnCollection(collection, "release");
        } else if (layout_name === "squeeze") {
            cytoscapeGraph.runSqueezeReleaseOnCollection(collection, "squeeze");
        }
    },
    runSqueezeReleaseOnCollection: function (collection, type) {
        var data = cytoscapeGraph.computeCollectionCentroid(collection);

        var centroid = data[0];
        var selectedNodes = collection.nodes();

        for (var i = 0; i < selectedNodes.length; i++) {
            var node = selectedNodes[i];
            var position = node.renderedPosition();
            var distance = cytoscapeGraph.travelDistance(centroid, position);

            if (!isNaN(position.x)) {
                if (position.x < centroid.x) {
                    if (type === 'squeeze') {
                        position.x += distance.x;
                    } else {
                        position.x -= distance.x;
                    }

                }
                if (position.x > centroid.x) {
                    if (type == 'squeeze') {
                        position.x -= distance.x;
                    } else {
                        position.x += distance.x;
                    }
                }
            }

            if (!isNaN(position.y)) {
                if (position.y < centroid.y) {
                    if (type == 'squeeze') {
                        position.y += distance.y;
                    } else {
                        position.y -= distance.y;
                    }
                }
                if (position.y > centroid.y) {
                    if (type == 'squeeze') {
                        position.y -= distance.y;
                    } else {
                        position.y += distance.y;
                    }
                }
            }

            if (!isNaN(position.x) && !isNaN(position.y)) {
                node.renderedPosition(position);
            }
        }
    },
    runSquareLayoutOnCollection: function (cy, collection) {
        var minDistance = 0;
        var selectedArray = [];

        _.each(collection.nodes(), function (node) {
            selectedArray.push(node);
            minDistance = Math.max(node.boundingBox()["h"], minDistance);
        });

        //calculate center of the viewport
        var center = {
            x: cy.width() / 2,
            y: cy.height() / 2
        };


        var radius = (selectedArray.length / 4 * minDistance) / 2;

        if (selectedArray.length <= 4) {

            if (selectedArray.length == 0) {
                return;
            } else if (selectedArray.length == 1) {
                var newPosition = {
                    "x": center.x,
                    "y": center.y
                }
                selectedArray[0].renderedPosition(newPosition);
            } else if (selectedArray.length == 2) {
                var newPosition = {
                    "x": center.x,
                    "y": center.y + radius + minDistance
                }
                selectedArray[0].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x,
                    "y": center.y - radius
                }
                selectedArray[1].renderedPosition(newPosition);

            } else if (selectedArray.length == 3) {
                var newPosition = {
                    "x": center.x - radius,
                    "y": center.y - radius
                }
                selectedArray[0].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x + radius + minDistance,
                    "y": center.y - radius
                }
                selectedArray[1].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x + radius + minDistance,
                    "y": center.y + radius + minDistance
                }
                selectedArray[2].renderedPosition(newPosition);

            } else if (selectedArray.length == 4) {
                var newPosition = {
                    "x": center.x - radius,
                    "y": center.y - radius
                }
                selectedArray[0].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x + radius + minDistance,
                    "y": center.y - radius
                }
                selectedArray[1].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x + radius + minDistance,
                    "y": center.y + radius + minDistance
                }
                selectedArray[2].renderedPosition(newPosition);
                var newPosition = {
                    "x": center.x - radius,
                    "y": center.y + radius + minDistance
                }
                selectedArray[3].renderedPosition(newPosition);
            }
            return;
        }

        //Group into regions (top, bottom, left, right) Assuem that we have at least 4 selected elements

        //Top region
        var topBar = selectedArray.slice(0, selectedArray.length / 4);

        for (var i = 0; i < topBar.length; i++) {
            var newPosition = {
                "x": center.x - radius + (i * minDistance),
                "y": center.y - radius
            }
            topBar[i].renderedPosition(newPosition);
        }

        //Bottom Region
        var bottomBar = selectedArray.slice(selectedArray.length / 4, 2 * selectedArray.length / 4);

        for (var i = 0; i < bottomBar.length; i++) {
            var newPosition = {
                "x": center.x - radius + (i * minDistance),
                "y": center.y + radius
            }
            bottomBar[i].renderedPosition(newPosition);
        }

        //Left Region
        var leftBar = selectedArray.slice(2 * selectedArray.length / 4, 3 * selectedArray.length / 4);

        for (var i = 0; i < leftBar.length; i++) {
            var newPosition = {
                "x": center.x - radius,
                "y": center.y - radius + (i * minDistance)
            }
            leftBar[i].renderedPosition(newPosition);
        }

        //Right Region
        var rightBar = selectedArray.slice(3 * selectedArray.length / 4, 4 * selectedArray.length);

        for (var i = 0; i < rightBar.length; i++) {
            var newPosition = {
                "x": center.x + radius,
                "y": center.y - radius + (i * minDistance)
            }
            rightBar[i].renderedPosition(newPosition);
        }
    },
    runHorizontalVerticalLayoutOnCollection: function (cy, collection, layout_name) {
        var data = cytoscapeGraph.computeCollectionCentroid(collection);
        console.log(layout_name, layout_name === "vertical" ? 1 : 2);
        var center = {
            x: cy.width() / 2,
            y: cy.height() / 2
        };

        var selectedNodes = collection.nodes();
        var minDistance = data[layout_name === "vertical" ? 2 : 1];

        var radius = (selectedNodes.length / 4 * minDistance) / 2;

        for (var i = 0; i < selectedNodes.length; i++) {
            if (layout_name === "vertical") {
                var newPosition = {
                    "x": center.x,
                    "y": center.y - radius + (i * minDistance)
                };
            } else {
                var newPosition = {
                    "x": center.x - radius + (i * minDistance),
                    "y": center.y
                };
            }

            selectedNodes[i].renderedPosition(newPosition);
        }
    },
    computeCollectionCentroid: function (collection) {
        var centroid = {x: 0, y: 0};
        var minWidthDistance = 0;
        var minHeightDistance = 0;

        _.each(collection.nodes(), function (node) {
            var position = node.renderedPosition();
            centroid["x"] += position.x;
            centroid["y"] += position.y;
            minWidthDistance = Math.max(node.boundingBox()["w"], minWidthDistance);
            minHeightDistance = Math.max(node.boundingBox()["h"], minHeightDistance);
        });

        centroid["x"] /= collection.nodes().length;
        centroid["y"] /= collection.nodes().length;

        return [centroid, minWidthDistance, minHeightDistance];
    },
    travelDistance: function (center, nodePosition) {
        var a = Math.abs(center.x - nodePosition.x);
        var b = Math.abs(center.y - nodePosition.y);

        if (a == 0) {
            a = 1;
        }

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

};