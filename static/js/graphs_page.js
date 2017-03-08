/**
 * Created by adb on 25/11/16.
 */

var apis = {
    graphs: {
        ENDPOINT: '/ajax/graphs/',
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
        ENDPOINT: _.template('/ajax/graphs/<%= graph_id %>/nodes/'),
        get: function (graph_id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.nodes.ENDPOINT({'graph_id': graph_id}), data, successCallback, errorCallback)
        },
    },
    edges: {
        ENDPOINT: _.template('/ajax/graphs/<%= graph_id %>/edges/'),
        get: function (graph_id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.edges.ENDPOINT({'graph_id': graph_id}), data, successCallback, errorCallback)
        },
    },
    layouts: {
        ENDPOINT: _.template('/ajax/graphs/<%= graph_id %>/layouts/'),
        get: function (graph_id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.layouts.ENDPOINT({'graph_id': graph_id}), data, successCallback, errorCallback)
        },
        add: function (graph_id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.layouts.ENDPOINT({'graph_id': graph_id}), data, successCallback, errorCallback)
        },
        getByID: function (graph_id, layout_id, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.layouts.ENDPOINT({'graph_id': graph_id}) + layout_id, undefined, successCallback, errorCallback)
        },
        update: function (graph_id, layout_id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.layouts.ENDPOINT({'graph_id': graph_id}) + layout_id, data, successCallback, errorCallback)
        },
        delete: function (graph_id, layout_id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.layouts.ENDPOINT({'graph_id': graph_id}) + layout_id, undefined, successCallback, errorCallback)
        }
    },
    logging: {
        ENDPOINT: 'http://localhost:9200/layouts/action',
        add: function (data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.logging.ENDPOINT, data, successCallback, errorCallback)
        }
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
            graphsPage.searchBar.val(null).trigger('change');
            var queryRows = $('#queryBuilder').find('.row');
            for (i = 1; i < queryRows.length; i++) {
                queryRows[i].remove();
            }
            graphsPage.queryBuilder.clearQueryField($('#queryBuilder').find('.row')[0]);
        });

        $('input.graphs-table-search').keypress(function (e) {
            if (e.which == 13) {
                $("#ok").trigger("click");
                return false;
            }
        });

        graphsPage.searchBar = $(".graph-search").select2({
            tags: true,
            tokenSeparators: [',', ' '],
            placeholder: "Search graphs, nodes and edges."
        });

        graphsPage.searchBar.on('change', function (evt) {
            var query = graphsPage.searchBar.val() && graphsPage.searchBar.val().length > 0 ? '?query=' + graphsPage.searchBar.val() : '';
            window.history.pushState('query', 'Graphs Page', window.location.origin + window.location.pathname + query);
            $("#ok").trigger("click");
        });

        if (utils.getURLParameter('query') && utils.getURLParameter('query') != "") {
            _.each(_.split(utils.getURLParameter('query'), ','), function (val) {
                graphsPage.searchBar.append(new Option(val, val, true, true)).trigger('change');
            });
        }

        graphsPage.queryBuilder.initializeNodeSearchBar($("#queryBuilder").find('.row'));
        graphsPage.queryBuilder.initializeEdgeSearchBar($("#queryBuilder").find('.edge-row'));

        //show.bs.collapse

        $('#advancedSearchCollapse').on('shown.bs.collapse', function () {
            $('#advancedSearchBtn').text('Hide Advanced Search');
            graphsPage.searchBar.prop('disabled', true);
        });
        $('#advancedSearchCollapse').on('hidden.bs.collapse', function () {
            $('#advancedSearchBtn').text('Advanced Search');
            graphsPage.searchBar.prop('disabled', false);
        });

        $('#ConfirmRemoveGraphBtn').click(graphsPage.graphsTable.onRemoveGraphConfirm);

        utils.initializeTabs();
    },
    searchBar: null,
    queryBuilder: {
        computeQuery: function () {
            return _.filter(_.map($('#queryBuilder').find('.row'), function (queryRow) {
                if ($(queryRow).find('.datatype-select').val() == 'node') {
                    return $(queryRow).find('.node-search').select2('data').length > 0 ? $(queryRow).find('.node-search').select2('data')[0].id : null;
                } else {
                    selectedHeadOption = $(queryRow).closest('.edge-search').find('.edge-head-search').select2('data') ? $(queryRow).closest('.edge-search').find('.edge-head-search').select2('data')[0] : null;
                    selectedTailOption = $(queryRow).closest('.edge-search').find('.edge-tail-search').select2('data') ? $(queryRow).closest('.edge-search').find('.edge-tail-search').select2('data')[0] : null;
                    if (selectedHeadOption && selectedTailOption) {
                        return selectedHeadOption.id + ":" + selectedTailOption.id;
                    } else {
                        return null;
                    }
                }
            }));
        },
        syncQuery: function () {
            graphsPage.searchBar.find('option').remove();
            _.each(graphsPage.queryBuilder.computeQuery(), function (val) {
                graphsPage.searchBar.append(new Option(val, val, true, true)).trigger('change');
            });
        },
        initializeNodeSearchBar: function (queryRow) {
            queryRow.find('.datatype-select').select2();
            queryRow.find('.datatype-select').on('change', function (evt) {
                graphsPage.queryBuilder.changeQueryField($(this).closest('.row'), $(this).val());
            });
            queryRow.find('.node-search').select2({
                tags: true,
                tokenSeparators: [',', ' '],
                placeholder: "Search by gene/protein alias.",
                ajax: {
                    url: "/ajax/aliases/",
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            q: '%' + params.term + '%', // search term
                            offset: 0, //params.page*30 - 30,
                            limit: 100
                        };
                    },
                    processResults: function (data, params) {
                        // parse the results into the format expected by Select2
                        // since we are using custom formatting functions we do not need to
                        // alter the remote JSON data, except to indicate that infinite
                        // scrolling can be used
                        params.limit = params.limit || 100;

                        return {
                            results: data.uniprot_aliases,
                            pagination: {
                                more: (params.limit) < data.total_count
                            }
                        };
                    },
                    cache: true
                },
                escapeMarkup: function (markup) {
                    return markup;
                }, // let our custom formatter work
                minimumInputLength: 1,
                templateResult: function (alias) {
                    if (alias.alias_name) {
                        return alias.alias_name + " (UniProtKB: " + alias.id + " )";
                    } else {
                        return alias.text;
                    }
                },
                templateSelection: function (alias) {
                    if (alias.alias_name) {
                        return alias.alias_name + " (UniProtKB: " + alias.id + " )";
                    } else {
                        return alias.text;
                    }
                }
            });

            queryRow.find('.node-search').on('change', function (evt) {
                graphsPage.queryBuilder.syncQuery()
            });
        },
        initializeEdgeSearchBar: function (queryRow) {
            queryRow.find('.datatype-select').select2();
            queryRow.find('.datatype-select').on('change', function (evt) {
                graphsPage.queryBuilder.changeQueryField($(this).closest('.row'), $(this).val());
            });
            queryRow.find('.edge-head-search, .edge-tail-search').select2({
                tags: true,
                tokenSeparators: [',', ' '],
                placeholder: "Search by gene/protein alias.",
                ajax: {
                    url: "/ajax/aliases/",
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            q: '%' + params.term + '%', // search term
                            offset: 0, //params.page*30 - 30,
                            limit: 100
                        };
                    },
                    processResults: function (data, params) {
                        // parse the results into the format expected by Select2
                        // since we are using custom formatting functions we do not need to
                        // alter the remote JSON data, except to indicate that infinite
                        // scrolling can be used
                        params.limit = params.limit || 100;

                        return {
                            results: data.uniprot_aliases,
                            pagination: {
                                more: (params.limit) < data.total_count
                            }
                        };
                    },
                    cache: true
                },
                escapeMarkup: function (markup) {
                    return markup;
                }, // let our custom formatter work
                minimumInputLength: 1,
                templateResult: function (alias) {
                    if (alias.alias_name) {
                        return alias.alias_name + " (UniProtKB: " + alias.id + " )";
                        ;
                    } else {
                        return alias.text;
                    }
                },
                templateSelection: function (alias) {
                    if (alias.alias_name) {
                        return alias.alias_name + " (UniProtKB: " + alias.id + " )";
                        ;
                    } else {
                        return alias.text;
                    }
                }
            });

            queryRow.find('.edge-head-search, .edge-tail-search').on('change', function (evt) {
                graphsPage.queryBuilder.syncQuery()
            });
        },
        clearQueryField: function (queryRow) {
            if ($(queryRow).find('.datatype-select').val() == 'node') {
                $(queryRow).find('.node-search').val(null).trigger("change");
            } else {
                $(queryRow).find('.edge-head-search').val(null).trigger("change");
                $(queryRow).find('.edge-tail-search').val(null).trigger("change");
            }
            return queryRow;
        },
        removeQueryField: function (elem, queryType) {
            if (queryType == 'edge') {
                selectedHeadOption = $(elem).closest('.row').find('.edge-head-search').val();
                selectedTailOption = $(elem).closest('.row').find('.edge-tail-search').val();
                graphsPage.searchBar.find('option[value="' + selectedHeadOption + ":" + selectedTailOption + '"]').remove();
                $(elem).closest('.row').remove();
                if (selectedHeadOption && selectedTailOption) {
                    graphsPage.searchBar.trigger('change');
                }

            } else {
                selectedOption = $(elem).closest('.row').find('.node-search').val();
                graphsPage.searchBar.find('option[value="' + selectedOption + '"]').remove();
                $(elem).closest('.row').remove();
                if (selectedOption) {
                    graphsPage.searchBar.trigger('change');
                }
            }
        },
        addQueryField: function (elem, type) {
            if (type == 'edge') {
                $newQuery = $('<div class="row edge-search query-builder-field"> \
                            <div class="col-md-1 or-label"><p class="lead" style="text-align: right">OR</p></div> \
                            <div class="col-md-1"> \
                                <select class="form-control datatype-select"> \
                                    <option value="node" >Node</option> \
                                    <option value="edge" selected>Edge</option> \
                                </select> \
                            </div> \
                            <div class="col-md-1"><p class="lead" style="text-align: center">between</p></div> \
                            <div class="col-md-3"> \
                                <select class="edge-head-search" style="width: 100%"> \
                                </select> \
                            </div> \
                            <div class="col-md-1"><p class="lead" style="text-align: center">and</p></div> \
                            <div class="col-md-3"> \
                                <select class="edge-tail-search" style="width: 100%"> \
                                </select> \
                            </div> \
                            <div class="col-md-1 zero-margin zero-padding"> \
                                <button class="btn btn-default btn-sm  add-query-btn" aria-label="add" \
                                        style="border-color: transparent;color: green;" onclick="graphsPage.queryBuilder.addQueryField(this, \'edge\')"> \
                                    <i class="fa fa-plus-circle fa-lg" aria-hidden="true"></i> \
                                </button> \
                                <button class="btn btn-default btn-sm remove-query-btn" aria-label="remove" \
                                        style="border-color: transparent;color: red;" onclick="graphsPage.queryBuilder.removeQueryField(this, \'edge\')"> \
                                    <i class="fa fa-minus-circle fa-lg" aria-hidden="true"></i> \
                                </button>  \
                            </div> \
                        </div>');
                $(elem).closest('.row').after($newQuery);
                graphsPage.queryBuilder.initializeEdgeSearchBar($newQuery);
            } else {
                $newQuery = $('<div class="row query-builder-field"> \
                            <div class="col-md-1 or-label"><p class="lead" style="text-align: right">OR</p></div> \
                            <div class="col-md-1"> \
                                <select class="form-control datatype-select"> \
                                    <option value="node" selected>Node</option> \
                                    <option value="edge" >Edge</option> \
                                </select> \
                            </div> \
                            <div class="col-md-8"> \
                                <select class="node-search" style="width: 100%"> \
                                </select> \
                            </div> \
                            <div class="col-md-1 zero-margin zero-padding"> \
                                <button class="btn btn-default btn-sm  add-query-btn" aria-label="add" \
                                        style="border-color: transparent;color: green;" onclick="graphsPage.queryBuilder.addQueryField(this, \'node\')"> \
                                    <i class="fa fa-plus-circle fa-lg" aria-hidden="true"></i> \
                                </button> \
                                <button class="btn btn-default btn-sm  remove-query-btn" aria-label="remove" \
                                        style="border-color: transparent;color: red;" onclick="graphsPage.queryBuilder.removeQueryField(this, \'node\')"> \
                                    <i class="fa fa-minus-circle fa-lg" aria-hidden="true"></i> \
                                </button>  \
                            </div> \
                        </div>');
                $(elem).closest('.row').after($newQuery);
                graphsPage.queryBuilder.initializeNodeSearchBar($newQuery);
            }
            return $newQuery;
        },
        changeQueryField: function (queryRow, newType) {
            $newQuery = graphsPage.queryBuilder.addQueryField(queryRow, newType);
            if ($(queryRow).closest('.row').find('.or-label').html() == "") {
                $newQuery.find('.or-label').html('');
                $newQuery.find('.remove-query-btn').remove();
            }
            graphsPage.queryBuilder.removeQueryField(queryRow, newType == 'edge' ? 'node' : 'edge');
        }
    },
    graphsTable: {
        searchTag: function (e) {
            searchedTag = $(e).text();
            tags = _.uniq(_.pull(_.split($('#tagSearchBar').val(), ','), '', undefined));

            if (_.indexOf(tags, searchedTag) == -1) {
                tags.push(searchedTag);
                $('#tagSearchBar').val(_.join(tags, ','));
                $("#ok").trigger("click");
            }
        },
        graphNameFormatter: function (value, row) {
            var queryString = (graphsPage.searchBar.val() && graphsPage.searchBar.val().length > 0) ? '?query=' + _.join(graphsPage.searchBar.val(), ',') : '';
            return $('<a>').attr('href', '/graphs/' + row.id + queryString).text(value)[0].outerHTML;
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
            params['search'] = $('.graph-search').val() ? $('.graph-search').val() : [];
            params['nodes'] = $('.node-search').val() ? $('.graph-search').val() : [];


            params["names"] = _.map(_.filter(params["search"], function (s) {
                return s.indexOf(':') === -1;
            }), function (str) {
                return '%' + str + '%';
            });

            params["nodes"] = _.map(params["nodes"], function (str) {
                return '%' + str + '%';
            });

            params["nodes"] = _.union(params["names"], params['nodes']);
            params["edges"] = _.map(_.filter(params["search"], function (s) {
                return s.indexOf(':') !== -1;
            }), function (str) {
                edge = _.split(str, ':');
                return '%' + edge[0] + '%:%' + edge[1] + '%';
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
                    $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
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
            $('#SharedGraphsTable').bootstrapTable('showLoading');
            $('#sharedGraphsTotal').html('<i class="fa fa-refresh fa-spin fa fa-fw"></i>');

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["member_email"] = $('#UserEmail').val();

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    $('#SharedGraphsTable').bootstrapTable('hideLoading');
                    params.success(response);
                    $('#sharedGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    $('#SharedGraphsTable').bootstrapTable('hideLoading');
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
            $('#PublicGraphsTable').bootstrapTable('showLoading');
            $('#publicGraphsTotal').html('<i class="fa fa-refresh fa-spin fa fa-fw"></i>');

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["is_public"] = 1;

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    $('#PublicGraphsTable').bootstrapTable('hideLoading');
                    params.success(response);
                    $('#publicGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    $('#PublicGraphsTable').bootstrapTable('hideLoading');
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
            $('#OwnedGraphsTable').bootstrapTable('showLoading');

            $('#ownedGraphsTotal').html('<i class="fa fa-refresh fa-spin fa fa-fw"></i>');

            if (params.data["tags"]) {
                params.data["tags"] = _.map(_.split(params.data["tags"], ','), function (str) {
                    return '%' + str + '%';
                });
            }

            params.data["owner_email"] = $('#UserEmail').val();

            apis.graphs.get(params.data,
                successCallback = function (response) {
                    // This method is called when graphs are successfully fetched.
                    $('#OwnedGraphsTable').bootstrapTable('hideLoading');
                    params.success(response);
                    $('#ownedGraphsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching graphs.
                    $('#OwnedGraphsTable').bootstrapTable('hideLoading');
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
            } else if (_.trim($("#GraphFileInput").val()).length == 0) {
                return $.notify({
                    message: 'Please upload a valid file!',
                }, {
                    type: 'warning'
                });
            } else {
                $(this).button('loading');
                $("#UploadGraphForm").submit();
            }

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

        graphPage.cyGraph.panzoom();

        utils.initializeTabs();

        $('#saveLayoutBtn').click(function () {
            graphPage.cyGraph.contextMenus('get').destroy(); // Destroys the cytocscape context menu extension instance.

            cytoscapeGraph.showGraphInformation(graphPage.cyGraph);
            // display node data as a popup
            graphPage.cyGraph.unbind('tap').on('tap', graphPage.onTapGraphElement);

            graphPage.saveLayout($('#layoutNameInput').val());
        });

        $('#layoutEditorBtn').click(function () {
            graphPage.layoutEditor.init();
        });

        $('#exitLayoutEditorBtn').click(function () {
            $('#exitLayoutBtn').removeClass('hidden');
            $('#saveLayoutModal').modal('show');
        });

        $('#exitLayoutBtn').click(function () {
            graphPage.cyGraph.contextMenus('get').destroy(); // Destroys the cytocscape context menu extension instance.

            cytoscapeGraph.showGraphInformation(graphPage.cyGraph);
            // display node data as a popup
            graphPage.cyGraph.unbind('tap').on('tap', graphPage.onTapGraphElement);
        });

        $('#saveLayoutModalBtn').click(function () {
            $('#exitLayoutBtn').addClass('hidden');
            $('#saveLayoutModal').modal('show');
        });

        $('#ConfirmRemoveLayoutBtn').click(graphPage.layoutsTable.onConfirmRemoveGraph);
        $('#ConfirmUpdateLayoutBtn').click(graphPage.layoutsTable.onConfirmUpdateGraph);

        this.filterNodesEdges.init();

        if (window.location.hash == '#editor') {
            $('#layoutEditorBtn').trigger('click');
        }

        if (!_.isEmpty(utils.getURLParameter('auto_layout'))) {
            graphPage.applyAutoLayout(utils.getURLParameter('auto_layout'));
        } else if (!_.isEmpty(utils.getURLParameter('user_layout'))) {
            graphPage.applyUserLayout(utils.getURLParameter('user_layout'));
        }

        $('#graphVisualizationTabBtn').click(function (e) {
            window.setTimeout(function () {
                $('#cyGraphContainer').css('height', '99%');
            }, 100);

        });

        $('#inputSearchEdgesAndNodes').val(utils.getURLParameter('query')).trigger('onkeyup');

        graphPage.defaultLayoutWidget.init();
    },
    export: function (format) {
        cytoscapeGraph.export(graphPage.cyGraph, format, $('#GraphName').val());
    },
    applyAutoLayout: function (layout_id) {
        graphPage.applyLayout(cytoscapeGraph.getAutomaticLayoutSettings(layout_id));
        window.history.pushState('auto-layout', 'Graph Page', window.location.origin + window.location.pathname + '?auto_layout=' + layout_id);
        graphPage.defaultLayoutWidget.init(0);
    },
    applyUserLayout: function (layout_id) {
        apis.layouts.getByID($('#GraphID').val(), layout_id,
            successCallback = function (response) {
                graphPage.applyLayoutStyle(JSON.parse(response['json'])['style']);
                graphPage.applyLayout({
                    name: 'preset',
                    positions: JSON.parse(response['json'])['positions']
                });
                window.history.pushState('user-layout', 'Graph Page', window.location.origin + window.location.pathname + '?user_layout=' + layout_id);
                graphPage.defaultLayoutWidget.init(response['is_shared']);
            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                alert("Layout does not exist or has not been shared yet!");
            });
    },
    onSelectLayoutBtnClick: function (e) {
        if ($(e).hasClass('auto-layout')) {
            graphPage.applyAutoLayout($(e).data('layout-id'));
        } else {
            graphPage.applyUserLayout($(e).data('layout-id'));
        }
    },
    applyLayoutStyle: function (layoutStyle) {
        layoutStyle = _.map(layoutStyle, function (elemStyle) {
            elem = graphPage.cyGraph.elements(elemStyle['selector']);
            if (elem.isNode()) {
                return {
                    'selector': elemStyle['selector'],
                    'style': graphPage.getGraphSpaceNodeStyle(elemStyle['style'], elem.data())
                }
            } else {
                return {
                    'selector': elemStyle['selector'],
                    'style': graphPage.getGraphSpaceEdgeStyle(elemStyle['style'], elem.data())
                }
            }
        });
        graphPage.cyGraph.style().fromJson(_.concat(defaultStylesheet, layoutStyle, selectedElementsStylesheet)).update();
    },
    applyLayout: function (layout) {
        // TODO: Convert the old layout format to new layout format.
        /*

         The reason we need the new format is that it loads faster and it doesnt require any additional code for
         pre processing whereas we need to format the old format before passing it to the cytoscape layout function.

         The new format looks like :
         var new_format = {
         "json": {
         "<node_id>": {
         "x": 19.28,
         "y": 287.97
         },
         ....
         }
         };

         var old_format = {
         "json": [
         {
         "x": 19.28,
         "y": 287.97,
         "id": "<node_id>"
         },
         .....
         ]
         };
         */
        if (isArray(layout.positions)) {
            var corrected_positions = {};
            _.forEach(layout.positions, function (node) {
                corrected_positions[node.id] = node;
            });
            layout.positions = corrected_positions;
        }
        graphPage.cyGraph.layout(layout);

    },
    saveLayout: function (layoutName) {
        graphPage.cyGraph.elements().unselect();

        if (_.trim(layoutName).length === 0) {
            return $.notify({
                message: 'Please enter a valid layout name!',
            }, {
                type: 'warning'
            });
        } else {
            if (graphPage.layoutEditor.undoRedoManager) {
                _.each(graphPage.layoutEditor.undoRedoManager.state, function (action, i) {
                    if (action['action_type'] === 'select') {
                        if (action['data']['elements'].length > 0) {
                            action['data']['elements'] = action['data']['elements'].jsons();
                        }
                    }
                    // Uncomment the code after setting up the elastic server.

                    //apis.logging.add({
                    //        'layout_name': layoutName,
                    //        'graph_id': $('#GraphID').val(),
                    //        'user_id': $('#UserEmail').val(),
                    //        'action': action,
                    //        'step': i
                    //    },
                    //    successCallback = function (response) {
                    //        console.log(response);
                    //    },
                    //    errorCallback = function (xhr, status, errorThrown) {
                    //        // This method is called when  error occurs while deleting group_to_graph relationship.
                    //        $.notify({                             message: xhr.responseJSON.error_message                         }, {                             type: 'danger'                         });
                    //    })
                });
            }

            layout_json = {
                'positions': cytoscapeGraph.getNodePositions(graphPage.cyGraph),
                'style': cytoscapeGraph.getStylesheet(graphPage.cyGraph)
            };

            apis.layouts.add($('#GraphID').val(), {
                    "owner_email": $('#UserEmail').val(),
                    "graph_id": $('#GraphID').val(),
                    "name": layoutName,
                    "json": layout_json
                },
                successCallback = function (response) {
                    $('#saveLayoutModal').modal('toggle');
                    $('#PrivateLayoutsTable').bootstrapTable('refresh');
                    $('#SharedLayoutsTable').bootstrapTable('refresh');
                },
                errorCallback = function (response) {
                    // This method is called when  error occurs while deleting group_to_graph relationship.
                    $.notify({
                        message: response.responseJSON.error_message
                    }, {
                        type: 'danger'
                    });
                });
        }

    },
    addLayoutBtns: function (layout, domID) {
        // domID: ID of the dom in which the layout btns will be inserted.
        $('#' + domID).append(
            $('<li>', {
                class: "margin-bottom-2"
            }).append(
                $('<button>', {
                    'type': "button",
                    'class': "btn btn-default gs-full-width select-layout-btn user-layout",
                    'data-layout-id': layout.id,
                    'onclick': "graphPage.onSelectLayoutBtnClick(this)"
                }).html('<b>' + layout.name + '</b> <br> created by ' + layout.owner_email)
            )
        );
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
                $.notify({
                    message: xhr.responseJSON.error_message
                }, {
                    type: 'danger'
                });

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
                $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
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
                $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
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
                $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
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
                if (nodes.length > 0) {
                    apis.nodes.get($('#GraphID').val(), {
                            "names": nodes,
                            "labels": nodes
                        },
                        successCallback = function (response) {
                            _.each(response.nodes, function (node) {
                                graphPage.cyGraph.$("[id = '" + node.name + "']").select();
                            });
                        },
                        errorCallback = function (xhr, status, errorThrown) {
                            $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
                        }
                    );
                }

                if (edges.length > 0) {
                    apis.edges.get($('#GraphID').val(), {
                            "edges": edges
                        },
                        successCallback = function (response) {
                            _.each(response.edges, function (edge) {
                                graphPage.cyGraph.edges("[name = '" + edge.name + "']").select();
                            });
                        },
                        errorCallback = function (xhr, status, errorThrown) {
                            $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
                        }
                    );
                }
            }
            graphPage.timeout = null;
        }, 250);
    },
    onTapGraphElement: function (evt) {
        this.elements().removeCss('color');
        // get target
        var target = evt.cyTarget;
        // target some element other than background (node/edge)
        if (target !== this) {
            var popup = target._private.data.popup

            //When user clicks an element, turn that element red
            this.$('[id="' + target._private.data.id + '"]').css('color', 'red');

            //If there is no embedded content, don't display anything
            if (popup == null || popup.length == 0) {
                return;
            }

            //Display embedded content if there is any
            if (target._private.data.popup != null && target._private.data.popup.length > 0) {
                $("#dialog").html("<p>" + target._private.data.popup + "</p>");
            }
            if (target._private.group == 'edges') {
                $('#dialog').dialog('option', 'title', target._private.data.source + "-" + target._private.data.target);
            } else {
                $('#dialog').dialog('option', 'title', target.style('label'));
            }

            $("#dialog").dialog({
                'maxHeight': 500
            });
            $('#dialog').dialog('open');

        } else {
            //If another element was clicked, remove the red color from previously clicked element
            this.elements().removeCss('color');
        }
    },
    getGraphSpaceNodeStyle: function (nodeStyle, nodeData) {
        /*
         This function will check if the style object has valid values and fix them otherwise.

         nodeStyle - JSON object of style attributes,
         */

        //VALUES CONSISTENT AS OF CYTOSCAPEJS 2.5.0
        //DONE TO SUPPORT OLD GRAPHS AND SETS A MINIMUM SETTINGS TO AT LEAST DISPLAY GRAPH IF USER
        //DOESN'T HAVE ANY OTHER SETTINGS TO ALTER HOW THE NODES IN GRAPH LOOKS
        var acceptedShapes = ["rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star", "diamond", "vee", "rhomboid", "polygon"];

        //If the node has a shape, make sure that shape is recognized by CytoscapeJS
        //Otherwise, make shape an ellipse
        if (nodeStyle.hasOwnProperty('shape') == true && acceptedShapes.indexOf(nodeStyle['shape'].toLowerCase()) == -1) {
            //TO SUPPORT OLD GRAPHS THAT HAD THESE SHAPES
            if (nodeStyle['shape'].toLowerCase() == 'square') {
                nodeStyle['shape'] = "rectangle"
            }
        } else if (nodeStyle['shape']) {
            nodeStyle['shape'] = nodeStyle['shape'].toLowerCase();
        }

        //Pick default color if nothing is provided
        if (nodeStyle['background-color'] != undefined) {
            var hexCode = colourNameToHex(nodeStyle['background-color']);
            if (hexCode != false) {
                nodeStyle['background-color'] = hexCode;
            } else {
                if (isHexaColor(addCharacterToHex(nodeStyle['background-color']))) {
                    nodeStyle['background-color'] = addCharacterToHex(nodeStyle['background-color']);
                }
            }
        }

        return nodeStyle;
    },
    getNodeStylesheet: function (nodeJSON) {
        /**
         * get style properties of node objects and set style object to null because if set it will set unmutable style properties.
         */
        return _.map(nodeJSON, function (node) {
            return {
                'selector': _.template("node[id='<%= id %>']")({'id': node['data']['id']}),
                'style': graphPage.getGraphSpaceNodeStyle(node['style'], node['data'])
            };
        });
    },
    getGraphSpaceEdgeStyle: function (edgeStyle, edgeData) {
        /*
         This function will check if the style object has valid values and fix them otherwise.

         edgeStyle - JSON object of style attributes,
         */

        //Color property maps to line_color
        //DONE TO SUPPORT OLD GRAPHS
        if (edgeStyle.hasOwnProperty('color')) {
            edgeStyle['line-color'] = edgeStyle['color'];
        }

        if (edgeStyle['line-color'] != undefined) {
            //Converts the line color into Hexadecimal so CytoscapeJS can user it
            var hexCode = colourNameToHex(edgeStyle['line-color']);
            if (hexCode != false) {
                edgeStyle['line-color'] = hexCode;
            } else {
                if (isHexaColor(addCharacterToHex(edgeStyle['line-color']))) {
                    edgeStyle['line-color'] = addCharacterToHex(edgeStyle['line-color']);
                }
            }
        }

        //DONE TO SUPPORT OLD GRAPHS: If "directed" property is not there, edge is undirected, otherwise it is directed
        if (edgeStyle['target-arrow-shape'] == undefined || (edgeData['directed'] == false || edgeData['directed'] == 'false')) {
            edgeStyle['target-arrow-shape'] = 'none';
        } else if (edgeData['directed'] == true) {
            edgeStyle['target-arrow-shape'] = 'triangle';
        }

        return edgeStyle;
    },
    getEdgeStylesheet: function (edgeJSON) {

        return _.map(edgeJSON, function (edge) {
            return {
                'selector': _.template("edge[name='<%= name %>']")({'name': edge['data']['name']}),
                'style': graphPage.getGraphSpaceEdgeStyle(edge['style'], edge['data'])
            };
        });

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
        var nodeStylesheet = graphPage.getNodeStylesheet(graph_json['graph']['nodes']);
        var edgeStylesheet = graphPage.getEdgeStylesheet(graph_json['graph']['edges']);

        graph_json['graph']['nodes'] = _.map(graph_json['graph']['nodes'], function (node) {
            return {
                "data": node['data']
            }
        });
        graph_json['graph']['edges'] = _.map(graph_json['graph']['edges'], function (edge) {
            return {
                "data": edge['data']
            }
        });

        return cytoscape({
            container: document.getElementById('cyGraphContainer'),
            boxSelectionEnabled: true,
            autounselectify: false,
            minZoom: 1e-2,
            maxZoom: 1e2,
            elements: graph_json['graph'],
            layout: layout,

            //Style properties of NODE body
            style: _.concat(defaultStylesheet, nodeStylesheet, edgeStylesheet, selectedElementsStylesheet),

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
    defaultLayoutWidget: {
        init: function (is_shared) {
            if (utils.getURLParameter('auto_layout') || _.isNil(is_shared) || is_shared == 0) {
                $('#setDefaultLayoutBtn').hide();
                $('#removeDefaultLayoutBtn').hide();
            } else if (utils.getURLParameter('user_layout') && utils.getURLParameter('user_layout') == default_layout_id) {
                $('#setDefaultLayoutBtn').hide();
                $('#removeDefaultLayoutBtn').show();
            } else {
                $('#setDefaultLayoutBtn').show();
                $('#removeDefaultLayoutBtn').hide();
            }
        },
        onSetDefaultLayoutBtn: function (e) {
            apis.graphs.update($('#GraphID').val(), {
                'default_layout_id': utils.getURLParameter('user_layout')
            },
            successCallback = function (response) {
                default_layout_id = utils.getURLParameter('user_layout');
                graphPage.defaultLayoutWidget.init(1);
            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                $.notify({
                        message: response.responseJSON.error_message
                    }, {
                        type: 'danger'
                    });
            });
        },
        onRemoveDefaultLayoutBtn: function (e) {
            apis.graphs.update($('#GraphID').val(), {
                'default_layout_id': 0
            },
            successCallback = function (response) {
                default_layout_id = null;
                graphPage.defaultLayoutWidget.init(1);
            },
            errorCallback = function (xhr, status, errorThrown) {
                // This method is called when  error occurs while deleting group_to_graph relationship.
                $.notify({
                        message: response.responseJSON.error_message
                    }, {
                        type: 'danger'
                    });
            });
        }
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

            apis.nodes.get($('#GraphID').val(), params.data,
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
    layoutsTable: {
        getPrivateLayoutsByGraphID: function (params) {
            /**
             * This is the custom ajax request used to load layouts in layoutsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["name"] = '%' + params.data["search"] + '%';
            }

            params.data["is_shared"] = 0;
            params.data["owner_email"] = $('#UserEmail').val();

            apis.layouts.get($('#GraphID').val(), params.data,
                successCallback = function (response) {
                    // This method is called when layouts are successfully fetched.
                    params.success(response);

                    $('#userPrivateLayoutBtns').html('');
                    _.each(response.layouts, function (layout) {
                        graphPage.addLayoutBtns(layout, 'userPrivateLayoutBtns');
                    });
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching layouts.
                    params.error('Error');
                }
            );
        },
        getSharedLayoutsByGraphID: function (params) {
            /**
             * This is the custom ajax request used to load layouts in layoutsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                params.data["name"] = '%' + params.data["search"] + '%';
            }

            params.data["is_shared"] = 1;

            apis.layouts.get($('#GraphID').val(), params.data,
                successCallback = function (response) {
                    // This method is called when layouts are successfully fetched.
                    params.success(response);

                    $('#userSharedLayoutBtns').html('');
                    _.each(response.layouts, function (layout) {
                        graphPage.addLayoutBtns(layout, 'userSharedLayoutBtns');
                    });
                },
                errorCallback = function () {
                    // This method is called when error occurs while fetching layouts.
                    params.error('Error');
                }
            );
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<div class="pull-left">',
                row['name'],
                '</div>',
                '<div class="pull-right">',
                row['owner_email'] == $('#UserEmail').val() ? '&nbsp;<a class="edit-layout" href="javascript:void(0)" title="Rename Layout"> Rename <i class="fa fa-lg fa-pencil"></i> </a>&nbsp;' : '',
                row['is_shared'] == 0 ? '&nbsp;<a class="share-layout" href="javascript:void(0)" title="Share Layout"> Share <i class="fa fa-lg fa-eye" aria-hidden="true"></i> </a>&nbsp;' : '<a class="unshare-layout" href="javascript:void(0)" title="Unshare Layout"> Unshare <i class="fa fa-lg fa-eye-slash" aria-hidden="true"></i> </a>&nbsp;',
                row['owner_email'] == $('#UserEmail').val() ? '&nbsp;<a class="delete-layout" href="javascript:void(0)" title="Delete Layout"> Delete <i class="fa fa-lg fa-trash"></i> </a>' : '',
                '</div>'
            ].join('');
        },
        operationEvents: {
            'click .delete-layout': function (e, value, row, index) {
                $('#deleteLayoutModal').data('layout-id', row.id).modal('show');
            },
            'click .edit-layout': function (e, value, row, index) {
                $('#editLayoutModal').data('layout-id', row.id).modal('show');
            },
            'click .share-layout': function (e, value, row, index) {
                apis.layouts.update($('#GraphID').val(), row.id, {'is_shared': 1},
                    successCallback = function (response) {
                        // This method is called when layout is successfully shared.
                        // The entry from the table is deleted.
                        $('#SharedLayoutsTable').bootstrapTable('refresh');
                        $('#PrivateLayoutsTable').bootstrapTable('refresh');
                    },
                    errorCallback = function (response) {
                        // This method is called when  error occurs while sharing layout.
                        $.notify({
                            message: response.responseJSON.error_message
                        }, {
                            type: 'danger'
                        });
                    });
            },
            'click .unshare-layout': function (e, value, row, index) {
                apis.layouts.update($('#GraphID').val(), row.id, {'is_shared': 0},
                    successCallback = function (response) {
                        // This method is called when layout is successfully unshared.
                        // The entry from the table is deleted.
                        $('#SharedLayoutsTable').bootstrapTable('refresh');
                        $('#PrivateLayoutsTable').bootstrapTable('refresh');
                    },
                    errorCallback = function (response) {
                        // This method is called when  error occurs while unsharing layout.
                        $.notify({
                            message: response.responseJSON.error_message
                        }, {
                            type: 'danger'
                        });
                    });
            }
        },
        onConfirmRemoveGraph: function (e) {
            e.preventDefault();
            apis.layouts.delete($('#GraphID').val(), $('#deleteLayoutModal').data('layout-id'),
                successCallback = function (response) {
                    // This method is called when layout is successfully deleted.
                    // The entry from the table is deleted.
                    $('#SharedLayoutsTable').bootstrapTable('refresh');
                    $('#PrivateLayoutsTable').bootstrapTable('refresh');
                    $('#deleteLayoutModal').modal('hide');
                },
                errorCallback = function (response) {
                    // This method is called when  error occurs while deleting layout.
                    $.notify({
                        message: response.responseJSON.error_message
                    }, {
                        type: 'danger'
                    });
                });
        },
        onConfirmUpdateGraph: function (e) {
            e.preventDefault();
            apis.layouts.update($('#GraphID').val(), $('#editLayoutModal').data('layout-id'), {
                    "name": $('#newlayoutNameInput').val()
                },
                successCallback = function (response) {
                    // This method is called when layout is successfully updated.
                    // The entry from the table is updated.
                    $('#SharedLayoutsTable').bootstrapTable('refresh');
                    $('#PrivateLayoutsTable').bootstrapTable('refresh');
                    $('#editLayoutModal').modal('hide');
                },
                errorCallback = function (response) {
                    // This method is called when  error occurs while updating layout.
                    $.notify({
                        message: response.responseJSON.error_message
                    }, {
                        type: 'danger'
                    });
                });
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

            apis.edges.get($('#GraphID').val(), params.data,
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
            cytoscapeGraph.contextMenu.init(graphPage.cyGraph);

            graphPage.layoutEditor.undoRedoManager = new UndoManager(
                onUndo = function (item) {
                    if (item) {
                        if (item['action_type'] === 'select') {
                            graphPage.cyGraph.elements('*').unselect();
                            graphPage.cyGraph.collection(item['data']['elements']).select();
                        } else {
                            cytoscapeGraph.setRenderedNodePositions(graphPage.cyGraph, item['data']['positions']);
                        }
                        $('#redoBtn').removeClass('disabled');
                    } else {
                        $('#undoBtn').addClass('disabled');
                    }
                },
                onRedo = function (item) {
                    if (item) {
                        if (item['action_type'] === 'select') {
                            graphPage.cyGraph.elements('*').unselect();
                            graphPage.cyGraph.collection(item['data']['elements']).select();
                        } else {
                            cytoscapeGraph.setRenderedNodePositions(graphPage.cyGraph, item['data']['positions']);
                        }
                        $('#undoBtn').removeClass('disabled');
                    } else {
                        $('#redoBtn').addClass('disabled');
                    }
                },
                onUpdate = function (item) {
                    $('#undoBtn').removeClass('disabled');
                }
            );

            graphPage.layoutEditor.undoRedoManager.update({
                'action_type': 'move',
                'data': {
                    'positions': cytoscapeGraph.getRenderedNodePositionsMap(graphPage.cyGraph)
                }
            });

            graphPage.layoutEditor.undoRedoManager.update({
                'action_type': 'select',
                'data': {
                    'elements': graphPage.cyGraph.elements(':selected')
                }
            });

            graphPage.cyGraph.on('free', function (e) {
                graphPage.layoutEditor.undoRedoManager.update({
                    'action_type': 'move',
                    'data': {
                        'positions': cytoscapeGraph.getRenderedNodePositionsMap(graphPage.cyGraph)
                    }
                });
            });

            // display node data as a popup
            graphPage.cyGraph.unbind('tap').on('tap', function (evt) {
                graphPage.layoutEditor.undoRedoManager.update({
                    'action_type': 'select',
                    'data': {
                        'elements': graphPage.cyGraph.elements(':selected')
                    }
                });
            });

            $('#undoBtn').addClass('disabled');

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

                graphPage.layoutEditor.undoRedoManager.update({
                    'action_type': 'select',
                    'data': {
                        'elements': graphPage.cyGraph.elements(':selected')
                    }
                });
            });

            graphPage.layoutEditor.nodeSelector.init();

            $('.arrange_nodes').click(function () {
                cytoscapeGraph.applyLayoutToCollection(
                    graphPage.cyGraph,
                    graphPage.cyGraph.collection(cytoscapeGraph.getAllSelectedNodes(graphPage.cyGraph)),
                    $(this).data('layout')
                );
                graphPage.layoutEditor.undoRedoManager.update({
                    'action_type': 'move',
                    'data': {
                        'positions': cytoscapeGraph.getRenderedNodePositionsMap(graphPage.cyGraph)
                    }
                });
            });

            $('#undoBtn').click(function () {
                graphPage.layoutEditor.undoRedoManager.undo();
            });

            $('#redoBtn').click(function () {
                graphPage.layoutEditor.undoRedoManager.redo();
            });

            //cytoscapeGraph.hideGraphInformation(graphPage.cyGraph);

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

            $('#toggleNodeLabels').prop('checked', true);

            $('#toggleNodeLabels').change(function (e) {
                if ($('#toggleNodeLabels').is(":checked")) {
                    cytoscapeGraph.showGraphInformation(graphPage.cyGraph);
                } else {
                    cytoscapeGraph.hideGraphInformation(graphPage.cyGraph);
                }
            });

            graphPage.layoutEditor.nodeEditor.init();

        },
        nodeSelector: {
            init: function () {
                var colors = _.uniq(_.map(graphPage.cyGraph.nodes(), function (node) {
                    return node.style('background-color');
                }));
                $('#selectColors').html('');
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

                var shapes = _.uniq(_.map(graphPage.cyGraph.nodes(), function (node) {
                    return node.style('shape');
                }));
                $('#selectShapes').html('');
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

                $('input:checkbox[name=shapes], input:checkbox[name=colors] ').change(function () {
                    var selectedShapes = _.map($('input:checkbox[name=shapes]:checked'), function (elem) {
                        return $(elem).val();
                    });
                    var selectedColors = _.map($('input:checkbox[name=colors]:checked'), function (elem) {
                        return $(elem).val();
                    });

                    if ($(this).attr('name') === 'colors') {
                        var attributeName = 'background-color';
                    } else {
                        var attributeName = 'shape';
                    }
                    var attributeValue = $(this).val();
                    var isSelected = $(this).is(":checked");

                    _.each(graphPage.cyGraph.nodes(), function (node) {

                        if (attributeValue == node.style(attributeName)) {
                            if (isSelected) {
                                node.select();
                            } else {
                                if (_.indexOf(selectedColors, node.style('background-color')) === -1 && _.indexOf(selectedShapes, node.style('shape')) === -1) {
                                    node.unselect();
                                }
                            }
                        }

                    });

                    graphPage.layoutEditor.undoRedoManager.update({
                        'action_type': 'select',
                        'data': {
                            'elements': graphPage.cyGraph.elements(':selected')
                        }
                    });
                });
            }
        },
        nodeEditor: {
            init: function () {
                $('#applyNodePropertiesBtn').click(function () {
                    nodeSelector = _.template("node[name='<%= name %>']");

                    if (_.isEmpty($('#nodeWidth').val())) {
                        return $.notify({
                            message: 'Please enter valid width value!',
                        }, {
                            type: 'warning'
                        });
                    } else if (_.isEmpty($('#nodeHeight').val())) {
                        return $.notify({
                            message: 'Please enter valid height value!',
                        }, {
                            type: 'warning'
                        });
                    } else if (_.isEmpty($("#nodeBackgroundColorPicker").colorpicker('getValue'))) {
                        return $.notify({
                            message: 'Please enter valid color value!',
                        }, {
                            type: 'warning'
                        });
                    } else if (_.isEmpty($('#nodeShape').val())) {
                        return $.notify({
                            message: 'Please enter valid shape value!',
                        }, {
                            type: 'warning'
                        });
                    } else {
                        _.each(graphPage.cyGraph.elements(':selected'), function (elem) {
                            graphPage.cyGraph.style().selector(nodeSelector({'name': elem.data('name')})).style({
                                'shape': $('#nodeShape').val(),
                                'width': _.toString($('#nodeWidth').val()) + 'px',
                                'height': _.toString($('#nodeHeight').val()) + 'px',
                                'background-color': $("#nodeBackgroundColorPicker").colorpicker('getValue')
                            }).update();
                        });
                        graphPage.layoutEditor.nodeSelector.init();
                    }

                });
            },
            open: function (collection) {
                $('.gs-sidebar-nav').removeClass('active');
                $('#nodeEditorSideBar').addClass('active');

                $('#nodeShape').val(collection.style('shape'));
                $('#nodeBackgroundColor').val(collection.style('background-color'));
                $('#nodeWidth').val(_.replace(collection.style('width'), 'px', ''));
                $('#nodeHeight').val(_.replace(collection.style('height'), 'px', ''));

                $("#nodeBackgroundColorPicker").colorpicker();
            }

        }
    },
    filterNodesEdges: {
        init: function () {
            //Hides appropriate nodes based on k value
            $("#input_k").val(graphPage.filterNodesEdges.getLargestK(graph_json.graph));

            /*
             * When input_k bar is changed, update the nodes shown in the graph.
             */
            $("#input_k").bind("change", function () {
                graphPage.filterNodesEdges.setInputK();
            });

            //Shows up to maximum k values
            $("#input_max").val(graphPage.filterNodesEdges.getLargestK(graph_json.graph));

            //When user slides, it changes value of slider as well
            //as updates graph to reflect max k values allowed in subgraph
            $("#slider").slider({
                value: $("#input_max").val(),
                max: $("#input_max").val(),
                min: 0,
                step: 1,
                slide: function (event, ui) {
                    $("#input_k").val(ui.value);
                    m_val = ui.value;
                    if (m_val < 0) {
                        m_val = 0;
                        $(this).slider({
                            value: 0
                        });
                    }
                },
                change: function (event, ui) {
                    if (event.originalEvent) {
                        graphPage.filterNodesEdges.showOnlyK();
                    }
                }
            });
        },
        setInputK: function () {
            /*
             * Updates the text box when the user slides the bar.
             */
            if ($("#input_k").val() < 0) {
                $("#input_k").val(0);
            }
            if (parseInt($("#input_k").val()) > parseInt($("#input_max").val())) {
                $("#input_k").val($("#input_max").val());

            }
            graphPage.filterNodesEdges.setBarToValue($("#input_k"), "slider");
            $("#slider").slider({
                value: $("#input_k").val(),
                max: $('#input_max').val()
            });
        },
        getLargestK: function (graph_json) {
            // Gets the largest K value elements from the graph
            // and only renders those values
            var edges = graph_json['edges'];

            var largestK = 0;
            for (var i = 0; i < edges.length; i++) {
                k_val = parseInt(edges[i]['data']['k']);
                if (k_val > largestK) {
                    largestK = k_val;
                }
            }
            return largestK;
        },
        applyMax: function (graph_layout) {
            //Gets all nodes and edges up do the max value set
            //and only renders them
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

            graphPage.cyGraph.load(newJSON);
            graphPage.filterNodesEdges.showOnlyK();
        },
        showOnlyK: function () {
            // Returns all the id's that are > k value
            if ($("#input_k").val()) {
                if ($("#input_k").val().length > 0) {
                    var maxVal = parseInt($("#input_k").val());

                    graphPage.cyGraph.elements().show();
                    hideList = graphPage.cyGraph.filter('[k > ' + maxVal + ']');
                    hideList.hide();
                }
            }
        },
        setBarToValue: function (inputId, barId) {
            /**
             * If the user enters a value greater than the max value allowed, change value of bar to max allowed value.
             * inputId the id of the input bar
             * barId  the id of the max paths shown bar.
             */
            if ($(inputId).val() > $("#input_max").val()) {
                $(inputId).val($("#input_max").val());
            }
            graphPage.filterNodesEdges.showOnlyK();
        }
    }

};

var cytoscapeGraph = {
    contextMenu: {
        init: function (cy) {
            var selectAllOfTheSameType = function (ele) {
                cy.elements().unselect();
                if (ele.isNode()) {
                    cy.nodes().select();
                }
                else if (ele.isEdge()) {
                    cy.edges().select();
                }
            };
            var unselectAllOfTheSameType = function (ele) {
                if (ele.isNode()) {
                    cy.nodes().unselect();
                }
                else if (ele.isEdge()) {
                    cy.edges().unselect();
                }
            };

            var cm = graphPage.cyGraph.contextMenus({
                menuItems: [
                    {
                        id: 'edit-node',
                        title: 'edit selected nodes',
                        selector: 'node',
                        onClickFunction: function (event) {
                            graphPage.layoutEditor.nodeEditor.open(cy.collection(cy.elements(':selected')).add(event.cyTarget).select());
                        },
                        hasTrailingDivider: true
                    },
                    {
                        id: 'select-all-nodes',
                        title: 'select all nodes',
                        selector: 'node',
                        show: true,
                        onClickFunction: function (event) {
                            selectAllOfTheSameType(event.cyTarget);
                        }
                    },
                    {
                        id: 'unselect-all-nodes',
                        title: 'unselect all nodes',
                        selector: 'node',
                        show: true,
                        onClickFunction: function (event) {
                            unselectAllOfTheSameType(event.cyTarget);
                        }
                    },
                    {
                        id: 'select-all-edges',
                        title: 'select all edges',
                        selector: 'edge',
                        show: true,
                        onClickFunction: function (event) {
                            selectAllOfTheSameType(event.cyTarget);
                        }
                    },
                    {
                        id: 'unselect-all-edges',
                        title: 'unselect all edges',
                        selector: 'edge',
                        show: true,
                        onClickFunction: function (event) {
                            unselectAllOfTheSameType(event.cyTarget);
                        }
                    }
                ]
            });
        }
    },
    getNodePositions: function (cy) {
        /*
         *  gets location of all the nodes so that it can be save later.
         *  cy: cytoscape graph object
         */
        var nodes = cy.elements('node');
        var layout = {};
        for (var i = 0; i < Object.keys(nodes).length - 2; i++) {
            layout[nodes[i]._private.data.id] = {
                'x': nodes[i]._private.position.x,
                'y': nodes[i]._private.position.y
            };
        }
        return layout;
    },
    getStylesheet: function (cy) {
        /*
         *  gets stylesheet for the graph.
         *  
         *  cy: cytoscape graph object
         */

        return _.map(cy.elements(), function (elem) {
            return {
                'selector': elem.isNode() ? _.template("node[name='<%= name %>']")({'name': elem.data('name')}) : _.template("edge[name='<%= name %>']")({'name': elem.data('name')}),
                'style': _.omitBy(_.mapValues(elem._private.style, function (style) {
                    return style ? style['strValue'] : undefined
                }), _.isNil)
            }

        });

    },
    export: function (cy, format, filename) {
        filename = filename ? filename : 'graph';
        var file = (format === 'jpg') ? cy.jpg({'full': true}) : (format === 'png' ? cy.png({'full': true}) : "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
            'graph': cy.json()['elements'],
            'metadata': graph_json['metadata']
        }, null, 4)));
        var link =  $('<a>').attr('href', file).attr('download', filename + '.' + format);
        $('body').append(link);
        link.get(0).click();
        link.get(0).remove();
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
            .update(); // update the elements in the graph with the new style

    },
    showGraphInformation: function (cy) {
        /*
         Function to Show information about the graph that the layout editor hid from the users.
         */
        cy.style()
            .selector('node').style({
                'font-size': "16px"
            })
            .update();
        console.log('done');
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