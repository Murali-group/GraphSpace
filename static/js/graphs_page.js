/**
 * Created by adb on 25/11/16.
 */

var apis = {
  graphs: {
    ENDPOINT: '/ajax/graphs/',
    search: function ( queryParams, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'POST', apis.graphs.ENDPOINT + 'advanced_search' + '?' + $.param( queryParams ), data, successCallback, errorCallback )
    },
    get: function ( data, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.graphs.ENDPOINT, data, successCallback, errorCallback )
    },
    add: function ( data, successCallback, errorCallback ) {
      apis.jsonRequest( 'POST', apis.graphs.ENDPOINT, data, successCallback, errorCallback )
    },
    getByID: function ( id, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback )
    },
    update: function ( id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'PUT', apis.graphs.ENDPOINT + id, data, successCallback, errorCallback )
    },
    delete: function ( id, successCallback, errorCallback ) {
      apis.jsonRequest( 'DELETE', apis.graphs.ENDPOINT + id, undefined, successCallback, errorCallback )
    },
    getSharedGroups: function ( id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.graphs.ENDPOINT + id + '/groups', data, successCallback, errorCallback )
    },
    shareGraph: function ( id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'POST', apis.graphs.ENDPOINT + id + '/groups', data, successCallback, errorCallback )
    },
    unshareGraph: function ( graph_id, group_id, successCallback, errorCallback ) {
      apis.jsonRequest( 'DELETE', apis.graphs.ENDPOINT + graph_id + '/groups/' + group_id, undefined, successCallback, errorCallback )
    }
  },
  nodes: {
    ENDPOINT: _.template( '/ajax/graphs/<%= graph_id %>/nodes/' ),
    get: function ( graph_id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.nodes.ENDPOINT( {
        'graph_id': graph_id
      } ), data, successCallback, errorCallback )
    },
  },
  edges: {
    ENDPOINT: _.template( '/ajax/graphs/<%= graph_id %>/edges/' ),
    get: function ( graph_id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.edges.ENDPOINT( {
        'graph_id': graph_id
      } ), data, successCallback, errorCallback )
    },
  },
  layouts: {
    ENDPOINT: _.template( '/ajax/graphs/<%= graph_id %>/layouts/' ),
    get: function ( graph_id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.layouts.ENDPOINT( {
        'graph_id': graph_id
      } ), data, successCallback, errorCallback )
    },
    add: function ( graph_id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'POST', apis.layouts.ENDPOINT( {
        'graph_id': graph_id
      } ), data, successCallback, errorCallback )
    },
    getByID: function ( graph_id, layout_id, successCallback, errorCallback ) {
      apis.jsonRequest( 'GET', apis.layouts.ENDPOINT( {
        'graph_id': graph_id
      } ) + layout_id, undefined, successCallback, errorCallback )
    },
    update: function ( graph_id, layout_id, data, successCallback, errorCallback ) {
      apis.jsonRequest( 'PUT', apis.layouts.ENDPOINT( {
        'graph_id': graph_id
      } ) + layout_id, data, successCallback, errorCallback )
    },
    delete: function ( graph_id, layout_id, successCallback, errorCallback ) {
      apis.jsonRequest( 'DELETE', apis.layouts.ENDPOINT( {
        'graph_id': graph_id
      } ) + layout_id, undefined, successCallback, errorCallback )
    }
  },
  logging: {
    ENDPOINT: _.template( 'http://<%= hostname %>:9200/layouts/action' ),
    add: function ( data, successCallback, errorCallback ) {
      $.ajax( {
        headers: {
          'Accept': 'application/json'
        },
        method: 'POST',
        data: JSON.stringify( data ),
        url: apis.logging.ENDPOINT( {
          'hostname': 'graphspace.org'
        } ),
        headers: {
          'Authorization': 'Basic Z3JhcGhjcm93ZDpncmFwaGNyb3dk'
        },
        success: successCallback,
        error: errorCallback
      } );

    }
  },
  jsonRequest: function ( method, url, data, successCallback, errorCallback ) {
    $.ajax( {
      headers: {
        'Accept': 'application/json'
      },
      method: method,
      data: method == 'GET' ? data : JSON.stringify( data ),
      url: url,
      success: successCallback,
      error: errorCallback
    } );
  }
}; //var api ends

