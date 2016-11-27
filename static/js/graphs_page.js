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
        getByID: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        update: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.graphs.ENDPOINT + id, data, successCallback, errorCallback)
        },
        delete: function (id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback)
        }
    },
    jsonRequest: function (method, url, data, successCallback, errorCallback) {
        $.ajax({
            headers: {
                'Accept': 'application/json'
            },
            method: method,
            data: data,
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
    init: function () {
        /**
         * This function is called to setup the graph page.
         * It will initialize all the event listeners.
         */

        graphPage.cyGraph = cytoscape({
            container: document.getElementById('cyGraphContainer'),
            boxSelectionEnabled: true,
            autounselectify: false,
            elements: graph_json['graph'],
            layout: {
                name: 'random'
            },
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
                    'background-opacity': 'data(background_opacity)'
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
        });

    }

}