var graphsPage = {
  init: function () {
    /**
     * This function is called to setup the graphs page.
     * It will initialize all the event listeners.
     */
    console.log( 'Loading Graphs Page....' );

    $( '#ok' ).click( function () {
      $.xhrPool.abortAll();
      $( 'table' ).bootstrapTable( 'refresh' );
    } );

    $( '#clear' ).click( function () {
      graphsPage.searchBar.val( null ).trigger( "change" );
    } );

    $( 'input.graphs-table-search' ).keypress( function ( e ) {
      if ( e.which == 13 ) {
        $( "#ok" ).trigger( "click" );
        return false;
      }
    } );

    graphsPage.searchBar = $( ".graph-search" ).select2( {
      tags: true,
      tokenSeparators: [ ',', ' ', '-' ],
      placeholder: "Search for networks"
    } );

    graphsPage.searchBar.on( 'change', function ( evt ) {
      var query = graphsPage.searchBar.val() && graphsPage.searchBar.val().length > 0 ? '?query=' + graphsPage.searchBar.val() : '';
      window.history.pushState( 'query', 'Graphs Page', window.location.origin + window.location.pathname + query );
      $( "#ok" ).trigger( "click" );
    } );

    if ( utils.getURLParameter( 'query' ) && utils.getURLParameter( 'query' ) != "" ) {
      _.each( _.split( utils.getURLParameter( 'query' ), ',' ), function ( val ) {
        graphsPage.searchBar.append( new Option( val, val, true, true ) ).trigger( 'change' );
      } );
    }

    if ( utils.getURLParameter( 'tags' ) && utils.getURLParameter( 'tags' ) != "" ) {
      _.each( _.split( utils.getURLParameter( 'tags' ), ',' ), function ( val ) {
        graphsPage.searchBar.append( new Option( 'tags:' + val, 'tags:' + val, true, true ) ).trigger( 'change' );
      } );
    }

    $( '#ConfirmRemoveGraphBtn' ).click( graphsPage.graphsTable.onRemoveGraphConfirm );

    utils.initializeTabs();
  },
  searchBar: null,
  advancedQueryBuilder: {
    computeQuery: function () {
      var query = $.extend( true, {}, searchQueryTemplateJSON );
      var search = $( '.graph-search' ).val() ? $( '.graph-search' ).val() : [];

      if ( search.length > 0 ) {

        nodeQuery = _.map( _.filter( _.pull( search, '' ), function ( s ) {
          return s.indexOf( ':' ) === -1;
        } ), function ( term ) {
          var temp = _.template( 'object_elements.object_nodes.object_data.string_name:*<%= node %>* OR object_elements.object_nodes.object_data.string_label:*<%= node %>* OR object_elements.object_nodes.object_data.string_aliases:*<%= node %>*' )
          return '(' + temp( {
            'node': term
          } ) + ')';
        } );

        networkQuery = _.flatten( _.map( search, function ( term ) {
          if ( term.indexOf( ':' ) === -1 ) {
            var temp = _.template( 'object_data.string_name:*<%= name %>*' );
            return '(' + temp( {
              'name': term
            } ) + ')';
          } else {
            var attr = term.split( ':' )[ 0 ];
            var val = term.split( ':' )[ 1 ];
            return _.split( val, '-' ).map( function ( n ) {
              return '(object_data.string_' + attr + ':*' + n + '*)';
            } );
          }
        } ) );

        console.log( networkQuery );

        query.query.bool.should.push( {
          "query_string": {
            "query": nodeQuery.join( ' AND ' ),
            "analyze_wildcard": true
          }
        } );
        query.query.bool.should.push( {
          "query_string": {
            "query": networkQuery.join( ' AND ' ),
            "analyze_wildcard": true
          }
        } );
      }

      return ( search.length > 0 ) ? query : null;
    }
  },
  graphsTable: {
    searchTag: function ( e ) {
      searchedTag = 'tags:' + $( e ).text();
      search = _.uniq( _.pull( graphsPage.searchBar.val(), '', undefined ) );

      if ( _.indexOf( search, searchedTag ) == -1 ) {
        search.push( searchedTag );

        if ( search && search.length > 0 ) {
          graphsPage.searchBar.html( '' );
          _.each( search, function ( term ) {
            graphsPage.searchBar.append( new Option( term, term, true, true ) );
          } );
          graphsPage.searchBar.trigger( 'change' );
        }
      }
    },
    graphNameFormatter: function ( value, row ) {
      var queryString = ( graphsPage.searchBar.val() && graphsPage.searchBar.val().length > 0 ) ? '?query=' + _.join( graphsPage.searchBar.val(), ',' ) : '';
      return $( '<a>' ).attr( 'href', '/graphs/' + row.id + queryString ).text( value )[ 0 ].outerHTML;
    },
    tagsFormatter: function ( value, row ) {
      links = [];
      links = _.map( row.tags, function ( tag ) {
        return $( '<a>' ).attr( 'href', '#' ).html( $( '<span>' ).attr( 'class', 'label label-info tag-btn' ).attr( 'onclick', 'graphsPage.graphsTable.searchTag(this);' ).text( tag )[ 0 ] )[ 0 ].outerHTML + '&nbsp;';
      } );
      return links.join( '' );
    },
    ownerEmailFormatter: function ( value, row ) {
      if ( _.startsWith( row.owner_email, 'public_user_' ) ) {
        return "Anonymous User";
      } else {
        return row.owner_email;
      }
    },
    visibilityFormatter: function ( value, row ) {
      if ( row.is_public === 1 ) {
        return "<i class='fa fa-globe fa-lg'></i> Public";
      } else {
        return "<i class='fa fa-lock fa-lg'></i> Private";
      }
    },
    queryParams: function ( params ) {

      var search = $( '.graph-search' ).val() ? $( '.graph-search' ).val() : [];

      var query = graphsPage.advancedQueryBuilder.computeQuery();
      if ( query ) {
        params[ 'query' ] = query;
      } else {
        params[ 'query' ] = {};
      }
      return params;
    },
    operationsFormatter: function ( value, row, index ) {
      if ( row.owner_email === $( '#UserEmail' ).val() ) {
        return [
          '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Remove">',
          'Remove <i class="glyphicon glyphicon-remove"></i>',
          '</a>'
        ].join( '' );
      } else {
        return '';
      }
    },
    operationEvents: {
      'click .remove': function ( e, value, row, index ) {
        $( '#deleteGraphModal' ).data( 'graph-id', row.id ).modal( 'show' );
      }
    },
    onRemoveGraphConfirm: function ( e ) {
      e.preventDefault();
      $( 'table' ).bootstrapTable( 'remove', {
        field: 'id',
        values: [ $( '#deleteGraphModal' ).data( 'graph-id' ) ]
      } );
      $( '#deleteGraphModal' ).modal( 'hide' );
      $.notify( {
        message: 'Submitted the request to delete the graph. The graph will be deleted in sometime.'
      }, {
        type: 'info'
      } );

      apis.graphs.delete( $( '#deleteGraphModal' ).data( 'graph-id' ),
        successCallback = function ( response ) {
          // This method is called when graph is successfully deleted.
          // The entry from the table is deleted.
          $.notify( {
            message: 'Successfully deleted the graph with id=' + $( '#deleteGraphModal' ).data( 'graph-id' )
          }, {
            type: 'success'
          } );
        },
        errorCallback = function ( xhr, status, errorThrown ) {
          // This method is called when  error occurs while deleting group_to_graph relationship.
          $.notify( {
            message: xhr.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    },
  },
  sharedGraphsTable: {
    getGraphsByGroupMember: function ( params ) {
      /**
       * This is the custom ajax request used to load graphs in sharedGraphsTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */

      $( '#SharedGraphsTable' ).bootstrapTable( 'showLoading' );
      $( '#sharedGraphsTotal' ).html( '<i class="fa fa-refresh fa-spin fa fa-fw"></i>' );

      query = params.data[ 'query' ]
      delete params.data.query;

      params.data[ "member_email" ] = $( '#UserEmail' ).val();

      apis.graphs.search( params.data, query,
        successCallback = function ( response ) {
          // This method is called when graphs are successfully fetched.
          $( '#SharedGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.success( response );
          $( '#sharedGraphsTotal' ).text( response.total );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching graphs.
          $( '#SharedGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.error( 'Error' );
        }
      );
    },
  },
  publicGraphsTable: {
    getPublicGraphs: function ( params ) {
      /**
       * This is the custom ajax request used to load graphs in publicGraphsTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */
      $( '#PublicGraphsTable' ).bootstrapTable( 'showLoading' );
      $( '#publicGraphsTotal' ).html( '<i class="fa fa-refresh fa-spin fa fa-fw"></i>' );

      query = params.data[ 'query' ]
      delete params.data.query;

      params.data[ "is_public" ] = 1;


      apis.graphs.search( params.data, query,
        successCallback = function ( response ) {
          // This method is called when graphs are successfully fetched.
          $( '#PublicGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.success( response );
          $( '#publicGraphsTotal' ).text( response.total );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching graphs.
          $( '#PublicGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.error( 'Error' );
        }
      );
    },
  },
  ownedGraphsTable: {
    getGraphsByOwner: function ( params ) {
      /**
       * This is the custom ajax request used to load graphs in ownedGraphsTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */
      $( '#OwnedGraphsTable' ).bootstrapTable( 'showLoading' );

      $( '#ownedGraphsTotal' ).html( '<i class="fa fa-refresh fa-spin fa fa-fw"></i>' );

      query = params.data[ 'query' ]
      delete params.data.query;

      params.data[ "owner_email" ] = $( '#UserEmail' ).val();

      apis.graphs.search( params.data, query,
        successCallback = function ( response ) {
          // This method is called when graphs are successfully fetched.
          $( '#OwnedGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.success( response );
          $( '#ownedGraphsTotal' ).text( response.total );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching graphs.
          $( '#OwnedGraphsTable' ).bootstrapTable( 'hideLoading' );
          params.error( 'Error' );
        }
      );
    }
  },
}; //var graph ends

var uploadGraphPage = {
  init: function () {
    /**
     * This function is called to setup the upload graph page.
     * It will initialize all the event listeners.
     */

    $( '.browse' ).click( function ( e ) {
      e.preventDefault();
      var file = $( this ).parent().parent().find( '.file' );
      file.trigger( 'click' );
    } );

    $( '.file' ).change( function () {
      $( this ).parent().find( '.form-control' ).val( $( this ).val().replace( /C:\\fakepath\\/i, '' ) );
    } );

    //Upload the graph
    $( "#UploadGraphBtn" ).click( function ( e ) {
      e.preventDefault();

      if ( _.trim( $( "#GraphNameInput" ).val() ).length == 0 ) {
        return $.notify( {
          message: 'Please enter graph name!',
        }, {
          type: 'warning'
        } );
      } else if ( _.trim( $( "#GraphFileInput" ).val() ).length == 0 ) {
        return $.notify( {
          message: 'Please upload a valid file!',
        }, {
          type: 'warning'
        } );
      } else {
        $( this ).button( 'loading' );
        $( "#UploadGraphForm" ).submit();
      }

    } );

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

    graphPage.legend.init( style_json );

    graphPage.cyGraph.panzoom();

        //Update the parent node array
    graphPage.cyGraph.nodes().forEach(function (ele) {
            if (ele.data().parent != null && parent_nodes.indexOf(ele.data().parent) == -1)
            {
                parent_nodes.push(ele.data().parent);
            }

    });

    utils.initializeTabs();

    $( '#saveOnExitLayoutBtn' ).click( function () {
      graphPage.cyGraph.contextMenus( 'get' ).destroy(); // Destroys the cytocscape context menu extension instance.

      cytoscapeGraph.showGraphInformation( graphPage.cyGraph );
      // display node data as a popup
      graphPage.cyGraph.unbind( 'tap' ).on( 'tap', graphPage.onTapGraphElement );
      graphPage.saveLayout( $( '#saveOnExitLayoutNameInput' ).val(), '#saveOnExitLayoutModal' );
    } );

    $( '#saveLayoutBtn' ).click( function () {
      graphPage.saveLayout( $( '#saveLayoutNameInput' ).val(), '#saveLayoutModal' );
    } );

    $( '#layoutEditorBtn' ).click( function () {
      graphPage.layoutEditor.init();
    } );

    $( '#exitLayoutEditorBtn' ).click( function () {
      $( '#exitLayoutBtn' ).removeClass( 'hidden' );
      $( '#saveOnExitLayoutModal' ).modal( 'show' );
    } );

    $( '#saveLayoutEditorBtn' ).click( function () {
      $( '#exitLayoutBtn' ).removeClass( 'hidden' );
      $( '#saveLayoutModal' ).modal( 'show' );
    } );

    $( '#exitLayoutBtn' ).click( function () {
      graphPage.cyGraph.contextMenus( 'get' ).destroy(); // Destroys the cytocscape context menu extension instance.

      cytoscapeGraph.showGraphInformation( graphPage.cyGraph );
      // display node data as a popup
      graphPage.cyGraph.unbind( 'tap' ).on( 'tap', graphPage.onTapGraphElement );
    } );

    $( '#ConfirmRemoveLayoutBtn' ).click( graphPage.layoutsTable.onConfirmRemoveGraph );
    $( '#ConfirmUpdateLayoutBtn' ).click( graphPage.layoutsTable.onConfirmUpdateGraph );

    this.filterNodesEdges.init();
    this.colaLayoutWidget.init();

    if ( window.location.hash == '#layoutEditor' ) {
      $( '#layoutEditorBtn' ).trigger( 'click' );
    }

    if ( window.location.hash == '#legendEditor' ) {
      $( '#legendEditorBtn' ).trigger( 'click' );
    }

    if ( window.location.hash == '#graph_details_tab' ) {
      $( '#graphDetailsTabBtn' ).trigger( 'click' );
    }

    if ( !_.isEmpty( utils.getURLParameter( 'auto_layout' ) ) ) {
      graphPage.applyAutoLayout( utils.getURLParameter( 'auto_layout' ) );
    } else if ( !_.isEmpty( utils.getURLParameter( 'user_layout' ) ) ) {
      graphPage.applyUserLayout( utils.getURLParameter( 'user_layout' ) );
    }

    $( '#graphVisualizationTabBtn' ).click( function ( e ) {
      window.setTimeout( function () {
        $( '#cyGraphContainer' ).css( 'height', '99%' );
      }, 100 );
    } );

    if ( utils.getURLParameter( 'query' ) ) {
      var searchquery = _.map( _.filter( _.pull( _.split( _.trim( utils.getURLParameter( 'query' ) ), ',' ), '' ), function ( s ) {
        return s.indexOf( ':' ) === -1;
      } ), function ( str ) {
        return _.trim( str );
      } ).join( ',' );

      $( '#inputSearchEdgesAndNodes' ).val( searchquery ).trigger( 'onkeyup' );
    }


    graphPage.defaultLayoutWidget.init();
  },
  export: function ( format ) {
    cytoscapeGraph.export( graphPage.cyGraph, format, $( '#GraphName' ).val() );
  },
  applyAutoLayout: function ( layout_id ) {
    graphPage.applyLayout( cytoscapeGraph.getAutomaticLayoutSettings( layout_id ) );
    console.log( "after applying layout" );
    window.history.pushState( 'auto-layout', 'Graph Page', window.location.origin + window.location.pathname + '?auto_layout=' + layout_id );
    graphPage.defaultLayoutWidget.init( 0 );
  },
  applyUserLayout: function ( layout_id ) {
    apis.layouts.getByID( $( '#GraphID' ).val(), layout_id,
      successCallback = function ( response ) {
        graphPage.applyLayoutStyle( JSON.parse( response[ 'style_json' ] ) );
        graphPage.applyLayout( {
          name: 'preset',
          positions: JSON.parse( response[ 'positions_json' ] )
        } );
        if ( 'legend' in JSON.parse( response[ 'style_json' ] ) ) {
          graphPage.legend.currentLegendJSON[ 'legend' ] = JSON.parse( response[ 'style_json' ] )[ 'legend' ];
          if ( graphPage.legend.cyLegend ) {
            graphPage.legend.cyLegend.destroy();
            graphPage.legend.resizeLegendInterfaceHeight( "0px" );
          }
          graphPage.legend.cyLegend = graphPage.legend.constructLegend();
        }
        window.history.pushState( 'user-layout', 'Graph Page', window.location.origin + window.location.pathname + '?user_layout=' + layout_id );
        graphPage.defaultLayoutWidget.init( response[ 'is_shared' ] );
      },
      errorCallback = function ( xhr, status, errorThrown ) {
        // This method is called when  error occurs while deleting group_to_graph relationship.
        $.notify( {
          message: "You are not authorized to access this layout, create an account and contact resource's owner for permission to access this layout."
        }, {
          type: 'danger'
        } );
      } );
  },
  onSelectLayoutBtnClick: function ( e ) {
    if ( $( e ).hasClass( 'auto-layout' ) ) {
      graphPage.applyAutoLayout( $( e ).data( 'layout-id' ) );
    } else {
      graphPage.applyUserLayout( $( e ).data( 'layout-id' ) );
    }
  },
  applyLayoutStyle: function ( layoutStyle ) {
    layoutStyle = _.map( cytoscapeGraph.parseStylesheet( layoutStyle ), function ( elemStyle ) {
      elem = graphPage.cyGraph.elements( elemStyle[ 'selector' ] );
      if ( elem.isNode() ) {
        return {
          'selector': elemStyle[ 'selector' ],
          'style': graphPage.getGraphSpaceNodeStyle( elemStyle[ 'style' ], elem.data() )
        }
      } else {
        return {
          'selector': elemStyle[ 'selector' ],
          'style': graphPage.getGraphSpaceEdgeStyle( elemStyle[ 'style' ], elem.data() )
        }
      }
    } );
    graphPage.cyGraph.style().fromJson( _.concat( defaultStylesheet, layoutStyle, selectedElementsStylesheet ) ).update();
  },
  applyLayout: function ( layoutID ) {
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
    if ( isArray( layoutID.positions ) ) {
      var corrected_positions = {};
      _.forEach( layoutID.positions, function ( node ) {
        corrected_positions[ node.id ] = node;
      } );
      layoutID.positions = corrected_positions;
    }
    graphPage.cyGraph.layout( layoutID );

  },
  saveLayout: function ( layoutName, modalNameId, callback ) {
    graphPage.cyGraph.elements().unselect();

    if ( _.trim( layoutName ).length === 0 ) {
      return $.notify( {
        message: 'Please enter a valid layout name!',
      }, {
        type: 'warning'
      } );
    } else {
      if ( graphPage.layoutEditor.undoRedoManager ) {
        _.each( graphPage.layoutEditor.undoRedoManager.state, function ( action, i ) {
          if ( !_.isArray( action[ 'data' ][ 'selected_elements' ] ) ) {
            action[ 'data' ][ 'selected_elements' ] = action[ 'data' ][ 'selected_elements' ].jsons();
          }
          // Uncomment the code after setting up the elastic server.
          console.debug( action[ 'data' ][ 'selected_elements' ] );

          apis.logging.add( {
              'layout_name': layoutName,
              'graph_id': $( '#GraphID' ).val(),
              'graph_name': $( '#GraphName' ).val(),
              'user_email': $( '#UserEmail' ).val(),
              'action': action,
              'step': i
            },
            successCallback = function ( response ) {
              console.log( response );
            },
            errorCallback = function ( xhr, status, errorThrown ) {
              // This method is called when  error occurs while deleting group_to_graph relationship.
              console.log( xhr.responseJSON.error_message );
            } )
        } );
      }

      positions_json = cytoscapeGraph.getNodePositions( graphPage.cyGraph );
      cyGraph_style_json = cytoscapeGraph.getStylesheet( graphPage.cyGraph );
      apis.layouts.add( $( '#GraphID' ).val(), {
          "owner_email": $( '#UserEmail' ).val(),
          "graph_id": $( '#GraphID' ).val(),
          "name": layoutName,
          "positions_json": positions_json,
          "style_json": {
            "format_version": "1.0",
            "generated_by": "graphspace-2.0.0",
            "target_cytoscapejs_version": "~2.7",
            "style": cyGraph_style_json,
            "legend": style_json[ 'legend' ]
          }
        },
        successCallback = function ( response ) {
          $( modalNameId ).modal( 'toggle' );
          $( '#PrivateLayoutsTable' ).bootstrapTable( 'refresh' );
          $( '#SharedLayoutsTable' ).bootstrapTable( 'refresh' );
          $( 'table' ).bootstrapTable( 'refresh' );
          if ( typeof callback === 'function' ) {
            callback( response.id );
          };

        },
        errorCallback = function ( response ) {
          // This method is called when  error occurs while deleting group_to_graph relationship.
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );

    }

  },
  addLayoutBtns: function ( layout, domID ) {
    // domID: ID of the dom in which the layout btns will be inserted.
    $( '#' + domID ).append(
      $( '<li>', {
        class: "margin-bottom-2"
      } ).append(
        $( '<button>', {
          'type': "button",
          'class': "btn btn-xs btn-default gs-full-width select-layout-btn user-layout",
          'data-layout-id': layout.id,
          'onclick': "graphPage.onSelectLayoutBtnClick(this)"
        } ).html( '<b>' + layout.name + '</b> <br> created by ' + layout.owner_email )
      )
    );
  },
  onShareGraphWithPublicBtn: function ( e, graph_id ) {

    apis.graphs.update( graph_id, {
        'is_public': 1
      },
      successCallback = function ( response ) {
        // This method is called when group_to_graph relationship is successfully deleted.
        // The entry from the table is deleted.
        $( e ).parent().find( '.unshare-graph-btn' ).removeClass( 'hidden' );
        $( e ).addClass( 'hidden' );

      },
      errorCallback = function ( xhr, status, errorThrown ) {
        // This method is called when  error occurs while deleting group_to_graph relationship.
        $.notify( {
          message: xhr.responseJSON.error_message
        }, {
          type: 'danger'
        } );

      } );


  },
  onUnshareGraphWithPublicBtn: function ( e, graph_id ) {

    apis.graphs.update( graph_id, {
        'is_public': 0
      },
      successCallback = function ( response ) {
        // This method is called when group_to_graph relationship is successfully deleted.
        // The entry from the table is deleted.
        $( e ).parent().find( '.share-graph-btn' ).removeClass( 'hidden' );
        $( e ).addClass( 'hidden' );

      },
      errorCallback = function ( xhr, status, errorThrown ) {
        // This method is called when  error occurs while deleting group_to_graph relationship.
        $.notify( {
          message: xhr.responseJSON.error_message
        }, {
          type: 'danger'
        } );
      } );


  },
  onShareGraphWithGroupBtn: function ( e, graph_id, group_id ) {

    apis.graphs.shareGraph( graph_id, {
        'group_id': group_id
      },
      successCallback = function ( response ) {
        // This method is called when group_to_graph relationship is successfully deleted.
        // The entry from the table is deleted.
        $( e ).parent().find( '.unshare-graph-btn' ).removeClass( 'hidden' );
        $( e ).addClass( 'hidden' );

      },
      errorCallback = function ( xhr, status, errorThrown ) {
        // This method is called when  error occurs while deleting group_to_graph relationship.
        $.notify( {
          message: xhr.responseJSON.error_message
        }, {
          type: 'danger'
        } );
      } );


  },
  onUnshareGraphWithGroupBtn: function ( e, graph_id, group_id ) {

    apis.graphs.unshareGraph( graph_id, group_id,
      successCallback = function ( response ) {
        // This method is called when group_to_graph relationship is successfully deleted.
        // The entry from the table is deleted.
        $( e ).parent().find( '.share-graph-btn' ).removeClass( 'hidden' );
        $( e ).addClass( 'hidden' );

      },
      errorCallback = function ( xhr, status, errorThrown ) {
        // This method is called when  error occurs while deleting group_to_graph relationship.
        $.notify( {
          message: xhr.responseJSON.error_message
        }, {
          type: 'danger'
        } );
      } );
  },
  onInputSearchEdgesAndNodes: function ( e ) {
    clearTimeout( graphPage.timeout );

    // Unselecting all elements before selecting searched elements.
    _.each( graphPage.cyGraph.elements(), function ( element ) {
      element.unselect();
    } );

    graphPage.timeout = setTimeout( function () { // Wait for User to Stop Typing, Using JavaScript

      nodes = _.map( _.filter( _.pull( _.split( _.trim( $( e ).val() ), ',' ), '' ), function ( s ) {
        return s.indexOf( '::' ) === -1;
      } ), function ( str ) {
        //return '%' + _.trim(str) + '%';
        return _.trim( str );
      } );

      edges = _.map( _.filter( _.split( _.trim( $( e ).val() ), ',' ), function ( s ) {
        return s.indexOf( '::' ) !== -1;
      } ), function ( str ) {
        edge = _.split( str, '::' );
        return '%' + _.trim( edge[ 0 ] ) + '%:%' + _.trim( edge[ 1 ] ) + '%';
      } );

      var elementComparator = function ( dataValue, searchedValue ) {
        /*
         This function will return true if one of the following condition is true:
         1. If both values are strings and searchedValue is substring of dataValue.
         2. If dataValue is list of string and searchedValue is a substring of one of the strings in dataValue.
         3. If dataValue is a list of numbers and searchedValue is present in the list.
         4. _.isEqual(dataValue, searchedValue) -> This method supports comparing arrays, array buffers, booleans, date objects, error objects, maps, numbers, Object objects, regexes, sets, strings, symbols, and typed arrays.
         */
        if ( _.isNil( searchedValue ) || _.isEmpty( searchedValue ) ) {
          return false;
        }

        if ( _.isArrayLike( dataValue ) ) {
          if ( utils.isNumeric( searchedValue ) ) {
            return dataValue.indexOf( searchedValue ) !== -1;
          } else if ( _.isString( dataValue ) ) {
            return ( '' + dataValue ).toLowerCase().indexOf( searchedValue.toLowerCase() ) !== -1;
          } else {
            return dataValue.join( ' ' ).toLowerCase().indexOf( searchedValue.toLowerCase() ) !== -1;
          }
        } else {
          return _.isEqual( '' + dataValue, searchedValue );
        }
      };

      if ( _.trim( $( e ).val() ).length > 0 ) {
        if ( nodes.length > 0 ) {
          graphPage.cyGraph.nodes().forEach( function ( ele, i, eles ) {
            _.each( nodes, function ( node ) {
              //Check if the node component is not null and include the node string
              if ( node.indexOf( ':' ) === -1 && node.indexOf( '>' ) === -1 && node.indexOf( '<' ) === -1 && node.indexOf( '=' ) === -1 ) {
                if ( ( ele.data( 'name' ) && ele.data( 'name' ).toLowerCase().indexOf( node.toLowerCase() ) != -1 ) ||
                  ( ele.data( 'label' ) && ele.data( 'label' ).toLowerCase().indexOf( node.toLowerCase() ) != -1 ) ||
                  ( ele.data( 'aliases' ) && ( ele.data( 'aliases' ).join( ' ' ).toLowerCase().indexOf( node.toLowerCase() ) != -1 ) )
                ) {

                  ele.select();
                }
              } else if ( node.indexOf( '>' ) !== -1 || node.indexOf( '<' ) !== -1 || node.indexOf( '=' ) !== -1 ) {
                graphPage.cyGraph.nodes( "node[" + node + "]" ).select();
              } else {
                if ( _.isEqualWith( ele.data( node.split( ':' )[ 0 ] ), node.split( ':' )[ 1 ], elementComparator ) ) {
                  ele.select();
                }
              }
            } );
          } );

          //apis.nodes.get($('#GraphID').val(), {
          //        "names": nodes,
          //        "labels": nodes
          //    },
          //    successCallback = function (response) {
          //        _.each(response.nodes, function (node) {
          //            graphPage.cyGraph.nodes("[name = '" + node.name + "']").select();
          //        });
          //    },
          //    errorCallback = function (xhr, status, errorThrown) {
          //        $.notify({message: xhr.responseJSON.error_message}, {type: 'danger'});
          //    }
          //);
        }

        if ( edges.length > 0 ) {
          apis.edges.get( $( '#GraphID' ).val(), {
              "edges": edges
            },
            successCallback = function ( response ) {
              _.each( response.edges, function ( edge ) {
                graphPage.cyGraph.edges( "[name = '" + edge.name + "']" ).select();
              } );
            },
            errorCallback = function ( xhr, status, errorThrown ) {
              $.notify( {
                message: xhr.responseJSON.error_message
              }, {
                type: 'danger'
              } );
            }
          );
        }
      }
      graphPage.timeout = null;
    }, 250 );
  },
  onTapGraphElement: function ( evt ) {
    // get target
    var target = evt.cyTarget;
    // target some element other than background (node/edge)
    if ( target !== this ) {
      var popup = target._private.data.popup;

      //If there is no embedded content, don't display anything
      if ( popup == null || popup.length == 0 ) {
        return;
      }

      //Display embedded content if there is any
      if ( target._private.data.popup != null && target._private.data.popup.length > 0 ) {
        $( "#dialog" ).html( "<p>" + target._private.data.popup + "</p>" );
      }
      if ( target._private.group == 'edges' ) {
        $( '#dialog' ).dialog( 'option', 'title', target._private.data.source + "-" + target._private.data.target );
      } else {
        $( '#dialog' ).dialog( 'option', 'title', target.style( 'label' ) );
      }

      $( "#dialog" ).dialog( {
        'maxHeight': 500
      } );
      $( '#dialog' ).dialog( 'open' );

    }
  },
  getGraphSpaceNodeStyle: function ( nodeStyle, nodeData ) {
    /*
     This function will check if the style object has valid values and fix them otherwise.

     nodeStyle - JSON object of style attributes,
     */

    //VALUES CONSISTENT AS OF CYTOSCAPEJS 2.5.0
    //DONE TO SUPPORT OLD GRAPHS AND SETS A MINIMUM SETTINGS TO AT LEAST DISPLAY GRAPH IF USER
    //DOESN'T HAVE ANY OTHER SETTINGS TO ALTER HOW THE NODES IN GRAPH LOOKS
    var acceptedShapes = [ "rectangle", "roundrectangle", "ellipse", "triangle", "pentagon", "hexagon", "heptagon", "octagon", "star", "diamond", "vee", "rhomboid", "polygon" ];

    //If the node has a shape, make sure that shape is recognized by CytoscapeJS
    //Otherwise, make shape an ellipse
    if ( nodeStyle.hasOwnProperty( 'shape' ) == true && acceptedShapes.indexOf( nodeStyle[ 'shape' ].toLowerCase() ) == -1 ) {
      //TO SUPPORT OLD GRAPHS THAT HAD THESE SHAPES
      if ( nodeStyle[ 'shape' ].toLowerCase() == 'square' ) {
        nodeStyle[ 'shape' ] = "rectangle"
      }
    } else if ( nodeStyle[ 'shape' ] ) {
      nodeStyle[ 'shape' ] = nodeStyle[ 'shape' ].toLowerCase();
    }

    //Pick default color if nothing is provided
    if ( nodeStyle[ 'background-color' ] != undefined ) {
      var hexCode = colourNameToHex( nodeStyle[ 'background-color' ] );
      if ( hexCode != false ) {
        nodeStyle[ 'background-color' ] = hexCode;
      } else {
        if ( isHexaColor( addCharacterToHex( nodeStyle[ 'background-color' ] ) ) ) {
          nodeStyle[ 'background-color' ] = addCharacterToHex( nodeStyle[ 'background-color' ] );
        }
      }
    }

    return nodeStyle;
  },
  getNodeStylesheet: function ( nodeJSON ) {
    /**
     * get style properties of node objects and set style object to null because if set it will set unmutable style properties.
     */
    return _.map( nodeJSON, function ( node ) {
      return {
        'selector': _.template( "node[id='<%= id %>']" )( {
          'id': node[ 'data' ][ 'id' ]
        } ),
        'style': graphPage.getGraphSpaceNodeStyle( node[ 'style' ], node[ 'data' ] )
      };
    } );
  },
  getGraphSpaceEdgeStyle: function ( edgeStyle, edgeData ) {
    /*
     This function will check if the style object has valid values and fix them otherwise.

     edgeStyle - JSON object of style attributes,
     */

    //Color property maps to line_color
    //DONE TO SUPPORT OLD GRAPHS
    if ( edgeStyle.hasOwnProperty( 'color' ) ) {
      edgeStyle[ 'line-color' ] = edgeStyle[ 'color' ];
    }

    if ( edgeStyle[ 'line-color' ] != undefined ) {
      //Converts the line color into Hexadecimal so CytoscapeJS can user it
      var hexCode = colourNameToHex( edgeStyle[ 'line-color' ] );
      if ( hexCode != false ) {
        edgeStyle[ 'line-color' ] = hexCode;
      } else {
        if ( isHexaColor( addCharacterToHex( edgeStyle[ 'line-color' ] ) ) ) {
          edgeStyle[ 'line-color' ] = addCharacterToHex( edgeStyle[ 'line-color' ] );
        }
      }
    }
    //DONE TO SUPPORT OLD GRAPHS: If "directed" property is not there, edge is undirected, otherwise it is directed
    if ( edgeStyle[ 'target-arrow-shape' ] == undefined || ( edgeData[ 'directed' ] == false || edgeData[ 'directed' ] == 'false' ) ) {
      edgeStyle[ 'target-arrow-shape' ] = 'none';
    } else if ( edgeData[ 'directed' ] == true ) {
      edgeStyle[ 'target-arrow-shape' ] = 'triangle';
    }

    return edgeStyle;
  },
  getEdgeStylesheet: function ( edgeJSON ) {

    return _.map( edgeJSON, function ( edge ) {
      return {
        'selector': _.template( "edge[name='<%= name %>']" )( {
          'name': edge[ 'data' ][ 'name' ]
        } ),
        'style': graphPage.getGraphSpaceEdgeStyle( edge[ 'style' ], edge[ 'data' ] )
      };
    } );

  },
  contructCytoscapeGraph: function ( layout ) {
    if ( !layout ) {
      layout = {
        name: 'random',
        padding: 10,
        fit: true,
        animate: false
      };
    }

    graph_json[ 'elements' ][ 'nodes' ] = _.map( graph_json[ 'elements' ][ 'nodes' ], function ( node ) {
      var newNode = {
        "data": node[ 'data' ]
      };
      if ( 'position' in node ) {
        newNode[ 'position' ] = node[ 'position' ];
        layout = {
          name: 'preset'
        };
      }
      return newNode
    } );

    graph_json[ 'elements' ][ 'edges' ] = _.map( graph_json[ 'elements' ][ 'edges' ], function ( edge ) {
      return {
        "data": edge[ 'data' ]
      }
    } );

    return cytoscape( {
      container: document.getElementById( 'cyGraphContainer' ),
      boxSelectionEnabled: true,
      autounselectify: false,
      wheelSensitivity: 0.2,
      minZoom: 1e-2,
      maxZoom: 1e2,
      elements: graph_json[ 'elements' ],
      layout: layout,

      //Style properties of NODE body
      style: _.concat( defaultStylesheet, cytoscapeGraph.parseStylesheet( style_json ), selectedElementsStylesheet ),

      ready: function () {

        //setup popup dialog for displaying dialog when nodes/edges
        //are clicked for information.

        $( '#dialog' ).dialog( {
          autoOpen: false
        } );

        // display node data as a popup
        this.on( 'tap', graphPage.onTapGraphElement );

      }
    } );

  },
  defaultLayoutWidget: {
    init: function ( is_shared ) {
      if ( _.isNil( is_shared ) ) {
        $( '#setDefaultLayoutBtn' ).hide();
        $( '#removeDefaultLayoutBtn' ).hide();
      } else if ( utils.getURLParameter( 'auto_layout' ) ) {
        $( '#setDefaultLayoutBtn' ).show();
        $( '#removeDefaultLayoutBtn' ).hide();
      } else if ( utils.getURLParameter( 'user_layout' ) && utils.getURLParameter( 'user_layout' ) == default_layout_id ) {
        $( '#setDefaultLayoutBtn' ).hide();
        $( '#removeDefaultLayoutBtn' ).show();
      } else {
        $( '#setDefaultLayoutBtn' ).show();
        $( '#removeDefaultLayoutBtn' ).hide();
      }
    },
    setDefaultAutoLayoutBtn: function ( layout_id ) {
      apis.graphs.update( $( '#GraphID' ).val(), {
          'default_layout_id': layout_id
        },
        successCallback = function ( response ) {
          default_layout_id = layout_id;
          graphPage.defaultLayoutWidget.init( 1 );
          $( '#setDefaultLayoutBtn' ).hide();
          $( '#removeDefaultLayoutBtn' ).show();
        },
        errorCallback = function ( xhr, status, errorThrown ) {
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    },
    onSetDefaultLayoutBtn: function ( e ) {
      if ( utils.getURLParameter( 'auto_layout' ) ) {
        graphPage.saveLayout( utils.getURLParameter( 'auto_layout' ), utils.getURLParameter( 'auto_layout' ),
          graphPage.defaultLayoutWidget.setDefaultAutoLayoutBtn );

      } else {
        apis.graphs.update( $( '#GraphID' ).val(), {
            'default_layout_id': utils.getURLParameter( 'user_layout' )
          },
          successCallback = function ( response ) {
            default_layout_id = utils.getURLParameter( 'user_layout' );
            graphPage.defaultLayoutWidget.init( 1 );
          },
          errorCallback = function ( xhr, status, errorThrown ) {
            // This method is called when  error occurs while deleting group_to_graph relationship.
            $.notify( {
              message: response.responseJSON.error_message
            }, {
              type: 'danger'
            } );
          } );
      }
    },
    onRemoveDefaultLayoutBtn: function ( e ) {
      apis.graphs.update( $( '#GraphID' ).val(), {
          'default_layout_id': 0
        },
        successCallback = function ( response ) {
          default_layout_id = null;
          graphPage.defaultLayoutWidget.init( 1 );
        },
        errorCallback = function ( xhr, status, errorThrown ) {
          // This method is called when  error occurs while deleting group_to_graph relationship.
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    }
  },
  nodesTable: {
    getNodesByGraphID: function ( params ) {
      /**
       * This is the custom ajax request used to load nodes in nodesTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */

      if ( params.data[ "search" ] ) {
        params.data[ "names" ] = _.map( _.filter( _.split( params.data[ "search" ], ',' ), function ( s ) {
          return s.indexOf( ':' ) === -1;
        } ), function ( str ) {
          return '%' + str + '%';
        } );
        params.data[ "labels" ] = params.data[ "names" ];
      }

      params.data[ "graph_id" ] = $( '#GraphID' ).val();

      apis.nodes.get( $( '#GraphID' ).val(), params.data,
        successCallback = function ( response ) {
          // This method is called when nodes are successfully fetched.
          params.success( response );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching nodes.
          params.error( 'Error' );
        }
      );
    }
  },
  layoutsTable: {
    getPrivateLayoutsByGraphID: function ( params ) {
      /**
       * This is the custom ajax request used to load layouts in layoutsTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */

      if ( params.data[ "search" ] ) {
        params.data[ "name" ] = '%' + params.data[ "search" ] + '%';
      }

      params.data[ "is_shared" ] = 0;
      params.data[ "owner_email" ] = $( '#UserEmail' ).val();

      apis.layouts.get( $( '#GraphID' ).val(), params.data,
        successCallback = function ( response ) {
          // This method is called when layouts are successfully fetched.
          params.success( response );

          if ( response.total > 0 ) {
            $( '#selectSavedLayoutHeading' ).show();
          }
          $( '#userPrivateLayoutBtns' ).html( '' );
          _.each( response.layouts, function ( layout ) {
            graphPage.addLayoutBtns( layout, 'userPrivateLayoutBtns' );
          } );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching layouts.
          params.error( 'Error' );
        }
      );
    },
    getSharedLayoutsByGraphID: function ( params ) {
      /**
       * This is the custom ajax request used to load layouts in layoutsTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */

      if ( params.data[ "search" ] ) {
        params.data[ "name" ] = '%' + params.data[ "search" ] + '%';
      }

      params.data[ "is_shared" ] = 1;

      apis.layouts.get( $( '#GraphID' ).val(), params.data,
        successCallback = function ( response ) {
          // This method is called when layouts are successfully fetched.
          params.success( response );

          if ( response.total > 0 ) {
            $( '#selectSavedLayoutHeading' ).show();
          }
          $( '#userSharedLayoutBtns' ).html( '' );
          _.each( response.layouts, function ( layout ) {
            graphPage.addLayoutBtns( layout, 'userSharedLayoutBtns' );
          } );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching layouts.
          params.error( 'Error' );
        }
      );
    },
    operationsFormatter: function ( value, row, index ) {
      return [
        '<div class="pull-left"><strong>',
        row[ 'name' ],
        '</strong><br><small>', 'created by ', row[ 'owner_email' ], '</small>',
        '</div>',
        '<div class="pull-right margin-top-1">',
        row[ 'owner_email' ] == $( '#UserEmail' ).val() ? '&nbsp;<a class="edit-layout" href="javascript:void(0)" title="Rename Layout"> Rename <i class="fa fa-lg fa-pencil"></i> </a>&nbsp;' : '',
        row[ 'owner_email' ] == $( '#UserEmail' ).val() ? ( row[ 'is_shared' ] == 0 ? '&nbsp;<a class="share-layout" href="javascript:void(0)" title="Share Layout"> Share <i class="fa fa-lg fa-eye" aria-hidden="true"></i> </a>&nbsp;' : '<a class="unshare-layout" href="javascript:void(0)" title="Unshare Layout"> Unshare <i class="fa fa-lg fa-eye-slash" aria-hidden="true"></i> </a>&nbsp;' ) : '',
        row[ 'owner_email' ] == $( '#UserEmail' ).val() ? '&nbsp;<a class="delete-layout" href="javascript:void(0)" title="Delete Layout"> Delete <i class="fa fa-lg fa-trash"></i> </a>' : '',
        '</div>'
      ].join( '' );
    },
    operationEvents: {
      'click .delete-layout': function ( e, value, row, index ) {
        $( '#deleteLayoutModal' ).data( 'layout-id', row.id ).modal( 'show' );
      },
      'click .edit-layout': function ( e, value, row, index ) {
        $( '#editLayoutModal' ).data( 'layout-id', row.id ).modal( 'show' );
      },
      'click .share-layout': function ( e, value, row, index ) {
        apis.layouts.update( $( '#GraphID' ).val(), row.id, {
            'is_shared': 1
          },
          successCallback = function ( response ) {
            // This method is called when layout is successfully shared.
            // The entry from the table is deleted.
            $( '#SharedLayoutsTable' ).bootstrapTable( 'refresh' );
            $( '#PrivateLayoutsTable' ).bootstrapTable( 'refresh' );
          },
          errorCallback = function ( response ) {
            // This method is called when  error occurs while sharing layout.
            $.notify( {
              message: response.responseJSON.error_message
            }, {
              type: 'danger'
            } );
          } );
      },
      'click .unshare-layout': function ( e, value, row, index ) {
        apis.layouts.update( $( '#GraphID' ).val(), row.id, {
            'is_shared': 0
          },
          successCallback = function ( response ) {
            // This method is called when layout is successfully unshared.
            // The entry from the table is deleted.
            $( '#SharedLayoutsTable' ).bootstrapTable( 'refresh' );
            $( '#PrivateLayoutsTable' ).bootstrapTable( 'refresh' );
          },
          errorCallback = function ( response ) {
            // This method is called when  error occurs while unsharing layout.
            $.notify( {
              message: response.responseJSON.error_message
            }, {
              type: 'danger'
            } );
          } );
      }
    },
    onConfirmRemoveGraph: function ( e ) {
      e.preventDefault();
      apis.layouts.delete( $( '#GraphID' ).val(), $( '#deleteLayoutModal' ).data( 'layout-id' ),
        successCallback = function ( response ) {
          // This method is called when layout is successfully deleted.
          // The entry from the table is deleted.
          $( '#SharedLayoutsTable' ).bootstrapTable( 'refresh' );
          $( '#PrivateLayoutsTable' ).bootstrapTable( 'refresh' );
          $( '#deleteLayoutModal' ).modal( 'hide' );
        },
        errorCallback = function ( response ) {
          // This method is called when  error occurs while deleting layout.
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    },
    onConfirmUpdateGraph: function ( e ) {
      e.preventDefault();
      apis.layouts.update( $( '#GraphID' ).val(), $( '#editLayoutModal' ).data( 'layout-id' ), {
          "name": $( '#newlayoutNameInput' ).val()
        },
        successCallback = function ( response ) {
          // This method is called when layout is successfully updated.
          // The entry from the table is updated.
          $( '#SharedLayoutsTable' ).bootstrapTable( 'refresh' );
          $( '#PrivateLayoutsTable' ).bootstrapTable( 'refresh' );
          $( '#editLayoutModal' ).modal( 'hide' );
        },
        errorCallback = function ( response ) {
          // This method is called when  error occurs while updating layout.
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    }
  },
  edgesTable: {
    getEdgesByGraphID: function ( params ) {
      /**
       * This is the custom ajax request used to load nodes in edgesTable.
       *
       * params - query parameters for the ajax request.
       *          It contains parameters like limit, offset, search, sort, order.
       */

      if ( params.data[ "search" ] ) {
        params.data[ "names" ] = _.map( _.filter( _.split( params.data[ "search" ], ',' ), function ( s ) {
          return s.indexOf( ':' ) === -1;
        } ), function ( str ) {
          return '%' + str + '%';
        } );
        params.data[ "edges" ] = _.map( _.filter( _.split( params.data[ "search" ], ',' ), function ( s ) {
          return s.indexOf( ':' ) !== -1;
        } ), function ( str ) {
          edge = _.split( str, ':' );
          return '%' + edge[ 0 ] + '%:%' + edge[ 1 ] + '%';
        } );
      }

      params.data[ "graph_id" ] = $( '#GraphID' ).val();

      apis.edges.get( $( '#GraphID' ).val(), params.data,
        successCallback = function ( response ) {
          // This method is called when edges are successfully fetched.
          params.success( response );
        },
        errorCallback = function () {
          // This method is called when error occurs while fetching edges.
          params.error( 'Error' );
        }
      );
    }
  },
  layoutEditor: {
    original_opacity: {},
    undoRedoManager: null,
    init: function () {
      cytoscapeGraph.hideGraphInformation( graphPage.cyGraph );
      cytoscapeGraph.showGraphInformation( graphPage.cyGraph );

      cytoscapeGraph.contextMenu.init( graphPage.cyGraph );

      graphPage.layoutEditor.undoRedoManager = new UndoManager(
        onUndo = function ( item ) {
          if ( item ) {

            graphPage.cyGraph.elements( '*' ).unselect();
            graphPage.cyGraph.collection( item[ 'data' ][ 'selected_elements' ] ).select();

            cytoscapeGraph.applyStylesheet( graphPage.cyGraph, {
              'style': item[ 'data' ][ 'style' ]
            } );
            cytoscapeGraph.setRenderedNodePositions( graphPage.cyGraph, item[ 'data' ][ 'positions' ] );

            $( '#redoBtn' ).removeClass( 'disabled' );
          } else {
            $( '#undoBtn' ).addClass( 'disabled' );
          }
        },
        onRedo = function ( item ) {
          if ( item ) {
            graphPage.cyGraph.elements( '*' ).unselect();
            graphPage.cyGraph.collection( item[ 'data' ][ 'selected_elements' ] ).select();

            cytoscapeGraph.applyStylesheet( graphPage.cyGraph, {
              'style': item[ 'data' ][ 'style' ]
            } );
            cytoscapeGraph.setRenderedNodePositions( graphPage.cyGraph, item[ 'data' ][ 'positions' ] );

            $( '#undoBtn' ).removeClass( 'disabled' );
          } else {
            $( '#redoBtn' ).addClass( 'disabled' );
          }
        },
        onUpdate = function ( item ) {
          $( '#undoBtn' ).removeClass( 'disabled' );
        }
      );

      graphPage.layoutEditor.undoRedoManager.update( {
        'action_type': 'init',
        'data': {
          'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
          'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
          'selected_elements': graphPage.cyGraph.elements( ':selected' ),
          'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
        }
      } );

      graphPage.cyGraph.on( 'free', function ( e ) {

        var selected_elements = e.cyTarget.length > 1 ? graphPage.cyGraph.elements( ':selected' ) : e.cyTarget;
        graphPage.layoutEditor.undoRedoManager.update( {
          'action_type': 'move_node',
          'data': {
            'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
            'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
            'selected_elements': selected_elements,
            'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
          }
        } );
      } );

      // display node data as a popup
      graphPage.cyGraph.unbind( 'tap' ).on( 'tap', function ( evt ) {
        graphPage.layoutEditor.undoRedoManager.update( {
          'action_type': 'select_node',
          'data': {
            'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
            'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
            'selected_elements': graphPage.cyGraph.elements( ':selected' ),
            'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
          }
        } );
      } );

      $( '#undoBtn' ).addClass( 'disabled' );

      $( "#unselectBtn" ).click( function ( e ) {
        //Unselect all nodes/edges when button is clicked
        e.preventDefault();
        cytoscapeGraph.unSelectAllNodes( graphPage.cyGraph );
        cytoscapeGraph.unSelectAllEdges( graphPage.cyGraph );

        $( 'input:checkbox[name=colors]' ).each( function ( index ) {
          $( this ).prop( 'checked', false );
        } );
        $( 'input:checkbox[name=shapes]' ).each( function ( index ) {
          $( this ).prop( 'checked', false );
        } );

        graphPage.layoutEditor.undoRedoManager.update( {
          'action_type': 'unselect_all',
          'data': {
            'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
            'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
            'selected_elements': graphPage.cyGraph.elements( ':selected' ),
            'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
          }
        } );
      } );

      graphPage.layoutEditor.nodeSelector.init();

      $( '.arrange_nodes' ).click( function () {

        cytoscapeGraph.applyLayoutToCollection(
          graphPage.cyGraph,
          graphPage.cyGraph.collection( cytoscapeGraph.getAllSelectedNodes( graphPage.cyGraph ) ),
          $( this ).data( 'layout' )
        );

        graphPage.layoutEditor.undoRedoManager.update( {
          'action_type': 'arrange_nodes_' + $( this ).data( 'layout' ),
          'data': {
            'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
            'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
            'selected_elements': graphPage.cyGraph.elements( ':selected' ),
            'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
          }
        } );
      } );

      $( '#undoBtn' ).click( function () {
        graphPage.layoutEditor.undoRedoManager.undo();
      } );

      $( '#redoBtn' ).click( function () {
        graphPage.layoutEditor.undoRedoManager.redo();
      } );

      //cytoscapeGraph.hideGraphInformation(graphPage.cyGraph);

      $( "#startTourBtn" ).click( function () {
        var intro = introJs();
        intro.setOptions( {
          'scrollToElement': true,
          'showStepNumbers': false,
          'disableInteraction': true,
          'overlayOpacity': 0.5
        } );
        intro.start();
      } );

      $( '#toggleNodeLabels' ).prop( 'checked', true );

      $( '#toggleNodeLabels' ).change( function ( e ) {
        if ( $( '#toggleNodeLabels' ).is( ":checked" ) ) {
          cytoscapeGraph.showGraphInformation( graphPage.cyGraph );
        } else {
          cytoscapeGraph.hideGraphInformation( graphPage.cyGraph );
        }
      } );

      graphPage.cyGraph.elements().on( 'select, unselect', function () {
        if ( graphPage.cyGraph.nodes( ':selected' ).length > 0 ) {
          $( '#editSelectedNodesBtn' ).removeClass( 'disabled' );
        } else {
          $( '#editSelectedNodesBtn' ).addClass( 'disabled' );
        }

        if ( graphPage.cyGraph.edges( ':selected' ).length > 0 ) {
          $( '#editSelectedEdgesBtn' ).removeClass( 'disabled' );
        } else {
          $( '#editSelectedEdgesBtn' ).addClass( 'disabled' );
        }

      } );

      $( '#editSelectedNodesBtn' ).click( function () {
        graphPage.layoutEditor.nodeEditor.open( graphPage.cyGraph.collection( graphPage.cyGraph.nodes( ':selected' ) ) );
      } );

      $( '#editSelectedEdgesBtn' ).click( function () {
        graphPage.layoutEditor.edgeEditor.open( graphPage.cyGraph.collection( graphPage.cyGraph.edges( ':selected' ) ) );
      } );

      graphPage.layoutEditor.nodeEditor.init();
      graphPage.layoutEditor.edgeEditor.init();


      $( '#importCytoscapeStyleBtn' ).change( function ( e ) {
        console.log( $( '#importCytoscapeStyleBtn' ).files );
        var reader = new FileReader();
        reader.onload = function ( event ) {
          var obj = JSON.parse( event.target.result );

          if ( cytoscapeGraph.applyStylesheet( graphPage.cyGraph, obj ) ) {
            graphPage.layoutEditor.undoRedoManager.update( {
              'action_type': 'upload_style',
              'data': {
                'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
                'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
                'selected_elements': graphPage.cyGraph.elements( ':selected' ),
                'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
              }
            } );
          } else {
            graphPage.layoutEditor.undoRedoManager.undo();
          }
        };
        reader.readAsText( event.target.files[ 0 ] );
      } );

      $( "#nodeBackgroundColorPicker" ).colorpicker();
      $( "#edgeLineColorPicker" ).colorpicker();

    },
    nodeSelector: {
      init: function () {
        var colors = _.uniq( _.map( graphPage.cyGraph.nodes(), function ( node ) {
            //If the node is a parent node, do not include the color of the parent node to the color option
            if (parent_nodes.indexOf(node.data().id) == -1)
            {
                return node.style('background-color');
            }
        } ) );
        $( '#selectColors' ).html( '' );
        _.each( colors, function ( color ) {
            //We only set the color of nodes that aren't parent nodes
            if (color != null)
            {
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
            }
        } );

        var shapes = _.uniq( _.map( graphPage.cyGraph.nodes(), function ( node ) {
            //If the node is a parent node, do not inlcude the shape of parent node to the option
            if (parent_nodes.indexOf(node.data().id) == -1)
            {
                return node.style('shape');
            }
        } ) );
        $( '#selectShapes' ).html( '' );
        _.each( shapes, function ( shape ) {
            //Do not include the shape of parent node
            if (shape != null)
            {
                $('#selectShapes').append(
                    $('<label>', {class: "checkbox-inline"}).css({'margin-left': '10px'}).append(
                        $('<input>', {
                            id: shape,
                            type: 'checkbox',
                            value: shape,
                            name: 'shapes'
                        })).append(_.capitalize(shape)));
            }
        } );

        $( 'input:checkbox[name=shapes], input:checkbox[name=colors] ' ).change( function () {
          var selectedShapes = _.map( $( 'input:checkbox[name=shapes]:checked' ), function ( elem ) {
            return $( elem ).val();
          } );
          var selectedColors = _.map( $( 'input:checkbox[name=colors]:checked' ), function ( elem ) {
            return $( elem ).val();
          } );

          if ( $( this ).attr( 'name' ) === 'colors' ) {
            var attributeName = 'background-color';
          } else {
            var attributeName = 'shape';
          }
          var attributeValue = $( this ).val();
          var isSelected = $( this ).is( ":checked" );

          _.each( graphPage.cyGraph.nodes(), function ( node ) {

            if ( ( selectedColors.length > 0 && _.indexOf( selectedColors, node.style( 'background-color' ) ) === -1 ) || ( selectedShapes.length > 0 && _.indexOf( selectedShapes, node.style( 'shape' ) ) === -1 ) ) {
              node.unselect();
            } else if ((selectedColors.length > 0 || selectedShapes.length > 0) && parent_nodes.indexOf(node.data().id) == -1) {
              node.select();
            } else {
              node.unselect();
            }

          } );

          graphPage.layoutEditor.undoRedoManager.update( {
            'action_type': 'select_widget_' + _.join( _.sortBy( _.concat( selectedColors, selectedShapes ) ), '_' ),
            'data': {
              'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
              'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
              'selected_elements': graphPage.cyGraph.elements( ':selected' ),
              'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
            }
          } );
        } );
      }
    },
    nodeEditor: {
      styleBeforeEdit: null,
      init: function () {
        var collection = graphPage.cyGraph.nodes( ':selected' );
        if ( collection.length == 1 ) {
          $( '#nodeShape' ).val( collection.style( 'shape' ) );
          $( '#nodeWidth' ).val( _.replace( collection.style( 'width' ), 'px', '' ) );
          $( '#nodeHeight' ).val( _.replace( collection.style( 'height' ), 'px', '' ) );
          $( '#nodeLabel' ).val( collection.style( 'content' ) );

          $( "#nodeBackgroundColorPicker" ).colorpicker( 'setValue', collection.style( 'background-color' ) );
        } else {
          $( '#nodeShape' ).val( null );
          $( '#nodeWidth' ).val( null );
          $( '#nodeHeight' ).val( null );
          $( '#nodeLabel' ).val( null );

          $( "#nodeBackgroundColorPicker" ).unbind( 'changeColor' ).colorpicker( 'setValue', null );
          $( '#nodeBackgroundColorPicker' ).on( 'changeColor', graphPage.layoutEditor.nodeEditor.onNodeBackgroudColorChange );
        }
      },
      updateNodeProperty: function ( styleJSON ) {
        nodeSelector = _.template( "node[name='<%= name %>']" );
        var tempStyle = graphPage.cyGraph.style();
        _.each( graphPage.cyGraph.elements( ':selected' ), function ( elem ) {
          tempStyle = tempStyle.selector( nodeSelector( {
            'name': elem.data( 'name' )
          } ) ).style( styleJSON );
        } );
        tempStyle.selector( 'node:selected' ).style( {
          'overlay-color': 'red',
          'overlay-padding': 10,
          'overlay-opacity': 0.3
        } ).update();
        graphPage.layoutEditor.nodeSelector.init();
      },
      open: function ( collection ) {
        collection.unselect();
        graphPage.layoutEditor.nodeEditor.styleBeforeEdit = cytoscapeGraph.getStyleJSON( graphPage.cyGraph );
        collection.select();

        graphPage.cyGraph.on( 'free', function ( e ) {
          graphPage.layoutEditor.nodeEditor.init();
        } );
        $( '.gs-sidebar-nav' ).removeClass( 'active' );
        $( '#nodeEditorSideBar' ).addClass( 'active' );
        graphPage.layoutEditor.nodeEditor.init();

        $( '#nodeWidth' ).on( 'input', function ( e ) {
          if ( _.isEmpty( $( '#nodeWidth' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid width value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.nodeEditor.updateNodeProperty( {
              'width': _.toString( $( '#nodeWidth' ).val() ) + 'px'
            } );
          }
        } );

        $( '#nodeHeight' ).on( 'input', function ( e ) {
          if ( _.isEmpty( $( '#nodeHeight' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid height value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.nodeEditor.updateNodeProperty( {
              'height': _.toString( $( '#nodeHeight' ).val() ) + 'px'
            } );
          }
        } );

        $( '#nodeBackgroundColorPicker' ).on( 'changeColor', graphPage.layoutEditor.nodeEditor.onNodeBackgroudColorChange );

        $( '#nodeShape' ).on( 'change', function ( e ) {
          if ( _.isEmpty( $( '#nodeShape' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid shape value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.nodeEditor.updateNodeProperty( {
              'shape': $( '#nodeShape' ).val()
            } );
          }
        } );

        $( '#nodeLabel' ).on( 'input', function ( e ) {
          if ( !_.isEmpty( $( '#nodeLabel' ).val() ) ) {

            graphPage.layoutEditor.nodeEditor.updateNodeProperty( {
              'content': $( '#nodeLabel' ).val()
            } );
          }
        } );
      },
      close: function ( save ) {
        if ( save ) {
          graphPage.layoutEditor.undoRedoManager.update( {
            'action_type': 'edit_node_style',
            'data': {
              'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
              'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
              'selected_elements': graphPage.cyGraph.elements( ':selected' ),
              'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
            }
          } );
          graphPage.layoutEditor.nodeEditor.styleBeforeEdit = null;
        } else {
          cytoscapeGraph.applyStylesheet( graphPage.cyGraph, graphPage.layoutEditor.nodeEditor.styleBeforeEdit );
        }
        $( '.gs-sidebar-nav' ).removeClass( 'active' );
        $( '#layoutEditorSideBar' ).addClass( 'active' );
      },
      onNodeBackgroudColorChange: function ( e ) {
        if ( _.isEmpty( $( "#nodeBackgroundColorPicker" ).colorpicker( 'getValue' ) ) ) {
          return $.notify( {
            message: 'Please enter valid color value!',
          }, {
            type: 'warning'
          } );
        } else {
          graphPage.layoutEditor.nodeEditor.updateNodeProperty( {
            'background-color': $( "#nodeBackgroundColorPicker" ).colorpicker( 'getValue' ),
            'text-outline-color': $( "#nodeBackgroundColorPicker" ).colorpicker( 'getValue' ),
          } );
        }
      }
    },
    edgeEditor: {
      styleBeforeEdit: null,
      init: function () {
        var collection = graphPage.cyGraph.edges( ':selected' );
        if ( collection.length == 1 ) {
          collection.unselect();
          $( '#edgeWidth' ).val( _.replace( collection.style( 'width' ), 'px', '' ) );
          $( '#edgeStyle' ).val( collection.style( 'line-style' ) );
          $( '#edgeSourceArrowShape' ).val( collection.style( 'source-arrow-shape' ) );
          $( '#edgeTargetArrowShape' ).val( collection.style( 'target-arrow-shape' ) );
          $( "#edgeLineColorPicker" ).colorpicker( 'setValue', collection.style( 'line-color' ) );
          collection.select();
        } else {
          $( '#edgeWidth' ).val( null );
          $( '#edgeStyle' ).val( null );


          $( "#edgeLineColorPicker" ).unbind( 'changeColor' ).colorpicker( 'setValue', null );
          $( '#edgeLineColorPicker' ).on( 'changeColor', graphPage.layoutEditor.edgeEditor.onEdgeLineColorChange );
        }
      },
      onEdgeLineColorChange: function ( e ) {

        if ( _.isEmpty( $( "#edgeLineColorPicker" ).colorpicker( 'getValue' ) ) ) {
          return $.notify( {
            message: 'Please enter valid color value!'
          }, {
            type: 'warning'
          } );
        } else {
          graphPage.layoutEditor.edgeEditor.updateEdgeProperty( {
            'line-color': $( "#edgeLineColorPicker" ).colorpicker( 'getValue' ),
            'target-arrow-color': $( "#edgeLineColorPicker" ).colorpicker( 'getValue' ),
            'source-arrow-color': $( "#edgeLineColorPicker" ).colorpicker( 'getValue' )
          } );
        }

      },
      updateEdgeProperty: function ( styleJSON ) {
        edgeSelector = _.template( "edge[name='<%= name %>']" );
        var tempStyle = graphPage.cyGraph.style();
        _.each( graphPage.cyGraph.edges( ':selected' ), function ( elem ) {
          tempStyle = tempStyle.style().selector( edgeSelector( {
            'name': elem.data( 'name' )
          } ) ).style( styleJSON );
        } );
        tempStyle.selector( 'edge:selected' ).style( {
          'overlay-color': 'red',
          'overlay-padding': 10,
          'overlay-opacity': 0.3
        } ).update();
      },
      close: function ( save ) {
        if ( save ) {
          graphPage.layoutEditor.undoRedoManager.update( {
            'action_type': 'edit_edge_style',
            'data': {
              'style': cytoscapeGraph.getStylesheet( graphPage.cyGraph ),
              'positions': cytoscapeGraph.getRenderedNodePositionsMap( graphPage.cyGraph ),
              'selected_elements': graphPage.cyGraph.elements( ':selected' ),
              'metadata': layoutLearner.computeLayoutMetadata( graphPage.cyGraph )
            }
          } );
          graphPage.layoutEditor.edgeEditor.styleBeforeEdit = null;
        } else {
          cytoscapeGraph.applyStylesheet( graphPage.cyGraph, graphPage.layoutEditor.edgeEditor.styleBeforeEdit );
        }
        $( '.gs-sidebar-nav' ).removeClass( 'active' );
        $( '#layoutEditorSideBar' ).addClass( 'active' );
      },
      open: function ( collection ) {
        collection.unselect();
        graphPage.layoutEditor.edgeEditor.styleBeforeEdit = cytoscapeGraph.getStyleJSON( graphPage.cyGraph );
        collection.select();

        graphPage.cyGraph.edges().on( 'free', function ( e ) {
          graphPage.layoutEditor.edgeEditor.init();
        } );

        $( '.gs-sidebar-nav' ).removeClass( 'active' );
        $( '#edgeEditorSideBar' ).addClass( 'active' );
        graphPage.layoutEditor.edgeEditor.init();

        $( '#edgeWidth' ).on( 'input', function ( e ) {
          if ( _.isEmpty( $( '#edgeWidth' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid width value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.edgeEditor.updateEdgeProperty( {
              'width': _.toString( $( '#edgeWidth' ).val() ) + 'px'
            } );
          }
        } );

        $( '#edgeStyle' ).on( 'change', function ( e ) {
          if ( _.isEmpty( $( '#edgeStyle' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid style value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.edgeEditor.updateEdgeProperty( {
              'line-style': $( '#edgeStyle' ).val()
            } );
          }
        } );

        $( '#edgeSourceArrowShape' ).on( 'change', function ( e ) {
          if ( _.isEmpty( $( '#edgeSourceArrowShape' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid arrow shape value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.edgeEditor.updateEdgeProperty( {
              'source-arrow-shape': $( '#edgeSourceArrowShape' ).val()
            } );
          }
        } );

        $( '#edgeTargetArrowShape' ).on( 'change', function ( e ) {
          if ( _.isEmpty( $( '#edgeTargetArrowShape' ).val() ) ) {
            return $.notify( {
              message: 'Please enter valid arrow shape value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.layoutEditor.edgeEditor.updateEdgeProperty( {
              'target-arrow-shape': $( '#edgeTargetArrowShape' ).val()
            } );
          }
        } );

        $( '#nodeBackgroundColorPicker' ).on( 'changeColor', graphPage.layoutEditor.edgeEditor.onEdgeLineColorChange );

      }

    }
  },
  filterNodesEdges: {
    init: function () {
      //Hides appropriate nodes based on k value
      $( "#input_k" ).val( graphPage.filterNodesEdges.getLargestK( graph_json.elements ) );

      /*
       * When input_k bar is changed, update the nodes shown in the graph.
       */
      $( "#input_k" ).bind( "change", function () {
        graphPage.filterNodesEdges.setInputK();
      } );

      //Shows up to maximum k values
      $( "#input_max" ).val( graphPage.filterNodesEdges.getLargestK( graph_json.elements ) );

      if ( $( "#input_max" ).val() == 0 ) {
        $( '#filterNodesEdgesSideBarBtn' ).hide();
      }

      //When user slides, it changes value of slider as well
      //as updates graph to reflect max k values allowed in subgraph
      $( "#slider" ).slider( {
        value: $( "#input_max" ).val(),
        max: $( "#input_max" ).val(),
        min: 0,
        step: 1,
        slide: function ( event, ui ) {
          $( "#input_k" ).val( ui.value );
          m_val = ui.value;
          if ( m_val < 0 ) {
            m_val = 0;
            $( this ).slider( {
              value: 0
            } );
          }
        },
        change: function ( event, ui ) {
          if ( event.originalEvent ) {
            graphPage.filterNodesEdges.showOnlyK();
          }
        }
      } );
    },
    setInputK: function () {
      /*
       * Updates the text box when the user slides the bar.
       */
      if ( $( "#input_k" ).val() < 0 ) {
        $( "#input_k" ).val( 0 );
      }
      if ( parseInt( $( "#input_k" ).val() ) > parseInt( $( "#input_max" ).val() ) ) {
        $( "#input_k" ).val( $( "#input_max" ).val() );

      }
      graphPage.filterNodesEdges.setBarToValue( $( "#input_k" ), "slider" );
      $( "#slider" ).slider( {
        value: $( "#input_k" ).val(),
        max: $( '#input_max' ).val()
      } );
    },
    getLargestK: function ( graph_json ) {
      // Gets the largest K value elements from the graph
      // and only renders those values
      var edges = graph_json[ 'edges' ];

      var largestK = 0;
      for ( var i = 0; i < edges.length; i++ ) {
        k_val = parseInt( edges[ i ][ 'data' ][ 'k' ] );
        if ( k_val > largestK ) {
          largestK = k_val;
        }
      }
      return largestK;
    },
    applyMax: function ( graph_layout ) {
      //Gets all nodes and edges up do the max value set
      //and only renders them
      var maxVal = parseInt( $( "#input_max" ).val() );

      if ( !maxVal ) {
        return;
      }
      var newJSON = {
        "nodes": new Array(),
        "edges": new Array()
      };

      // List of node ids that should remain in the graph
      var nodeNames = Array();

      //Get all edges that meet the max quantifier
      for ( var i = 0; i < graph_json.elements[ 'edges' ].length; i++ ) {
        var edge_data = graph_json.elements[ 'edges' ][ i ];
        if ( edge_data[ 'data' ][ 'k' ] <= maxVal ) {
          newJSON[ 'edges' ].push( edge_data );
          nodeNames.push( edge_data[ 'data' ][ 'source' ] );
          nodeNames.push( edge_data[ 'data' ][ 'target' ] );
        }
      }

      //Get all nodes that meet the max quantifier
      for ( var i = 0; i < graph_json.elements[ 'nodes' ].length; i++ ) {
        var node_data = graph_json.elements[ 'nodes' ][ i ];
        if ( nodeNames.indexOf( node_data[ 'data' ][ 'id' ] ) > -1 ) {
          newJSON[ 'nodes' ].push( node_data );
        }
      }

      graphPage.cyGraph.load( newJSON );
      graphPage.filterNodesEdges.showOnlyK();
    },
    showOnlyK: function () {
      // Returns all the id's that are > k value
      if ( $( "#input_k" ).val() ) {
        if ( $( "#input_k" ).val().length > 0 ) {
          var maxVal = parseInt( $( "#input_k" ).val() );

          graphPage.cyGraph.elements().show();
          hideList = graphPage.cyGraph.filter( '[k > ' + maxVal + ']' );
          hideList.hide();
        }
      }
    },
    setBarToValue: function ( inputId, barId ) {
      /**
       * If the user enters a value greater than the max value allowed, change value of bar to max allowed value.
       * inputId the id of the input bar
       * barId  the id of the max paths shown bar.
       */
      if ( $( inputId ).val() > $( "#input_max" ).val() ) {
        $( inputId ).val( $( "#input_max" ).val() );
      }
      graphPage.filterNodesEdges.showOnlyK();
    }
  },
  colaLayoutWidget: {
    init: function () {

      /*
       * When input_k bar is changed, update the nodes shown in the graph.
       */
      $( "#EdgeLengthInput" ).bind( "change", function () {
        graphPage.colaLayoutWidget.setInputK();
      } );
      $( "#NodeSpaceInput" ).bind( "change", function () {
        graphPage.colaLayoutWidget.setInputK();
      } );

      //Shows up to maximum k values
      $( "#input_max" ).val( 400 );


      //When user slides, it changes value of slider as well
      //as updates graph to reflect max k values allowed in subgraph
      $( "#EdgeLengthSlider" ).slider( {
        value: 45, //initial 45
        max: 400,
        min: 1,
        step: 1,
        slide: function ( event, ui ) {
          $( "#EdgeLengthInput" ).val( ui.value );
          m_val = ui.value;
          if ( m_val < 1 ) {
            m_val = 1;
            $( this ).slider( {
              value: 1
            } );
          }
        },
        change: function ( event, ui ) {
          if ( event.originalEvent ) {
            graphPage.colaLayoutWidget.edgeLengthChanged( $( "#EdgeLengthInput" ).val() );
          }
        }
      } );

      $( "#NodeSpaceSlider" ).slider( {
        value: 5,
        max: 50,
        min: 1,
        step: 1,
        slide: function ( event, ui ) {
          $( "#NodeSpaceInput" ).val( ui.value );
          m_val = ui.value;
          if ( m_val < 1 ) {
            m_val = 1;
            $( this ).slider( {
              value: 1
            } );
          }
        },
        change: function ( event, ui ) {
          if ( event.originalEvent ) {
            graphPage.colaLayoutWidget.nodeSpaceChanged( $( "#NodeSpaceInput" ).val() );
          }
        }
      } );



    },
    nodeSpaceChanged: function ( newNodeSpace ) {
      cola_node_space = newNodeSpace;
      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    edgeLengthChanged: function ( newEdgeLength ) {
      cola_edge_length = newEdgeLength;
      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: parseInt( cola_edge_length ),
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      };

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    overlapChanged: function ( checked ) {
      cola_avoid_overlap = checked;

      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );
      //        window.history.pushState('auto-layout', 'Graph Page', window.location.origin + window.location.pathname + '?auto_layout=' + layout_id);
      //        graphPage.defaultLayoutWidget.init(0);
    },
    infiniteChanged: function ( checked ) {


      cola_infinite = checked;
      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    fitChanged: function ( checked ) {
      cola_fit = checked;

      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );
    },
    randomizeChanged: function () {

      cola_randomize = true;


      newGraphLayout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_fit,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    flowXChanged: function ( checked ) {
      var newGraphLayout;
      //When flow checkbox is checked
      if ( checked ) {

        cola_flow = {
          axis: "x",
          minSeparation: 10
        };
        $( "#input_flow_y" ).prop( "checked", false );
        newGraphLayout = {
          name: 'cola',
          nodeSpacing: cola_node_space,
          edgeLength: cola_edge_length,
          animate: true,
          randomize: cola_randomize,
          avoidOverlap: cola_avoid_overlap,
          fit: cola_fit,
          flow: cola_flow,
          infinite: cola_infinite,
          maxSimulationTime: 4000
        }

      } else {
        cola_flow = undefined;
        newGraphLayout = {
          name: 'cola',
          nodeSpacing: cola_node_space,
          edgeLength: cola_edge_length,
          animate: true,
          randomize: cola_randomize,
          avoidOverlap: cola_avoid_overlap,
          fit: cola_fit,
          flow: cola_flow,
          infinite: cola_infinite,
          maxSimulationTime: 4000
        }
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    flowYChanged: function ( checked ) {
      var newGraphLayout;

      //When flow checkbox is checked
      if ( checked ) {
        cola_flow = {
          axis: "y",
          minSeparation: 10
        };
        $( "#input_flow_x" ).prop( "checked", false );
        newGraphLayout = {
          name: 'cola',
          nodeSpacing: cola_node_space,
          edgeLength: cola_edge_length,
          animate: true,
          randomize: cola_randomize,
          avoidOverlap: cola_avoid_overlap,
          fit: cola_fit,
          flow: cola_flow,
          infinite: cola_infinite,
          maxSimulationTime: 4000
        }

      }
      //Both x and y are unchecked
      else {
        cola_flow = undefined;
        newGraphLayout = {
          name: 'cola',
          nodeSpacing: cola_node_space,
          edgeLength: cola_edge_length,
          animate: true,
          randomize: cola_randomize,
          avoidOverlap: cola_avoid_overlap,
          fit: cola_fit,
          flow: cola_flow,
          infinite: cola_infinite,
          maxSimulationTime: 4000
        }
      }

      graphPage.applyLayout( newGraphLayout );
      console.log( "after applying layout" );

    },
    setInputEdgeLength: function () {
      /*
       * Updates the text box when the user slides the bar.
       */
      if ( $( "#EdgeLengthInput" ).val() < 1 ) {
        $( "#EdgeLengthInput" ).val( 1 );
      }
      if ( parseInt( $( "#EdgeLengthInput" ).val() ) > 400 ) {
        $( "#EdgeLengthInput" ).val( 400 );

      }
      graphPage.colaLayoutWidget.setBarToValueEdgeLength( $( "#EdgeLengthInput" ), "EdgeLengthSlider" );
      $( "#EdgeLengthSlider" ).slider( {
        value: $( "#EdgeLengthInput" ).val(),
        max: 400
      } );
    },
    setInputNodeSpace: function () {
      /*
       * Updates the text box when the user slides the bar.
       */
      if ( $( "#NodeSpaceInput" ).val() < 1 ) {
        $( "#NodeSpaceInput" ).val( 1 );
      }
      if ( parseInt( $( "#NodeSpaceInput" ).val() ) > 50 ) {
        $( "#NodeSpaceInput" ).val( 50 );

      }
      graphPage.colaLayoutWidget.setBarToValueNodeSpace( $( "#NodeSpaceInput" ), "NodeSpaceSlider" );
      $( "#NodeSpaceSlider" ).slider( {
        value: $( "#NodeSpaceInput" ).val(),
        max: 50
      } );
    },
    applyMax: function ( graph_layout ) {
      //Gets all nodes and edges up do the max value set
      //and only renders them
      var maxVal = parseInt( $( "#input_max" ).val() );

      if ( !maxVal ) {
        return;
      }
      var newJSON = {
        "nodes": new Array(),
        "edges": new Array()
      };

      // List of node ids that should remain in the graph
      var nodeNames = Array();

      //Get all edges that meet the max quantifier
      for ( var i = 0; i < graph_json.elements[ 'edges' ].length; i++ ) {
        var edge_data = graph_json.elements[ 'edges' ][ i ];
        if ( edge_data[ 'data' ][ 'k' ] <= maxVal ) {
          newJSON[ 'edges' ].push( edge_data );
          nodeNames.push( edge_data[ 'data' ][ 'source' ] );
          nodeNames.push( edge_data[ 'data' ][ 'target' ] );
        }
      }

      //Get all nodes that meet the max quantifier
      for ( var i = 0; i < graph_json.elements[ 'nodes' ].length; i++ ) {
        var node_data = graph_json.elements[ 'nodes' ][ i ];
        if ( nodeNames.indexOf( node_data[ 'data' ][ 'id' ] ) > -1 ) {
          newJSON[ 'nodes' ].push( node_data );
        }
      }

      graphPage.cyGraph.load( newJSON );
      graphPage.filterNodesEdges.showOnlyK();
    },
    setBarToValueEdgeLength: function ( inputId, barId ) {
      /**
       * If the user enters a value greater than the max value allowed, change value of bar to max allowed value.
       * inputId the id of the input bar
       * barId  the id of the max paths shown bar.
       */
      if ( $( inputId ).val() > 400 ) {
        $( inputId ).val( 400 );
      }

    },
    setBarToValueNodeSpace: function ( inputID, barId ) {
      if ( $( inputId ).val() > 50 ) {
        $( inputId ).val( 50 );
      }
    }
  },
  legend: {
    /**
     * This function is called to setup the legend in graph page.
     * It will initialize all the event listeners.
     */
    cyLegend: undefined,
    currentLegendJSON: {},
    currentLegendSizeFactor: 0.7,
    isEmpty: function () {
      return _.isEmpty( graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ] ) && _.isEmpty( graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ] )
    },
    init: function ( styleJSON ) {
      if ( !( 'legend' in styleJSON ) ) {
        styleJSON[ 'legend' ] = {};
      }
      // create a deep copy of the legend_json from the global style_json object.
      graphPage.legend.currentLegendJSON[ 'legend' ] = JSON.parse( JSON.stringify( styleJSON[ 'legend' ] ) );
      graphPage.legend.cyLegend = graphPage.legend.constructLegend();

      // makes the legend interface draggable
      $( "#cyLegendContainer" ).draggable( {
        containment: "#cyGraphContainer",
        scroll: false
      } );

      var updateLegendInHtmlFormat = 0;
      $( "#graphDetailsTabBtn" ).click( function () {
        /* This function is called when a user clicks on graph details tab.
         * This function will check if the graph contains HTML legend data in a particular format.
         * If the graph contains such HTML legend format,the variable "updateLegendInHtmlFormat"
         * is set to a unique value else 0 as default.
         */
        htmlLegendData = graph_json[ 'data' ][ 'description' ];
        if ( htmlLegendData ) {
          try {
            //Checks if the HTML format legend data is in format1. If not throws error.
            updateLegendInHtmlFormat = graphPage.legend.checkGraphWithHtmlLegendFormat1( htmlLegendData );
          } catch ( e ) {
            try {
              //Checks if the HTML format legend data is in format2. If not throws error.
              updateLegendInHtmlFormat = graphPage.legend.checkGraphWithHtmlLegendFormat2( htmlLegendData );
            } catch ( e ) {
              console.log( 'error!' );
            }
          }
        }
      } );

      $( "#ConfirmHtmlLegendConversionBtn" ).click( function () {
        /*This is the custom ajax request to convert and update the HTML format legend to JSON format*/
        $( '#convertHtmlLegendOption' ).hide();
        apis.graphs.update( $( '#GraphID' ).val(), {
            'update_legend_format': updateLegendInHtmlFormat
          },
          successCallback = function ( response ) {
            // This method is called when the graph is successfully updated with the legend JSON format.
            // The option to convert and update the HTML format legend to JSON format for the grah is hidden.
            location.reload( true );
          },
          errorCallback = function ( xhr, status, errorThrown ) {
            // This method is called when error occurs while updating the graph.
            $.notify( {
              message: response.responseJSON.error_message
            }, {
              type: 'danger'
            } );
          } );
        $.notify( {
          message: 'Submitted the request to update the legend format. The legend will be updated in a few minutes.'
        }, {
          type: 'info'
        } );

      } );

      $( "#toggleLegendBtn" ).click( function ( e ) {
        /*This function is called when user clicks either Hide Legend or Show Legend button available in the
         * default sidebar.
         * This function toggles the legend interface.
         */

        var legendContainer = document.getElementById( "cyLegendContainer" );
        if ( legendContainer.style.zIndex == -1 ) {
          legendContainer.style.zIndex = 999
          legendContainer.style.display = "block";
          document.getElementById( "toggleLegendBtn" ).innerHTML = "Hide Legend";
        } else {
          legendContainer.style.zIndex = -1
          document.getElementById( "toggleLegendBtn" ).innerHTML = "Show Legend";
        }
        graphPage.cyGraph.elements().unselect();
        graphPage.legend.cyLegend.elements().unselect();
      } );

      if ( graphPage.legend.isEmpty() ) {
        $( '#toggleLegendBtn' ).trigger( 'click' );
        $( '#toggleLegendBtn' ).hide();
      }

      $( 'input[name="checkForUserLayout"]' ).change( function () {
        /* This method is called when the user choose to save legend in a user layout.
         * Once checked creates a dropdown with all the user layout to choose upon which layout to save the legend.
         * Un-checks the other option to save the legend in the current graph.
         */
        if ( $( this ).is( ":checked" ) ) {
          params = {}
          params[ "is_shared" ] = 0;
          params[ "owner_email" ] = $( '#UserEmail' ).val();
          apis.layouts.get( $( '#GraphID' ).val(), params,
            successCallback = function ( response ) {
              var s = $( "<select></select>" ).attr( "id", 'selectLayoutDropdown' ).attr( "name", 'selectLayoutDropdown' );
              _.each( response.layouts, function ( layout ) {
                if ( utils.getURLParameter( 'user_layout' ) == layout.id ) {
                  $( '<option />', {
                    value: JSON.stringify( layout ),
                    text: layout.name
                  } ).appendTo( s );
                }
              } );
              _.each( response.layouts, function ( layout ) {
                if ( utils.getURLParameter( 'user_layout' ) != layout.id ) {
                  $( '<option />', {
                    value: JSON.stringify( layout ),
                    text: layout.name
                  } ).appendTo( s );
                }
              } );
              $( "#selectLayoutDropdown" ).val( $( "#target option:first" ).val() );
              s.appendTo( '#userPrivateLayoutDropdown' );
            },
            errorCallback = function () {
              console.log( 'error!' );
            }
          );
        } else {
          if ( $( '#selectLayoutDropdown' ).length )
            $( '#selectLayoutDropdown' ).remove();
        }
      } );

      $( '#saveOnExitLegendEditorBtn' ).click( function () {
        /*This function is called when user clicks on the "save and exit" legend button available on the legend modal.*/

        graphPage.legend.cyLegend.destroy();
        graphPage.legend.resizeLegendInterfaceHeight( "0px" );
        graphPage.legend.cyLegend = graphPage.legend.constructLegend();

        if ( !_.isEmpty( utils.getURLParameter( 'user_layout' ) ) ) {
          if ( $( '#checkForUserLayout' ).is( ':checked' ) && !$( '#checkForCurrentGraph' ).is( ':checked' ) ) {
            layoutData = document.getElementById( 'selectLayoutDropdown' ).value;
            layout_id = JSON.parse( layoutData ).id;
            layout_style_json = JSON.parse( layoutData ).style_json;
            graphPage.legend.saveLegendInUserLayout( layout_id, layout_style_json, '#saveOnExitLegendModal' );
          }

          if ( $( '#checkForCurrentGraph' ).is( ':checked' ) && !$( '#checkForUserLayout' ).is( ':checked' ) ) {
            graphPage.legend.saveLegendInGraph( '#saveOnExitLegendModal' );
          }

          if ( $( '#checkForCurrentGraph' ).is( ':checked' ) && $( '#checkForUserLayout' ).is( ':checked' ) ) {
            layoutData = document.getElementById( 'selectLayoutDropdown' ).value;
            layoutId = JSON.parse( layoutData ).id;
            layout_style_json = JSON.parse( layoutData ).style_json;
            apis.layouts.update( $( '#GraphID' ).val(), layoutId, {
                "style_json": {
                  "format_version": "1.0",
                  "generated_by": "graphspace-2.0.0",
                  "target_cytoscapejs_version": "~2.7",
                  "style": JSON.parse( layout_style_json ).style,
                  "legend": graphPage.legend.currentLegendJSON[ 'legend' ]
                }
              },
              successCallback = function ( response ) {
                graphPage.legend.saveLegendInGraph( '#saveOnExitLegendModal' );
              },
              errorCallback = function ( xhr, status, errorThrown ) {
                $.notify( {
                  message: response.responseJSON.error_message
                }, {
                  type: 'danger'
                } );
              } );
          }

          if ( !$( '#checkForUserLayout' ).is( ':checked' ) && !$( '#checkForCurrentGraph' ).is( ':checked' ) ) {
            $.notify( {
              message: 'Select atleast one of the options to save Legend'
            }, {
              type: 'warning'
            } );
          }
        } else {
          if ( $( '#checkForCurrentGraph' ).is( ':checked' ) ) {
            graphPage.legend.saveLegendInGraph( '#saveOnExitLegendModal' );
          } else {
            $.notify( {
              message: 'Select atleast one of the options to save Legend'
            }, {
              type: 'warning'
            } );
          }
        }
        graphPage.legend.resizeLegendInterfaceWidth( 20 * graphPage.legend.currentLegendSizeFactor + '%' );
        graphPage.legend.legendEditor.removeBinLegend();
        graphPage.legend.legendEditor.removeEditLegend();
      } );

      $( '#legendEditorBtn' ).click( function () {
        graphPage.legend.legendEditor.init();
      } );

      $( '#exitLegendEditorBtn' ).click( function () {
        /*This function is called when user clicks on the "Exit Legend Editor" legend button available on the legend editor sidebar.
         *This function activates the save on exit legend modal which provides user the option to save legend.
         */
        $( "#checkForCurrentGraph" ).prop( "checked", true );

        if ( !_.isEmpty( utils.getURLParameter( 'user_layout' ) ) ) {
          $( '#selectUserLayoutCheckbox' ).show();
          $( "#checkForUserLayout" ).prop( "checked", false );
        } else {
          $( '#selectUserLayoutCheckbox' ).hide();
        }
        if ( $( '#selectLayoutDropdown' ).length )
          $( '#selectLayoutDropdown' ).remove();

        $( '#exitLegendBtn' ).removeClass( 'hidden' );
        $( '#saveOnExitLegendModal' ).modal( 'show' );
      } );

      $( '#exitLegendBtn' ).click( function () {
        /*This function is called when user clicks on the "Exit without saving" legend button available on the legend modal.
         * This function exits the legend editor tool without saving the current available legend anywhere.
         */
        graphPage.legend.cyLegend.destroy();
        graphPage.legend.resizeLegendInterfaceHeight( "0px" );
        graphPage.legend.cyLegend = graphPage.legend.constructLegend();

        graphPage.cyGraph.elements().unselect();
        graphPage.legend.resizeLegendInterfaceWidth( 20 * graphPage.legend.currentLegendSizeFactor + '%' );
        graphPage.legend.legendEditor.removeBinLegend();
        graphPage.legend.legendEditor.removeEditLegend();
      } );
    },
    exportNetworkWithLegend: function ( fileformat ) {
      var filename = $( '#GraphName' ).val()
      var canvas = document.getElementById( 'mycanvas' );
      var context = canvas.getContext( '2d' );
      var cyGraphImg = new Image();
      var cyLegendImg = new Image();

      if ( fileformat === 'png' ) {
        var cyGraph_b64 = graphPage.cyGraph.png();
        graphPage.legend.cyLegend.nodes( '.legend_resize' ).hide();
        var cyLegend_b64 = graphPage.legend.cyLegend.png();
        graphPage.legend.cyLegend.nodes( '.legend_resize' ).show();


        cyGraphImg.onload = function () {
          canvas.width = cyGraphImg.width;
          canvas.height = cyGraphImg.height;
          cyLegendImg.src = cyLegend_b64;
        };

        cyLegendImg.onload = function () {
          context.globalAlpha = 1;
          context.drawImage( cyGraphImg, 0, 0 );
          context.globalAlpha = 1;
          context.drawImage( cyLegendImg, 0, 0 );
        };

        cyGraphImg.src = cyGraph_b64;
        var file = canvas.toDataURL();

        var link = $( '<a>' ).attr( 'href', file ).attr( 'download', filename + '.' + fileformat );
        $( 'body' ).append( link );
        link.get( 0 ).click();
        link.get( 0 ).remove();
      }

      if ( fileformat === 'jpg' ) {
        var cyGraph_b64 = graphPage.cyGraph.jpeg();
        graphPage.legend.cyLegend.nodes( '.legend_resize' ).hide();
        var cyLegend_b64 = graphPage.legend.cyLegend.jpeg();
        graphPage.legend.cyLegend.nodes( '.legend_resize' ).show();

        cyGraphImg.onload = function () {
          canvas.width = cyGraphImg.width;
          canvas.height = cyGraphImg.height;
          cyLegendImg.src = cyLegend_b64;
        };
        cyLegendImg.onload = function () {
          context.globalAlpha = 1;
          context.drawImage( cyGraphImg, 0, 0 );
          context.globalAlpha = 1;
          context.drawImage( cyLegendImg, 0, 0 );
        };
        cyGraphImg.src = cyGraph_b64;
        var file = canvas.toDataURL( "image/jpeg" );
        var link = $( '<a>' ).attr( 'href', file ).attr( 'download', filename + '.' + fileformat );
        $( 'body' ).append( link );
        link.get( 0 ).click();
        link.get( 0 ).remove();
      }

      // setTimeout( graphPage.legend.exportNetworkWithLegend1( fileformat ), 100000 );
    },
    checkGraphWithHtmlLegendFormat1: function ( htmlLegendData ) {
      const HTML_LEGEND_TABLE_FORMAT_1 = 1;
      var html_legend_data = $( $.parseHTML( htmlLegendData ) );
      var node_table = html_legend_data.filter( 'table' )[ 0 ].innerHTML;
      var edge_table = html_legend_data.filter( 'table' )[ 1 ].innerHTML;
      var actual_node_desc = [ 'Source Receptor', 'Target TF', 'Receptor', 'TF', 'Intermediate Protein' ];

      var node_elements = $( node_table );
      var found = $( 'td', node_elements );
      var parsed_node_desc = [];
      for ( var i = 1; i < found.length; i += 2 ) {
        parsed_node_desc.push( found[ i ].innerText );
      }

      if ( JSON.stringify( parsed_node_desc ) === JSON.stringify( actual_node_desc ) ) {
        $( '#convertHtmlLegendOption' ).show();
        return HTML_LEGEND_TABLE_FORMAT_1;
      }
      return 0;
    },
    checkGraphWithHtmlLegendFormat2: function ( htmlLegendData ) {
      const HTML_LEGEND_TABLE_FORMAT_2 = 2;
      var html_legend_data = $( $.parseHTML( htmlLegendData ) );
      var legend_table_count = html_legend_data.filter( 'table' ).length;
      var node_table = html_legend_data.filter( 'table' )[ 0 ].innerHTML;
      var node_elements = $( node_table );
      var found = $( 'td', node_elements );
      var parsed_node_desc = [];

      parsed_node_desc.push( found[ 1 ].innerText );
      parsed_node_desc.push( found[ 3 ].innerText );

      if ( legend_table_count == 1 && JSON.stringify( parsed_node_desc ) == JSON.stringify( [ "Receptor", "Transcription Factor" ] ) ) {
        $( '#convertHtmlLegendOption' ).show();
        return HTML_LEGEND_TABLE_FORMAT_2;
      }
      return 0;
    },
    incrementLegendInterfaceHeight: function ( heightToIncrement ) {
      var legendContainer = document.getElementById( "cyLegendContainer" );
      var currentlegendContainerHeight = Number( legendContainer.style.height.slice( 0, -2 ) );
      heightToIncrement = Number( heightToIncrement.slice( 0, -2 ) );
      legendContainer.style.height = ( currentlegendContainerHeight + heightToIncrement ).toString() + 'px';
    },
    decrementLegendInterfaceHeight: function ( heightToDecrement ) {
      var legendContainer = document.getElementById( "cyLegendContainer" );
      var currentlegendContainerHeight = Number( legendContainer.style.height.slice( 0, -2 ) );
      heightToDecrement = Number( heightToDecrement.slice( 0, -2 ) );
      legendContainer.style.height = ( currentlegendContainerHeight - heightToDecrement ).toString() + 'px';
    },
    resizeLegendInterfaceWidth: function ( legendContainerWidth ) {
      var legendContainer = document.getElementById( "cyLegendContainer" );
      legendContainer.style.width = legendContainerWidth;
    },
    resizeLegendInterfaceHeight: function ( legendContainerHeight ) {
      var legendContainer = document.getElementById( "cyLegendContainer" );
      legendContainer.style.height = legendContainerHeight;
    },
    saveLegendInUserLayout: function ( layoutId, styleJSON, modalNameId, callback ) {
      graphPage.cyGraph.elements().unselect();
      graphPage.legend.cyLegend.elements().unselect();
      apis.layouts.update( $( '#GraphID' ).val(), layoutId, {
          "style_json": {
            "format_version": "1.0",
            "generated_by": "graphspace-2.0.0",
            "target_cytoscapejs_version": "~2.7",
            "style": JSON.parse( styleJSON ).style,
            "legend": graphPage.legend.currentLegendJSON[ 'legend' ]
          }
        },
        successCallback = function ( response ) {
          $( modalNameId ).modal( 'toggle' );
        },
        errorCallback = function ( xhr, status, errorThrown ) {
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );
    },
    saveLegendInGraph: function ( modalNameId, callback ) {
      graphPage.cyGraph.elements().unselect();
      graphPage.legend.cyLegend.elements().unselect();

      positions_json = cytoscapeGraph.getNodePositions( graphPage.cyGraph );
      cyGraph_style_json = cytoscapeGraph.getStylesheet( graphPage.cyGraph );

      apis.graphs.update( $( '#GraphID' ).val(), {
          "style_json": {
            "format_version": "1.0",
            "generated_by": "graphspace-2.0.0",
            "target_cytoscapejs_version": "~2.7",
            "style": cyGraph_style_json,
            "legend": graphPage.legend.currentLegendJSON[ 'legend' ]
          }
        },
        successCallback = function ( response ) {
          $( modalNameId ).modal( 'toggle' );
        },
        errorCallback = function ( xhr, status, errorThrown ) {
          $.notify( {
            message: response.responseJSON.error_message
          }, {
            type: 'danger'
          } );
        } );

    },
    constructLegend: function () {
      /*
      This function will create a legend graph(using cytoscape.js library) from the legend data
      in the style_json object.
      */
      if ( !( 'nodes' in graphPage.legend.currentLegendJSON[ 'legend' ] ) ) {
        graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ] = {};
      }
      if ( !( 'edges' in graphPage.legend.currentLegendJSON[ 'legend' ] ) ) {
        graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ] = {};
      }

      var factor = graphPage.legend.currentLegendSizeFactor;
      graphPage.legend.resizeLegendInterfaceWidth( 20 * factor + "%" );

      var node_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ];
      var edge_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ];
      var node_legend_count = Object.keys( node_legend ).length;
      var edge_legend_count = Object.keys( edge_legend ).length;

      var cy = cytoscape( {
        container: document.getElementById( 'cyLegendContainer' ),
        autolock: true,
        autoungrabify: true,
        userPanningEnabled: false,
        userZoomingEnabled: false,
        boxSelectionEnabled: false,
        ready: function () {
          this.on( 'tap', graphPage.legend.onTapLegendGraphElement );

        }
      } );
      // console.log( cy.width(), cy.height(), cy.extent() );

      // var extent = cy.extent();

      // Adds elements to resize the legend interface
      var padding = 5 + 5 * factor;

      cy.add( [ {
        group: 'nodes',
        data: {
          id: 'sm'
        },
        classes: 'legend_resize',
        position: {
          // y: y_pos + 10,
          y: cy.extent()[ 'y1' ] + padding,
          x: cy.extent()[ 'x2' ] - padding
        }
      } ] ).style( {
        'background-image': '../images/minimize.png',
        'background-fit': 'cover',
        'background-color': 'white',
        'shape': 'square',
        'width': 15 * factor + 'px',
        'height': 15 * factor + 'px',
      } );

      // cy.add( [ {
      //   group: 'nodes',
      //   data: {
      //     id: 'md'
      //   },
      //   position: {
      //     y: y_pos + 10,
      //     x: 105 * factor
      //   }
      // } ] ).style( {
      //   'background-image': '../images/collapse.png',
      //   'background-color': 'white',
      //   'shape': 'square',
      //   'width': 15 * factor + 'px',
      //   'height': 15 * factor + 'px',
      // } );

      cy.add( [ {
        group: 'nodes',
        data: {
          id: 'lg'
        },
        classes: 'legend_resize',
        position: {
          y: cy.extent()[ 'y1' ] + padding,
          // x: 175 * factor
          x: cy.extent()[ 'x1' ] + padding
        }
      } ] ).style( {
        'background-image': '../images/full.png',
        'background-fit': 'cover',
        'background-color': 'white',
        'shape': 'square',
        'width': 15 * factor + 'px',
        'height': 15 * factor + 'px',
      } );
      graphPage.legend.incrementLegendInterfaceHeight( 30 * factor + 'px' );

      // Adds parent node for the node legend
      var parentId = 0;
      for ( var i = 0; i < node_legend_count; i++ ) {
        cy.add( [ {
          group: 'nodes',
          data: {
            id: PARENT_NODE_LEGEND_INITIALS + i
          }
        } ] ).style( {
          'background-color': 'white',
          'border-color': 'white',
          'padding': 3 * factor + 'px',
          'padding-relative-to': 'height'
        } );
        parentId = i;
      }
      // console.log( extent[ 'w' ] + 'px', );

      // Adds node legend
      // y_pos = 30 * factor;
      y_offset = 30 * factor;
      graphPage.legend.incrementLegendInterfaceHeight( y_offset + 'px' );
      for ( var i = 0; i < node_legend_count; i++ ) {
        // lines = Math.max( Math.round( Object.keys( node_legend )[ i ].length / 20 ) + 1, 2 )
        lines = Math.round( Object.keys( node_legend )[ i ].length / 20 ) + 1
        lines = Math.max( lines % 2 != 0 ? lines : lines + 1, 2 )

        graphPage.legend.incrementLegendInterfaceHeight( 16 * factor * lines + 'px' );
        cy.add( [ {
          group: 'nodes',
          data: {
            id: NODE_LEGEND_INITIALS + i,
            parent: PARENT_NODE_LEGEND_INITIALS + i
          },
          position: {
            // y: y_pos + 10,
            // x: 23 * factor
            y: cy.extent()[ 'y1' ] + padding + y_offset,
            x: cy.extent()[ 'x1' ] + padding
          }
        } ] ).style( {
          'background-color': node_legend[ Object.keys( node_legend )[ i ] ][ 'background-color' ],
          'label': Object.keys( node_legend )[ i ],
          'font-size': 16 * factor + 'px',
          'shape': node_legend[ Object.keys( node_legend )[ i ] ][ 'shape' ].toLowerCase(),
          'width': 15 * factor + 'px',
          'height': 15 * factor + 'px',
          'text-wrap': 'wrap',
          'text-overflow-wrap': 'anywhere',
          'text-max-width': ( cy.extent()[ 'w' ] - padding - 15 * factor - 10 * factor - 10 * factor ) + 'px',
          'text-margin-x': 20 * factor + 'px',
          'text-margin-y': -16 * factor + 'px',
          'text-valign': 'bottom',
          'text-halign': 'right'
        } );
        y_offset = y_offset + 16 * factor * lines;
      }

      /*
      Below if else condition is to tackle the problem when node legend doesnt exist and
      only edge legend is there and vice-versa*/
      if ( node_legend_count == 0 ) {
        var x = parentId;
      } else {
        var x = parentId + 1;
      }

      // Adds parent node for edge legend
      for ( var i = 0; i < edge_legend_count; i++ ) {
        cy.add( [ {
          group: 'nodes',
          data: {
            id: PARENT_NODE_LEGEND_INITIALS + i + node_legend_count
          }
        } ] ).style( {
          'background-color': 'white',
          'border-color': 'white',
          'padding': 3 * factor + 'px',
          'padding-relative-to': 'height'
        } );
      }

      // Adds edge legend
      for ( var i = 0; i < edge_legend_count; i++ ) {
        lines = Math.round( Object.keys( edge_legend )[ i ].length / 20 ) + 1
        lines = Math.max( lines % 2 == 0 ? lines : lines + 1, 2 )
        graphPage.legend.incrementLegendInterfaceHeight( 16 * factor * lines + 'px' );

        cy.add( [ {
          group: 'nodes',
          data: {
            id: EDGE_NODE_LEGEND_INITIALS + i,
            parent: PARENT_NODE_LEGEND_INITIALS + i + node_legend_count
          },
          position: {
            // y: y_pos + 10,
            // x: 15 * factor,
            y: cy.extent()[ 'y1' ] + padding + y_offset,
            x: cy.extent()[ 'x1' ] + padding - 10 * factor
          }
        } ] ).style( {
          'background-color': 'white',
          'background-opacity': '0',
          'width': '1px',
          'height': '1px'
        } );

        cy.add( [ {
          group: 'nodes',
          data: {
            id: EDGE_NODE_LEGEND_INITIALS + i + '-target',
            parent: PARENT_NODE_LEGEND_INITIALS + i + node_legend_count
          },
          position: {
            // y: y_pos + 10,
            // x: 35 * factor,
            y: cy.extent()[ 'y1' ] + padding + y_offset,
            x: cy.extent()[ 'x1' ] + padding + 20 * factor
          }
        } ] ).style( {
          'background-color': 'white',
          'background-opacity': '0',
          'width': '1px',
          'height': '1px',
          'label': Object.keys( edge_legend )[ i ],
          // 'text-margin-x': 5 * factor + 'px',
          // 'text-margin-y': factor + 'px',
          'font-size': 16 * factor + 'px',
          'text-wrap': 'wrap',
          'text-overflow-wrap': 'anywhere',
          'text-max-width': ( cy.extent()[ 'w' ] - padding - 10 * factor - 20 * factor ) + 'px',
          'text-margin-x': 5 * factor + 'px',
          'text-margin-y': -10 * factor + 'px',
          'text-valign': 'bottom',
          'text-halign': 'right'
        } );
        y_offset = y_offset + 16 * factor * lines;

        cy.add( [ {
          group: 'edges',
          data: {
            id: EDGE_LEGEND_INITIALS + i,
            source: EDGE_NODE_LEGEND_INITIALS + i,
            target: EDGE_NODE_LEGEND_INITIALS + i + '-target',
          }
        } ] ).style( {
          'line-color': edge_legend[ Object.keys( edge_legend )[ i ] ][ 'line-color' ],
          'curve-style': 'bezier',
          'width': 4 * factor + 'px',
          'line-style': edge_legend[ Object.keys( edge_legend )[ i ] ][ 'line-style' ],
          'target-arrow-shape': edge_legend[ Object.keys( edge_legend )[ i ] ][ 'arrow-shape' ],
          'target-arrow-color': edge_legend[ Object.keys( edge_legend )[ i ] ][ 'line-color' ]
        } );

        // y_pos = y_pos + 40 * factor;
        x = x + 1;
      }

      // Adds a node of negligible size to make the width of the selected box consistent in all legend entries
      // y_pos = 35 * factor;
      // for ( var i = 0; i < node_legend_count + edge_legend_count; i++ ) {
      //   cy.add( [ {
      //     group: 'nodes',
      //     data: {
      //       id: 'useless' + i,
      //       parent: PARENT_NODE_LEGEND_INITIALS + i
      //     },
      //     position: {
      //       y: y_pos + 10,
      //       x: 185 * factor
      //     }
      //   } ] ).style( {
      //     'background-color': 'white',
      //     'background-opacity': '0',
      //     'width': '1px',
      //     'height': '1px'
      //   } );
      //   y_pos = y_pos + 40 * factor;
      // }

      if ( graphPage.legend.isEmpty() ) {
        $( '#toggleLegendBtn' ).trigger( 'click' );
        $( '#toggleLegendBtn' ).hide();
      }

      return cy;
    },
    onTapLegendGraphElement: function ( evt ) {
      /*Selects the corresponding elements in the cyGraph whenever tapped on the parent node.*/

      // get target
      var target = evt.cyTarget;

      try {
        if ( target.isParent() ) {
          graphPage.legend.cyLegend.style().selector( ':parent:selected' ).style( {
            'overlay-color': 'grey',
            'overlay-padding': 0,
            'overlay-opacity': 0.2
          } ).update();

          /*Iterate through all the child elements of the selected compound node and get the actual legend
          with its property to select the corresponding elements in the cyGraph.*/
          Object.keys( target.children() ).forEach( function ( key ) {
            nodeId = target.children()[ key ].data().id;

            if ( nodeId.slice( 0, 1 ) == NODE_LEGEND_INITIALS ) {
              targetNode = graphPage.legend.cyLegend.nodes( '[id=' + '"' + nodeId + '"' + ']' );
              legend_shape = targetNode.style()[ 'shape' ];
              legend_color = targetNode.style()[ 'background-color' ];
              _.each( graphPage.cyGraph.nodes(), function ( node ) {
                if ( node.style( 'background-color' ) == legend_color && node.style( 'shape' ) == legend_shape ) {
                  graphPage.cyGraph.edges().unselect();
                  node.select();
                } else
                  node.unselect();
              } );
            }
            if ( nodeId.slice( 0, 2 ) == EDGE_NODE_LEGEND_INITIALS && nodeId.length == 3 ) {
              targetEdge = graphPage.legend.cyLegend.edges( '[id=' + '"' + EDGE_LEGEND_INITIALS + nodeId[ 2 ] + '"' + ']' );
              legend_style = targetEdge.style()[ 'line-style' ];
              legend_color = targetEdge.style()[ 'line-color' ];
              arrow_shape = targetEdge.style()[ 'target-arrow-shape' ];
              _.each( graphPage.cyGraph.edges(), function ( edge ) {
                if ( edge.style( 'line-color' ) == legend_color && edge.style( 'line-style' ) == legend_style && ( edge.style( 'source-arrow-shape' ) == arrow_shape || edge.style( 'target-arrow-shape' ) == arrow_shape ) ) {
                  graphPage.cyGraph.nodes().unselect();
                  edge.select();
                } else {
                  edge.unselect();
                }
              } );
            }
          } );
        } else {
          if ( target.isNode() ) {
            nodeId = target.id();
            if ( nodeId.slice( 0, 2 ) == 'sm' ) {
              graphPage.legend.currentLegendSizeFactor = 0.7;
              graphPage.legend.cyLegend.destroy();
              graphPage.legend.resizeLegendInterfaceHeight( "0px" );
              graphPage.legend.cyLegend = graphPage.legend.constructLegend();
              if ( window.location.hash == '#legendEditor' ) {
                graphPage.legend.legendEditor.init();
              }
            }

            if ( nodeId.slice( 0, 2 ) == 'md' ) {
              graphPage.legend.currentLegendSizeFactor = 1;
              graphPage.legend.cyLegend.destroy();
              graphPage.legend.resizeLegendInterfaceHeight( "0px" );
              graphPage.legend.cyLegend = graphPage.legend.constructLegend();
              if ( window.location.hash == '#legendEditor' ) {
                graphPage.legend.legendEditor.init();
              }
            }

            if ( nodeId.slice( 0, 2 ) == 'lg' ) {
              graphPage.legend.currentLegendSizeFactor = 1.2;
              graphPage.legend.cyLegend.destroy();
              graphPage.legend.resizeLegendInterfaceHeight( "0px" );
              graphPage.legend.cyLegend = graphPage.legend.constructLegend();
              if ( window.location.hash == '#legendEditor' ) {
                graphPage.legend.legendEditor.init();
              }
            }

            if ( nodeId.slice( 0, 1 ) == 'n' ) {
              legend_shape = target.style()[ 'shape' ];
              legend_color = target.style()[ 'background-color' ];
              _.each( graphPage.cyGraph.nodes(), function ( node ) {
                if ( node.style( 'background-color' ) == legend_color && node.style( 'shape' ) == legend_shape ) {
                  graphPage.cyGraph.edges().unselect();
                  node.select();
                } else {
                  node.unselect();
                }
              } );
            }
          }

          if ( target.isEdge() ) {
            legend_style = target.style()[ 'line-style' ];
            legend_color = target.style()[ 'line-color' ];
            arrow_shape = target.style()[ 'target-arrow-shape' ];

            _.each( graphPage.cyGraph.edges(), function ( edge ) {
              if ( edge.style( 'line-color' ) == legend_color && edge.style( 'line-style' ) == legend_style && ( edge.style( 'source-arrow-shape' ) == arrow_shape || edge.style( 'target-arrow-shape' ) == arrow_shape ) ) {
                graphPage.cyGraph.nodes().unselect();
                edge.select();
              } else {
                edge.unselect();
              }
            } );
          }
        }
      } catch {
        console.log( 'error!' );
      }
    },
    legendEditor: {
      init: function () {
        // Check if legend interface is active or not. If not, activate it first.
        if ( document.getElementById( "toggleLegendBtn" ).innerHTML == "Show Legend" ) {
          $( '#toggleLegendBtn' ).trigger( 'click' );
        }

        graphPage.legend.resizeLegendInterfaceWidth( 24 * graphPage.legend.currentLegendSizeFactor + '%' );
        graphPage.cyGraph.elements().unselect();
        graphPage.legend.cyLegend.elements().unselect();
        graphPage.legend.legendEditor.constructBinLegend();
        graphPage.legend.legendEditor.constructEditLegend();

        _.each( graphPage.legend.cyLegend.nodes(), function ( node ) {
          if ( node.id().slice( 0, 1 ) === 'u' ) {
            graphPage.legend.cyLegend.remove( node );
          }
        } );

        /*Once a bin node(identified by id with "rm" as prefix) is tapped, all the nodes having same
         * y-coordinate and different x-cordinate is removed.
         */
        graphPage.legend.cyLegend.on( 'tap', 'node', function ( evt ) {
          var bin_node = evt.cyTarget;
          console.log( 'tapped ' + bin_node.id() );
          if ( bin_node.id().slice( 0, 2 ) === BIN_ICON_INITIALS ) {
            bin_pos_x = bin_node.renderedPosition().x;
            bin_pos_y = bin_node.renderedPosition().y;
            bin_height = bin_node.parent().renderedHeight();

            _.each( graphPage.legend.cyLegend.nodes(), function ( node ) {
              node_pos_x = node.renderedPosition().x;
              node_pos_y = node.renderedPosition().y;
              if ( node_pos_y == bin_pos_y && node_pos_x != bin_pos_x && node.id().slice( 0, 1 ) != PARENT_NODE_LEGEND_INITIALS ) {
                /*If this node contains legend label, style_json is updated first and then
                the node is removed*/
                if ( node.style()[ 'label' ] in graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ] ) {
                  delete graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ node.style()[ 'label' ] ];
                }
                if ( node.style()[ 'label' ] in graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ] ) {
                  delete graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ node.style()[ 'label' ] ];
                }
                graphPage.legend.cyLegend.remove( node );
              }
            } );
            // get the parent node corresponding to the tapped the bin node
            var bin_node_parentID = bin_node.parent().id();
            console.log( bin_pos_y, bin_height );
            // remove the tapped bin node
            graphPage.legend.cyLegend.remove( bin_node );
            // finally remove the the parent node corresponding to the tapped the bin node
            graphPage.legend.cyLegend.remove( graphPage.legend.cyLegend.getElementById( bin_node_parentID ) );
            // shift other nodes to occupy the vaccant space
            graphPage.legend.legendEditor.rearrangeLegend( bin_pos_y, bin_height );
            graphPage.legend.decrementLegendInterfaceHeight( bin_height + 'px' );
          }
          if ( bin_node.id().slice( 0, 4 ) === EDIT_ICON_INITIALS ) {
            graphPage.legend.legendEditor.legendLabelEditor.open( bin_node.id() );
          }
        } );

        $( '#addNodeLegendBtn' ).click( function () {
          graphPage.legend.legendEditor.nodeLegendEditor.open();
        } );

        $( '#addEdgeLegendBtn' ).click( function () {
          graphPage.legend.legendEditor.edgeLegendEditor.open();
        } );

        $( '#editSelectedLegendBtn' ).click( function () {
          graphPage.legend.legendEditor.legendLabelEditor.open( graphPage.legend.cyLegend.collection( graphPage.legend.cyLegend.elements( ':selected' ) ) );
        } );
      },
      constructBinLegend: function () {
        /*This function is called when user clicks on the "Use Legend Editor" button available sidebar panel.
         *This function create bin icon adjacent to each legend on the legend interface which provides user the option to remove the legend.
         */
        var node_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ];
        var edge_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ];
        var node_legend_count = Object.keys( node_legend ).length;
        var edge_legend_count = Object.keys( edge_legend ).length;
        var total_elements = node_legend_count + edge_legend_count;
        var factor = graphPage.legend.currentLegendSizeFactor;

        graphPage.legend.cyLegend.nodes( '#sm' ).renderedPosition( {
          y: graphPage.legend.cyLegend.extent()[ 'y1' ] + ( 5 + 5 * factor ),
          x: graphPage.legend.cyLegend.extent()[ 'x2' ]
        } )

        // var y_pos = 35 * factor;
        // var x_pos = 180 * factor;
        // for ( var i = 0; i < total_elements; i++ ) {
        //   graphPage.legend.cyLegend.add( [ {
        //     group: 'nodes',
        //     data: {
        //       id: BIN_ICON_INITIALS + i,
        //       parent: PARENT_NODE_LEGEND_INITIALS + i
        //     },
        //     position: {
        //       y: y_pos + 10,
        //       x: x_pos
        //     }
        //   } ] ).style( {
        //     'background-image': '../images/trash.png',
        //     'background-color': 'white',
        //     'width': 15 * factor + 'px',
        //     'height': 18 * factor + 'px',
        //     'shape': 'rectangle'
        //   } );
        //   y_pos = y_pos + 40 * factor;
        // }

        for ( var i = 0; i < node_legend_count; i++ ) {
          graphPage.legend.cyLegend.add( [ {
            group: 'nodes',
            data: {
              id: BIN_ICON_INITIALS + i,
              parent: PARENT_NODE_LEGEND_INITIALS + i
            },
            position: {
              y: graphPage.legend.cyLegend.nodes( '#' + NODE_LEGEND_INITIALS + i ).position( 'y' ),
              x: graphPage.legend.cyLegend.extent()[ 'x2' ],
            }
          } ] ).style( {
            'background-image': '../images/trash.png',
            'background-fit': 'cover',
            'background-color': 'white',
            'width': 15 * factor + 'px',
            'height': 18 * factor + 'px',
            'shape': 'rectangle'
          } );
        }

        for ( var i = 0; i < edge_legend_count; i++ ) {
          graphPage.legend.cyLegend.add( [ {
            group: 'nodes',
            data: {
              id: BIN_ICON_INITIALS + i + node_legend_count,
              parent: PARENT_NODE_LEGEND_INITIALS + i + node_legend_count
            },
            position: {
              y: graphPage.legend.cyLegend.nodes( '#' + EDGE_NODE_LEGEND_INITIALS + i + '-target' ).position( 'y' ),
              x: graphPage.legend.cyLegend.extent()[ 'x2' ],
            }
          } ] ).style( {
            'background-image': '../images/trash.png',
            'background-fit': 'cover',
            'background-color': 'white',
            'width': 15 * factor + 'px',
            'height': 18 * factor + 'px',
            'shape': 'rectangle'
          } );
        }
      },
      constructEditLegend: function () {
        /*This function is called when user clicks on the "Use Legend Editor" button available sidebar panel.
         *This function create edit icon adjacent to each legend on the legend interface which provides user the option to edit the legend label.
         */
        var node_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ];
        var edge_legend = graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ];
        var node_legend_count = Object.keys( node_legend ).length;
        var edge_legend_count = Object.keys( edge_legend ).length;
        var total_elements = node_legend_count + edge_legend_count;
        var factor = graphPage.legend.currentLegendSizeFactor;

        // var y_pos = 35 * factor;
        // var x_pos = 200 * factor;
        // for ( var i = 0; i < total_elements; i++ ) {
        //   graphPage.legend.cyLegend.add( [ {
        //     group: 'nodes',
        //     data: {
        //       id: EDIT_ICON_INITIALS + i,
        //       parent: PARENT_NODE_LEGEND_INITIALS + i
        //     },
        //     position: {
        //       y: y_pos + 10,
        //       x: x_pos
        //     }
        //   } ] ).style( {
        //     'background-image': '../images/edit_icon.png',
        //     'background-color': 'white',
        //     'width': 15 * factor + 'px',
        //     'height': 18 * factor + 'px',
        //     'shape': 'rectangle'
        //   } );
        //   y_pos = y_pos + 40 * factor;
        // }
        graphPage.legend.cyLegend.nodes( '#sm' ).renderedPosition( {
          y: graphPage.legend.cyLegend.extent()[ 'y1' ] + ( 5 + 5 * factor ),
          x: graphPage.legend.cyLegend.extent()[ 'x2' ] + 25 * factor,
        } )

        for ( var i = 0; i < node_legend_count; i++ ) {
          graphPage.legend.cyLegend.add( [ {
            group: 'nodes',
            data: {
              id: EDIT_ICON_INITIALS + i,
              parent: PARENT_NODE_LEGEND_INITIALS + i
            },
            position: {
              y: graphPage.legend.cyLegend.nodes( '#' + NODE_LEGEND_INITIALS + i ).position( 'y' ),
              x: graphPage.legend.cyLegend.extent()[ 'x2' ] + 25 * factor,
            }
          } ] ).style( {
            'background-image': '../images/edit_icon.png',
            'background-fit': 'cover',
            'background-color': 'white',
            'width': 18 * factor + 'px',
            'height': 18 * factor + 'px',
            'shape': 'rectangle'
          } );
        }

        for ( var i = 0; i < edge_legend_count; i++ ) {
          graphPage.legend.cyLegend.add( [ {
            group: 'nodes',
            data: {
              id: EDIT_ICON_INITIALS + i + node_legend_count,
              parent: PARENT_NODE_LEGEND_INITIALS + i + node_legend_count
            },
            position: {
              y: graphPage.legend.cyLegend.nodes( '#' + EDGE_NODE_LEGEND_INITIALS + i + '-target' ).position( 'y' ),
              x: graphPage.legend.cyLegend.extent()[ 'x2' ] + 25 * factor,
            }
          } ] ).style( {
            'background-image': '../images/edit_icon.png',
            'background-fit': 'cover',
            'background-color': 'white',
            'width': 18 * factor + 'px',
            'height': 18 * factor + 'px',
            'shape': 'rectangle'
          } );
        }

      },
      rearrangeLegend: function ( bin_pos_y, bin_height ) {
        var factor = graphPage.legend.currentLegendSizeFactor;

        _.each( graphPage.legend.cyLegend.nodes(), function ( node ) {
          var node_pos_y = node.renderedPosition().y;
          if ( node_pos_y > bin_pos_y ) {
            graphPage.legend.cyLegend.autolock( false );
            node.animate( {
              position: {
                y: node_pos_y - bin_height
                // y: node_pos_y - 16 * factor * lines
              },
            }, {
              duration: 700
            } );
          }
        } );
      },
      removeBinLegend: function () {
        var factor = graphPage.legend.currentLegendSizeFactor;
        _.each( graphPage.legend.cyLegend.nodes(), function ( node ) {
          node_pos = node.renderedPosition();
          if ( node_pos.x == 180 * factor ) {
            graphPage.legend.cyLegend.remove( node );
          }
        } );
      },
      removeEditLegend: function () {
        var factor = graphPage.legend.currentLegendSizeFactor;
        _.each( graphPage.legend.cyLegend.nodes(), function ( node ) {
          node_pos = node.renderedPosition();
          if ( node_pos.x == 220 * factor ) {
            graphPage.legend.cyLegend.remove( node );
          }
        } );
      },
      legendLabelEditor: {
        legend_label: {},
        init: function () {
          $( '#nodeLegendLabel' ).val( null );
        },
        open: function ( nodeId ) {
          if ( nodeId ) {
            label = graphPage.legend.cyLegend.nodes( '#' + NODE_LEGEND_INITIALS + nodeId.replace( 'edit', '' ) ).style( 'label' );
          } else {
            label = ''
          }
          graphPage.legend.legendEditor.legendLabelEditor.init();
          $( '.gs-sidebar-nav' ).removeClass( 'active' );
          $( '#legendLabelEditorSideBar' ).addClass( 'active' );
          $( '#legendLabel' ).val( label );
          $( '#legendLabel' ).on( 'input', function ( e ) {
            if ( !_.isEmpty( $( '#legendLabel' ).val() ) ) {
              graphPage.legend.legendEditor.legendLabelEditor.legend_label[ 'label' ] = $( '#legendLabel' ).val();
            }
          } );
        },
        updateLegendLabel: function ( label ) {
          collection = graphPage.legend.cyLegend.collection( graphPage.legend.cyLegend.elements( ':selected' ) );
          col_pos = collection.renderedPosition();
          _.each( graphPage.legend.cyLegend.elements(), function ( elem ) {
            if ( elem.isNode() && elem.id().slice( 0, 1 ) == NODE_LEGEND_INITIALS && elem.renderedPosition().y == col_pos.y ) {
              graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ label ] = {};
              graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ label ] = graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ elem.style()[ 'label' ] ];
              delete graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ elem.style()[ 'label' ] ];
              elem.style( 'label', label );
              console.log( graphPage.legend.currentLegendJSON );
            }

            if ( elem.isNode() && elem.id().slice( 0, 2 ) == EDGE_NODE_LEGEND_INITIALS && elem.id().length == 4 && elem.renderedPosition().y == col_pos.y ) {
              graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ label ] = {};
              graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ label ] = graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ elem.style()[ 'label' ] ];
              delete graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ elem.style()[ 'label' ] ];
              elem.style( 'label', label );
              console.log( graphPage.legend.currentLegendJSON );
            }
          } );
        },
        close: function () {
          if ( save ) {
            graphPage.legend.legendEditor.legendLabelEditor.updateLegendLabel( graphPage.legend.legendEditor.legendLabelEditor.legend_label[ 'label' ] );
          }
          $( '.gs-sidebar-nav' ).removeClass( 'active' );
          $( '#legendEditorSideBar' ).addClass( 'active' );
        }
      },
      nodeLegendEditor: {
        node_legend: {},
        init: function () {
          $( '#nodeLegendShape' ).val( null );
          $( '#nodeLegendLabel' ).val( null );
          $( "#nodeLegendBackgroundColorPicker" ).unbind( 'changeColor' ).colorpicker( 'setValue', '#00AABB' );
          $( '#nodeLegendBackgroundColorPicker' ).on( 'changeColor', graphPage.legend.legendEditor.nodeLegendEditor.addNodeLegendBackgroundColor );
        },
        open: function () {
          /*Opens node legend editor. Provides option to select styles to add a new node legend */
          graphPage.legend.legendEditor.nodeLegendEditor.init();
          $( '.gs-sidebar-nav' ).removeClass( 'active' );
          $( '#nodeLegendEditorSideBar' ).addClass( 'active' );


          $( '#nodeLegendBackgroundColorPicker' ).on( 'changeColor', graphPage.legend.legendEditor.nodeLegendEditor.addNodeLegendBackgroundColor() );

          $( '#nodeLegendShape' ).on( 'change', function ( e ) {
            if ( _.isEmpty( $( '#nodeLegendShape' ).val() ) ) {
              return $.notify( {
                message: 'Please enter valid shape value!',
              }, {
                type: 'warning'
              } );
            } else {
              graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'shape' ] = $( '#nodeLegendShape' ).val();
            }
          } );

          $( '#nodeLegendLabel' ).on( 'input', function ( e ) {
            if ( !_.isEmpty( $( '#nodeLegendLabel' ).val() ) ) {
              graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'label' ] = $( '#nodeLegendLabel' ).val();
            }
          } );
        },
        addNodeLegendBackgroundColor: function ( e ) {
          if ( _.isEmpty( $( "#nodeLegendBackgroundColorPicker" ).colorpicker( 'getValue' ) ) ) {
            return $.notify( {
              message: 'Please enter valid color value!',
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'background-color' ] = $( "#nodeLegendBackgroundColorPicker" ).colorpicker( 'getValue' );
          }
        },
        addNodeLegend: function () {
          var n_label = graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'label' ];
          var n_shape = graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'shape' ];
          var n_color = graphPage.legend.legendEditor.nodeLegendEditor.node_legend[ 'background-color' ];

          graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ n_label ] = {};
          graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ n_label ][ 'shape' ] = n_shape;
          graphPage.legend.currentLegendJSON[ 'legend' ][ 'nodes' ][ n_label ][ 'background-color' ] = n_color;

          graphPage.legend.cyLegend.destroy();
          graphPage.legend.resizeLegendInterfaceHeight( "0px" );
          graphPage.legend.cyLegend = graphPage.legend.constructLegend();
          graphPage.legend.legendEditor.init();
        },
        close: function () {
          if ( save ) {
            graphPage.legend.legendEditor.nodeLegendEditor.addNodeLegend();
          } else {
            $( '.gs-sidebar-nav' ).removeClass( 'active' );
            $( '#legendEditorSideBar' ).addClass( 'active' );
          }
          graphPage.legend.legendEditor.nodeLegendEditor.init();
        }
      },
      edgeLegendEditor: {
        edge_legend: {},
        init: function () {
          $( '#edgeLegendStyle' ).val( null );
          $( '#edgeLegendLabel' ).val( null );
          $( '#edgeLegendArrowShape' ).val( null );
          $( "#edgeLegendColorPicker" ).unbind( 'changeColor' ).colorpicker( 'setValue', '#00AABB' );
          $( '#edgeLegendColorPicker' ).on( 'changeColor', graphPage.legend.legendEditor.edgeLegendEditor.addEdgeLegendBackgroundColor );
        },
        open: function () {
          /*Opens edge legend editor. Provides option to select styles to add a new edge legend */
          graphPage.legend.legendEditor.edgeLegendEditor.init();
          $( '.gs-sidebar-nav' ).removeClass( 'active' );
          $( '#edgeLegendEditorSideBar' ).addClass( 'active' );


          $( '#edgeLegendColorPicker' ).on( 'changeColor', graphPage.legend.legendEditor.edgeLegendEditor.addEdgeLegendBackgroundColor() );

          $( '#edgeLegendStyle' ).on( 'change', function ( e ) {
            if ( _.isEmpty( $( '#edgeLegendStyle' ).val() ) ) {
              return $.notify( {
                message: 'Please enter valid style value!',
              }, {
                type: 'warning'
              } );
            } else {
              graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'line-style' ] = $( '#edgeLegendStyle' ).val();
            }
          } );

          $( '#edgeLegendArrowShape' ).on( 'change', function ( e ) {
            if ( _.isEmpty( $( '#edgeLegendArrowShape' ).val() ) ) {
              return $.notify( {
                message: 'Please enter valid arrow shape value!',
              }, {
                type: 'warning'
              } );
            } else {
              graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'arrow-shape' ] = $( '#edgeLegendArrowShape' ).val();
            }
          } );

          $( '#edgeLegendLabel' ).on( 'input', function ( e ) {
            if ( !_.isEmpty( $( '#edgeLegendLabel' ).val() ) ) {
              graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'label' ] = $( '#edgeLegendLabel' ).val();
            }
          } );
        },
        addEdgeLegendBackgroundColor: function ( e ) {
          if ( _.isEmpty( $( "#edgeLegendColorPicker" ).colorpicker( 'getValue' ) ) ) {
            return $.notify( {
              message: 'Please enter valid color value!'
            }, {
              type: 'warning'
            } );
          } else {
            graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'line-color' ] = $( "#edgeLegendColorPicker" ).colorpicker( 'getValue' );
          }
        },
        addEdgeLegend: function () {
          var e_label = graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'label' ];
          var e_style = graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'line-style' ];
          var e_color = graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'line-color' ];
          var e_arrow_shape = graphPage.legend.legendEditor.edgeLegendEditor.edge_legend[ 'arrow-shape' ];

          graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ e_label ] = {};
          graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ e_label ][ 'line-style' ] = e_style;
          graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ e_label ][ 'line-color' ] = e_color;
          graphPage.legend.currentLegendJSON[ 'legend' ][ 'edges' ][ e_label ][ 'arrow-shape' ] = e_arrow_shape;

          graphPage.legend.cyLegend.destroy();
          graphPage.legend.resizeLegendInterfaceHeight( "0px" );
          graphPage.legend.cyLegend = graphPage.legend.constructLegend();
          graphPage.legend.legendEditor.init();
        },
        close: function () {
          if ( save ) {
            graphPage.legend.legendEditor.edgeLegendEditor.addEdgeLegend();
          } else {
            $( '.gs-sidebar-nav' ).removeClass( 'active' );
            $( '#legendEditorSideBar' ).addClass( 'active' );
          }
          graphPage.legend.legendEditor.edgeLegendEditor.init();
        }
      }
    }
  }
};

var layoutLearner = {
  computeLayoutMetadata: function ( cy ) {
    var edgeLengths = cytoscapeGraph.getEdgeLengths( cy );
    var totalEdgeLength = _.sum( edgeLengths );
    var avgEdgeLength = totalEdgeLength / cy.edges().length;
    return {
      'order': cy.nodes().length,
      'size': cy.edges().length,
      'timeTaken': utils.timer( 'lap' ),
      'edgeLengths': edgeLengths,
      'totalEdgeLength': totalEdgeLength,
      'averageEdgeLength': avgEdgeLength,
      'timestamp': moment().format( "YYYY-MM-DD HH:mm:ss" ),
      'edgeOverlapCount': cytoscapeGraph.computeNumEdgeOverlap( cy )
    }
  }
};

var cytoscapeGraph = {
  contextMenu: {
    init: function ( cy ) {
      var selectAllOfTheSameType = function ( ele ) {
        cy.elements().unselect();
        if ( ele.isNode() ) {
          cy.nodes().select();
        } else if ( ele.isEdge() ) {
          cy.edges().select();
        }
      };
      var unselectAllOfTheSameType = function ( ele ) {
        if ( ele.isNode() ) {
          cy.nodes().unselect();
        } else if ( ele.isEdge() ) {
          cy.edges().unselect();
        }
      };

      var cm = graphPage.cyGraph.contextMenus( {
        menuItems: [ {
            id: 'edit-node',
            title: 'edit selected nodes',
            selector: 'node',
            onClickFunction: function ( event ) {
              graphPage.layoutEditor.nodeEditor.open( cy.collection( cy.elements( ':selected' ) ).add( event.cyTarget ).select() );
            },
            hasTrailingDivider: true
          },
          {
            id: 'select-all-nodes',
            title: 'select all nodes',
            selector: 'node',
            show: true,
            onClickFunction: function ( event ) {
              selectAllOfTheSameType( event.cyTarget );
            }
          },
          {
            id: 'unselect-all-nodes',
            title: 'unselect all nodes',
            selector: 'node',
            show: true,
            onClickFunction: function ( event ) {
              unselectAllOfTheSameType( event.cyTarget );
            }
          },
          {
            id: 'select-all-edges',
            title: 'select all edges',
            selector: 'edge',
            show: true,
            onClickFunction: function ( event ) {
              selectAllOfTheSameType( event.cyTarget );
            }
          },
          {
            id: 'unselect-all-edges',
            title: 'unselect all edges',
            selector: 'edge',
            show: true,
            onClickFunction: function ( event ) {
              unselectAllOfTheSameType( event.cyTarget );
            }
          }
        ]
      } );
    }
  },
  getEdgeLengths: function ( cy ) {
    var edgeLengths = [];
    cy.edges().forEach( function ( ele, i, eles ) {
      edgeLengths.push( Math.sqrt( Math.pow( ele._private.rstyle.srcX - ele[ 0 ]._private.rstyle.tgtX, 2 ) + Math.pow( ele[ 0 ]._private.rstyle.srcY - ele[ 0 ]._private.rstyle.tgtY, 2 ) ) );
    } );
    return edgeLengths;
  },
  computeNumEdgeOverlap: function ( cy ) {
    var count = 0;
    var edges = cy.edges();
    for ( var i = 0; i < edges.length; i++ ) {
      for ( var j = i + 1; j < edges.length; j++ ) {
        if ( cytoscapeGraph.hasEdgeOverlap( edges[ i ], edges[ j ] ) ) {
          count++;
        }
      }
    }
    return count;
  },
  hasEdgeOverlap: function ( edge1, edge2 ) {
    result = utils.checkLineIntersection( edge1._private.rstyle.srcX, edge1._private.rstyle.srcY, edge1._private.rstyle.tgtX, edge1._private.rstyle.tgtY, edge2._private.rstyle.srcX, edge2._private.rstyle.srcY, edge2._private.rstyle.tgtX, edge2._private.rstyle.tgtY )
    return !!( result && result.x && result.y && result.onLine1 && result.onLine2 );
  },
  getNodePositions: function ( cy ) {
    /*
     *  gets location of all the nodes so that it can be save later.
     *  cy: cytoscape graph object
     */
    var nodes = cy.elements( 'node' );
    var layout = {};
    for ( var i = 0; i < Object.keys( nodes ).length - 2; i++ ) {
      layout[ nodes[ i ]._private.data.id ] = {
        'x': nodes[ i ]._private.position.x,
        'y': nodes[ i ]._private.position.y
      };
    }
    return layout;
  },
  applyStylesheet: function ( cy, stylesheetJSON ) {
    try {
      stylesheetJSON = cytoscapeGraph.parseStylesheet( stylesheetJSON );
      if ( stylesheetJSON ) {
        var tempCy = cy.style().resetToDefault();
        _.each( stylesheetJSON, function ( elemStyle ) {
          if ( elemStyle[ 'selector' ].indexOf( ':selected' ) == -1 ) {
            tempCy = tempCy.selector( elemStyle[ 'selector' ] ).style( 'css' in elemStyle ? elemStyle[ 'css' ] : elemStyle[ 'style' ] );
          }
        } );
        _.each( selectedElementsStylesheet, function ( elemStyle ) {
          tempCy = tempCy.selector( elemStyle[ 'selector' ] ).style( elemStyle[ 'style' ] );
        } );
        tempCy.update();
        return true;
      } else {
        throw "Invalid cytoscape stylesheet file!"
      }
    } catch ( err ) {
      $.notify( {
        message: 'Invalid cytoscape stylesheet file!'
      }, {
        type: 'danger'
      } );
      return false;
    }
  },
  getStylesheet: function ( cy ) {
    /*
     *  gets stylesheet for the graph.
     *
     *  cy: cytoscape graph object
     */
    var selectedElementStyleAttributes = [ 'overlay-opacity', 'overlay-color', 'overlay-padding' ];
    return _.map( cy.elements(), function ( elem ) {
      return {
        'selector': elem.isNode() ? _.template( "node[name='<%= name %>']" )( {
          'name': elem.data( 'name' )
        } ) : _.template( "edge[name='<%= name %>']" )( {
          'name': elem.data( 'name' )
        } ),
        'style': _.omitBy( _.mapValues( elem._private.style, function ( style ) {
          return style ? ( selectedElementStyleAttributes.indexOf( style[ 'name' ] ) == -1 ? style[ 'strValue' ] : undefined ) : undefined
        } ), _.isNil )
      }
    } );

  },
  export: function ( cy, format, filename ) {
    filename = filename ? filename : 'graph';
    var file = undefined;
    var fileformat = undefined;
    var bob = undefined;
    var MIME_TYPE = undefined;

    if ( format === 'jpg' ) {
      var b64key = 'base64,';
      var b64 = cy.jpg( {
        'full': true
      } ).substring( cy.jpg( {
        'full': true
      } ).indexOf( b64key ) + b64key.length );
      blob = utils.base64ToBlob( b64, 'image/jpeg' );
      fileformat = '.jpg';
    } else if ( format === 'png' ) {
      var b64key = 'base64,';
      var b64 = cy.png( {
        'full': true
      } ).substring( cy.png( {
        'full': true
      } ).indexOf( b64key ) + b64key.length );
      blob = utils.base64ToBlob( b64, 'image/png' );
      fileformat = '.png';
    } else if ( format === 'cyjs' ) {
      MIME_TYPE = "application/json";
      blob = new Blob( [ JSON.stringify( cytoscapeGraph.getNetworkAndViewJSON( cy ), null, 4 ) ], {
        type: MIME_TYPE
      } );
      fileformat = '.cyjs';
    } else if ( format === 'style' ) {
      MIME_TYPE = "application/json";
      blob = new Blob( [ JSON.stringify( cytoscapeGraph.getStyleJSON( cy ), null, 4 ) ], {
        type: MIME_TYPE
      } );
      fileformat = '.json';
    } else {
      MIME_TYPE = "application/json";
      blob = new Blob( [ JSON.stringify( cytoscapeGraph.getNetworkJSON( cy ), null, 4 ) ], {
        type: MIME_TYPE
      } );
      fileformat = '.cyjs';
    }
    file = window.URL.createObjectURL( blob );
    var link = $( '<a>' ).attr( 'href', file ).attr( 'download', filename + fileformat );
    $( 'body' ).append( link );
    link.get( 0 ).click();
    link.get( 0 ).remove();
  },
  getNetworkJSON: function ( cy ) {
    return {
      "format_version": "1.0",
      "generated_by": "graphspace-2.0.0",
      "target_cytoscapejs_version": "~2.7",
      'elements': {
        'nodes': _.map( cy.nodes(), function ( elem ) {
          return {
            'data': elem.data()
          }
        } ),
        'edges': _.map( cy.edges(), function ( elem ) {
          return {
            'data': elem.data(),
            'style': _.omitBy( _.mapValues( elem._private.style, function ( style ) {
              return style ? style[ 'strValue' ] : undefined
            } ), _.isNil )
          }
        } )
      },
      'data': graph_json[ 'data' ]
    };
  },
  getNetworkAndViewJSON: function ( cy ) {
    return {
      "format_version": "1.0",
      "generated_by": "graphspace-2.0.0",
      "target_cytoscapejs_version": "~2.7",
      'elements': {
        'nodes': _.map( cy.nodes(), function ( elem ) {
          return {
            'data': elem.data(),
            'position': elem.position()
          }
        } ),
        'edges': _.map( cy.edges(), function ( elem ) {
          return {
            'data': elem.data(),
            'style': _.omitBy( _.mapValues( elem._private.style, function ( style ) {
              return style ? style[ 'strValue' ] : undefined
            } ), _.isNil )
          }
        } )
      },
      'data': graph_json[ 'data' ]
    };
  },
  getStyleJSON: function ( cy ) {
    return {
      "format_version": "1.0",
      "generated_by": "graphspace-2.0.0",
      "target_cytoscapejs_version": "~2.7",
      'style': cytoscapeGraph.getStylesheet( cy ),
      'legend': graphPage.legend.currentLegendJSON[ 'legend' ]
    };
  },
  getAutomaticLayoutSettings: function ( layout_name ) {
    //The following code retrieves the specified layout
    //of a graph to be displayed.
    //Some of them are pre-defined. Check Cytoscapejs.org
    var graph_layout = {
      name: 'random',
      padding: 10,
      fit: true,
      animate: false
    };

    if ( layout_name == "breadthfirst" ) {
      graph_layout = {
        name: "breadthfirst",
        padding: 10,
        fit: true,
        avoidOverlap: true,
        animate: false
      }
    } else if ( layout_name == "concentric" ) {
      graph_layout = {
        name: "concentric",
        fit: true,
        padding: 10,
        avoidOverlap: true,
        animate: false
      }
    } else if ( layout_name == "circle" ) {
      graph_layout = {
        name: "circle",
        padding: 10,
        fit: true,
        avoidOverlap: true,
        animate: false
      }
    } else if ( layout_name == 'cose' ) {
      graph_layout = {
        name: "cose"
      }
    } else if ( layout_name == "grid" ) {
      graph_layout = {
        name: "grid"
      }
    } else if ( layout_name == "cola" ) {
      //console.log("here");
      graph_layout = {
        name: 'cola',
        nodeSpacing: cola_node_space,
        edgeLength: cola_edge_length,
        animate: true,
        randomize: cola_randomize,
        avoidOverlap: cola_avoid_overlap,
        fit: cola_avoid_overlap,
        flow: cola_flow,
        infinite: cola_infinite,
        maxSimulationTime: 1500
      }
    }
    return graph_layout;
  },
  hideGraphInformation: function ( cy ) {
    /*
     Function to hide information about the graph that the layout editor doesn't need to see.
     */
    cy.style()
      .selector( 'node' ).style( {
        'text-opacity': function ( ele ) {
          graphPage.layoutEditor.original_opacity[ ele.data().id ] = ele.style()[ 'text-opacity' ];

          return 0;
        }
      } )
      .update(); // update the elements in the graph with the new style

  },
  showGraphInformation: function ( cy ) {
    /*
    Function to Show information about the graph that the layout editor hid from the users.
    */
    console.log( cy.style().selector( 'node' ) );
    cy.style()
      .selector( 'node' ).style( {
        'text-opacity': function ( ele ) {
          return graphPage.layoutEditor.original_opacity[ ele.data().id ];
        }
      } )
      .update();
    console.log( 'done' );
  },
  getRenderedNodePositionsMap: function ( cy ) {
    var result = {};
    _.each( cy.nodes(), function ( node ) {
      result[ node.id() ] = node.renderedPosition();
    } );
    return result;
  },
  setRenderedNodePositions: function ( cy, positions ) {
    _.each( cy.nodes(), function ( node ) {
      node.renderedPosition( positions[ node.id() ] );
    } );
  },
  unSelectAllNodes: function ( cy ) {
    _.each( cy.nodes(), function ( node ) {
      node.unselect();
    } );
  },
  unSelectAllEdges: function ( cy ) {
    _.each( cy.edges(), function ( edge ) {
      edge.unselect();
    } );
  },
  getAllSelectedNodes: function ( cy ) {
    return _.filter( cy.nodes(), function ( node ) {
      return node.selected();
    } );
  },
  applyLayoutToCollection: function ( cy, collection, layout_name ) {
    if ( layout_name === "circle" ) {
      collection.layout( {
        name: "circle",
        fit: false,
        avoidOverlap: false,
        padding: 0
      } );
    } else if ( layout_name === "fill_circle" ) {
      collection.layout( {
        name: "concentric",
        fit: false,
        avoidOverlap: false,
        padding: 40
      } );
    } else if ( layout_name === "grid" ) {
      collection.layout( {
        name: "grid",
        fit: false,
        avoidOverlap: true,
        condense: true
      } );
    } else if ( layout_name === "square" ) {
      cytoscapeGraph.runSquareLayoutOnCollection( cy, collection );
    } else if ( layout_name === "horizontal" ) {
      cytoscapeGraph.runHorizontalVerticalLayoutOnCollection( cy, collection, "horizontal" );
    } else if ( layout_name === "vertical" ) {
      cytoscapeGraph.runHorizontalVerticalLayoutOnCollection( cy, collection, "vertical" );
    } else if ( layout_name === "release" ) {
      cytoscapeGraph.runSqueezeReleaseOnCollection( collection, "release" );
    } else if ( layout_name === "squeeze" ) {
      cytoscapeGraph.runSqueezeReleaseOnCollection( collection, "squeeze" );
    }
  },
  runSqueezeReleaseOnCollection: function ( collection, type ) {
    var data = cytoscapeGraph.computeCollectionCentroid( collection );

    var centroid = data[ 0 ];
    var selectedNodes = collection.nodes();

    for ( var i = 0; i < selectedNodes.length; i++ ) {
      var node = selectedNodes[ i ];
      var position = node.renderedPosition();
      var distance = cytoscapeGraph.travelDistance( centroid, position );

      if ( !isNaN( position.x ) ) {
        if ( position.x < centroid.x ) {
          if ( type === 'squeeze' ) {
            position.x += distance.x;
          } else {
            position.x -= distance.x;
          }

        }
        if ( position.x > centroid.x ) {
          if ( type == 'squeeze' ) {
            position.x -= distance.x;
          } else {
            position.x += distance.x;
          }
        }
      }

      if ( !isNaN( position.y ) ) {
        if ( position.y < centroid.y ) {
          if ( type == 'squeeze' ) {
            position.y += distance.y;
          } else {
            position.y -= distance.y;
          }
        }
        if ( position.y > centroid.y ) {
          if ( type == 'squeeze' ) {
            position.y -= distance.y;
          } else {
            position.y += distance.y;
          }
        }
      }

      if ( !isNaN( position.x ) && !isNaN( position.y ) ) {
        node.renderedPosition( position );
      }
    }
  },
  runSquareLayoutOnCollection: function ( cy, collection ) {
    var minDistance = 0;
    var selectedArray = [];

    _.each( collection.nodes(), function ( node ) {
      selectedArray.push( node );
      minDistance = Math.max( node.boundingBox()[ "h" ], minDistance );
    } );

    //calculate center of the viewport
    var center = {
      x: cy.width() / 2,
      y: cy.height() / 2
    };


    var radius = ( selectedArray.length / 4 * minDistance ) / 2;

    if ( selectedArray.length <= 4 ) {

      if ( selectedArray.length == 0 ) {
        return;
      } else if ( selectedArray.length == 1 ) {
        var newPosition = {
          "x": center.x,
          "y": center.y
        }
        selectedArray[ 0 ].renderedPosition( newPosition );
      } else if ( selectedArray.length == 2 ) {
        var newPosition = {
          "x": center.x,
          "y": center.y + radius + minDistance
        }
        selectedArray[ 0 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x,
          "y": center.y - radius
        }
        selectedArray[ 1 ].renderedPosition( newPosition );

      } else if ( selectedArray.length == 3 ) {
        var newPosition = {
          "x": center.x - radius,
          "y": center.y - radius
        }
        selectedArray[ 0 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x + radius + minDistance,
          "y": center.y - radius
        }
        selectedArray[ 1 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x + radius + minDistance,
          "y": center.y + radius + minDistance
        }
        selectedArray[ 2 ].renderedPosition( newPosition );

      } else if ( selectedArray.length == 4 ) {
        var newPosition = {
          "x": center.x - radius,
          "y": center.y - radius
        }
        selectedArray[ 0 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x + radius + minDistance,
          "y": center.y - radius
        }
        selectedArray[ 1 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x + radius + minDistance,
          "y": center.y + radius + minDistance
        }
        selectedArray[ 2 ].renderedPosition( newPosition );
        var newPosition = {
          "x": center.x - radius,
          "y": center.y + radius + minDistance
        }
        selectedArray[ 3 ].renderedPosition( newPosition );
      }
      return;
    }

    //Group into regions (top, bottom, left, right) Assuem that we have at least 4 selected elements

    //Top region
    var topBar = selectedArray.slice( 0, selectedArray.length / 4 );

    for ( var i = 0; i < topBar.length; i++ ) {
      var newPosition = {
        "x": center.x - radius + ( i * minDistance ),
        "y": center.y - radius
      }
      topBar[ i ].renderedPosition( newPosition );
    }

    //Bottom Region
    var bottomBar = selectedArray.slice( selectedArray.length / 4, 2 * selectedArray.length / 4 );

    for ( var i = 0; i < bottomBar.length; i++ ) {
      var newPosition = {
        "x": center.x - radius + ( i * minDistance ),
        "y": center.y + radius
      }
      bottomBar[ i ].renderedPosition( newPosition );
    }

    //Left Region
    var leftBar = selectedArray.slice( 2 * selectedArray.length / 4, 3 * selectedArray.length / 4 );

    for ( var i = 0; i < leftBar.length; i++ ) {
      var newPosition = {
        "x": center.x - radius,
        "y": center.y - radius + ( i * minDistance )
      }
      leftBar[ i ].renderedPosition( newPosition );
    }

    //Right Region
    var rightBar = selectedArray.slice( 3 * selectedArray.length / 4, 4 * selectedArray.length );

    for ( var i = 0; i < rightBar.length; i++ ) {
      var newPosition = {
        "x": center.x + radius,
        "y": center.y - radius + ( i * minDistance )
      }
      rightBar[ i ].renderedPosition( newPosition );
    }
  },
  runHorizontalVerticalLayoutOnCollection: function ( cy, collection, layout_name ) {
    var data = cytoscapeGraph.computeCollectionCentroid( collection );
    console.log( layout_name, layout_name === "vertical" ? 1 : 2 );
    var center = {
      x: cy.width() / 2,
      y: cy.height() / 2
    };

    var selectedNodes = collection.nodes();
    var minDistance = data[ layout_name === "vertical" ? 2 : 1 ];

    var radius = ( selectedNodes.length / 4 * minDistance ) / 2;

    for ( var i = 0; i < selectedNodes.length; i++ ) {
      if ( layout_name === "vertical" ) {
        var newPosition = {
          "x": center.x,
          "y": center.y - radius + ( i * minDistance )
        };
      } else {
        var newPosition = {
          "x": center.x - radius + ( i * minDistance ),
          "y": center.y
        };
      }

      selectedNodes[ i ].renderedPosition( newPosition );
    }
  },
  computeCollectionCentroid: function ( collection ) {
    var centroid = {
      x: 0,
      y: 0
    };
    var minWidthDistance = 0;
    var minHeightDistance = 0;

    _.each( collection.nodes(), function ( node ) {
      var position = node.renderedPosition();
      centroid[ "x" ] += position.x;
      centroid[ "y" ] += position.y;
      minWidthDistance = Math.max( node.boundingBox()[ "w" ], minWidthDistance );
      minHeightDistance = Math.max( node.boundingBox()[ "h" ], minHeightDistance );
    } );

    centroid[ "x" ] /= collection.nodes().length;
    centroid[ "y" ] /= collection.nodes().length;

    return [ centroid, minWidthDistance, minHeightDistance ];
  },
  travelDistance: function ( center, nodePosition ) {
    var a = Math.abs( center.x - nodePosition.x );
    var b = Math.abs( center.y - nodePosition.y );

    if ( a == 0 ) {
      a = 1;
    }

    var ratio = b / a;

    var miniH = Math.sqrt( 1 + ratio * ratio );

    var distance = 0.10 * Math.sqrt( a * a + b * b );
    var travelX = distance / miniH;
    var travelY = ratio * travelX;

    return {
      x: travelX,
      y: travelY
    };
  },
  parseStylesheet: function ( styleJSON ) {
    styleJSON = _.isArray( styleJSON ) ? styleJSON : [ styleJSON ];
    return _.filter( _.flatten( _.map( styleJSON, function ( stylesheet ) {
      return _.map( stylesheet.style || [], function ( elemStyle ) {
        return _.mapKeys( elemStyle, function ( value, key ) {
          return key == 'css' ? 'style' : key;
        } );
      } )
    } ) ), function ( elemStyle ) {
      return elemStyle[ 'selector' ].indexOf( ':selected' ) == -1;
    } );
  }

};
//vars
var parent_nodes = [];

//variables for cola
//Different from other layout options, cola can choose options for other variables
//Initial edge length set up to 45 in range of 1 to 400
var cola_edge_length = 150;
//Initial node space set up for 5 in range of 1 to 50
var cola_node_space = 5;

var cola_fit = true;
var cola_randomize = false;
var cola_avoid_overlap = true;
var cola_flow = undefined;
var cola_infinite = false;

var BIN_ICON_INITIALS = "rm";
var EDIT_ICON_INITIALS = "edit";
var EDGE_NODE_LEGEND_INITIALS = "en";
var EDGE_LEGEND_INITIALS = "e";
var NODE_LEGEND_INITIALS = "n";
var PARENT_NODE_LEGEND_INITIALS = "p";
