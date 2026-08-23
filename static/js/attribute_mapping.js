/**
 * Visual Attribute Mapping — attribute discovery from graph_json.
 */
var attributeMapping = {
  RESERVED_NODE_ATTRS: [ 'id', 'name', 'label', 'aliases', 'popup', 'k', 'parent' ],
  RESERVED_EDGE_ATTRS: [ 'id', 'source', 'target', 'name', 'is_directed', 'popup', 'k' ],

  discoveredAttributes: null,
  styleBeforeMapping: null,
  appliedMappings: [],
  lastSavedMapping: null,

  COLOR_VISUAL_PROPERTIES: [ 'background-color', 'line-color' ],

  DEFAULT_COLORS: [
    '#3366cc', '#dc3912', '#ff9900', '#109618',
    '#990099', '#0099c6', '#dd4477', '#66aa00'
  ],

  DEFAULT_MIN_NODE_SIZE: 30,
  DEFAULT_MAX_NODE_SIZE: 80,
  DEFAULT_MIN_EDGE_WIDTH: 2,
  DEFAULT_MAX_EDGE_WIDTH: 10,

  NODE_SHAPES: [
    'ellipse', 'rectangle', 'roundrectangle', 'triangle',
    'diamond', 'pentagon', 'hexagon', 'heptagon',
    'octagon', 'star', 'vee', 'rhomboid'
  ],

  EDGE_LINE_STYLES: [ 'solid', 'dashed', 'dotted' ],

  VISUAL_PROPERTIES: {
    node: [
      { id: 'background-color', label: 'Node color', discrete: true, continuous: true },
      { id: 'width', label: 'Node size', discrete: false, continuous: true },
      { id: 'shape', label: 'Node shape', discrete: true, continuous: false }
    ],
    edge: [
      { id: 'line-color', label: 'Edge color', discrete: true, continuous: true },
      { id: 'width', label: 'Edge width', discrete: false, continuous: true },
      { id: 'line-style', label: 'Edge style', discrete: true, continuous: false }
    ]
  },

  init: function () {
    if ( typeof graph_json === 'undefined' || !graph_json ) {
      this.discoveredAttributes = { nodes: {}, edges: {} };
      return;
    }
    this.discoveredAttributes = this.extractAttributes( graph_json );
  },

  extractAttributes: function ( graphJson ) {
    if ( !graphJson || !graphJson.elements ) {
      return { nodes: {}, edges: {} };
    }

    return {
      nodes: this._scanElements( graphJson.elements.nodes, this.RESERVED_NODE_ATTRS ),
      edges: this._scanElements( graphJson.elements.edges, this.RESERVED_EDGE_ATTRS )
    };
  },

  _scanElements: function ( elements, reserved ) {
    var attrs = {};
    var self = this;

    _.each( elements || [], function ( el ) {
      _.each( el.data || {}, function ( value, key ) {
        if ( reserved.indexOf( key ) !== -1 ) {
          return;
        }
        if ( !attrs[ key ] ) {
          attrs[ key ] = { values: [] };
        }
        if ( value !== null && value !== undefined && value !== '' ) {
          attrs[ key ].values.push( value );
        }
      } );
    } );

    var result = {};
    _.each( attrs, function ( info, key ) {
      result[ key ] = self._classifyAttribute( info.values );
    } );
    return result;
  },

  _classifyAttribute: function ( values ) {
    var unique = _.uniq( values );
    var allNumeric = unique.length > 0 && _.every( unique, function ( v ) {
      return !isNaN( parseFloat( v ) ) && isFinite( v );
    } );

    if ( allNumeric ) {
      var nums = _.map( unique, parseFloat );
      return {
        type: 'numerical',
        min: _.min( nums ),
        max: _.max( nums ),
        count: values.length
      };
    }

    return {
      type: 'categorical',
      values: unique.sort(),
      count: values.length
    };
  },

  bindPanelEvents: function () {
    $( '#mapAttributesBtn' ).off( 'click' ).on( 'click', function ( e ) {
      e.preventDefault();
      attributeMapping.openPanel();
    } );

    $( '#backToLayoutEditorBtn' ).off( 'click' ).on( 'click', function ( e ) {
      e.preventDefault();
      attributeMapping.closePanel();
    } );

    $( '#applyMappingBtn' ).off( 'click' ).on( 'click', function ( e ) {
      e.preventDefault();
      attributeMapping.applyMapping();
    } );

    $( '#resetMappingBtn' ).off( 'click' ).on( 'click', function ( e ) {
      e.preventDefault();
      attributeMapping.resetMapping();
    } );

    this.bindFormEvents();
  },

  bindFormEvents: function () {
    $( '#mappingElementType' ).off( 'change' ).on( 'change', function () {
      $( '#mappingMappingType' ).val( 'discrete' );
      attributeMapping.populateAttributeDropdown();
      attributeMapping.populateVisualPropertyDropdown();
      attributeMapping.updateMappingConfig();
    } );

    $( '#mappingAttribute' ).off( 'change' ).on( 'change', function () {
      attributeMapping.syncMappingTypeFromAttribute();
      attributeMapping.updateMappingConfig();
    } );

    $( '#mappingMappingType' ).off( 'change' ).on( 'change', function () {
      attributeMapping.populateVisualPropertyDropdown();
      attributeMapping.updateMappingConfig();
    } );

    $( '#mappingVisualProperty' ).off( 'change' ).on( 'change', function () {
      attributeMapping.updateMappingConfig();
    } );
  },

  getSelectedElementType: function () {
    var elementType = $( '#mappingElementType' ).val();
    return elementType === 'edge' ? 'edge' : 'node';
  },

  getSelectedMappingType: function () {
    return $( '#mappingMappingType' ).val() === 'continuous' ? 'continuous' : 'discrete';
  },

  getVisualPropertiesForSelection: function () {
    var elementType = this.getSelectedElementType();
    var mappingType = this.getSelectedMappingType();
    var properties = this.VISUAL_PROPERTIES[ elementType ] || [];

    return _.filter( properties, function ( property ) {
      return mappingType === 'continuous' ? property.continuous : property.discrete;
    } );
  },

  getAttributesForElementType: function ( elementType ) {
    var discovered = this.discoveredAttributes || { nodes: {}, edges: {} };
    return elementType === 'edge' ? discovered.edges : discovered.nodes;
  },

  getSelectedAttributeMeta: function () {
    var attributeName = $( '#mappingAttribute' ).val();
    if ( !attributeName ) {
      return null;
    }

    var attributeMap = this.getAttributesForElementType( this.getSelectedElementType() );
    return attributeMap[ attributeName ] || null;
  },

  syncMappingTypeFromAttribute: function () {
    var meta = this.getSelectedAttributeMeta();
    if ( !meta ) {
      this.populateVisualPropertyDropdown();
      return;
    }

    var mappingType = meta.type === 'numerical' ? 'continuous' : 'discrete';
    $( '#mappingMappingType' ).val( mappingType );
    this.populateVisualPropertyDropdown();
  },

  isColorVisualProperty: function ( propertyId ) {
    return this.COLOR_VISUAL_PROPERTIES.indexOf( propertyId ) !== -1;
  },

  isWidthVisualProperty: function ( propertyId ) {
    return propertyId === 'width';
  },

  isNodeWidthVisualProperty: function ( propertyId, elementType ) {
    return this.isWidthVisualProperty( propertyId ) && elementType === 'node';
  },

  isEdgeWidthVisualProperty: function ( propertyId, elementType ) {
    return this.isWidthVisualProperty( propertyId ) && elementType === 'edge';
  },

  isNodeShapeVisualProperty: function ( propertyId, elementType ) {
    return propertyId === 'shape' && elementType === 'node';
  },

  isEdgeStyleVisualProperty: function ( propertyId, elementType ) {
    return propertyId === 'line-style' && elementType === 'edge';
  },

  getDefaultShape: function ( index ) {
    return this.NODE_SHAPES[ index % this.NODE_SHAPES.length ];
  },

  getDefaultLineStyle: function ( index ) {
    return this.EDGE_LINE_STYLES[ index % this.EDGE_LINE_STYLES.length ];
  },

  isSelectionComplete: function () {
    return !!(
      $( '#mappingAttribute' ).val() &&
      $( '#mappingVisualProperty' ).val()
    );
  },

  getColorPickerValue: function ( $picker ) {
    if ( $picker.data( 'colorpicker' ) ) {
      return $picker.colorpicker( 'getValue' );
    }
    return $picker.find( 'input' ).val();
  },

  isDiscreteColorMappingReady: function () {
    if ( !this.isSelectionComplete() ) {
      return false;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();

    return !!(
      meta &&
      meta.type === 'categorical' &&
      this.getSelectedMappingType() === 'discrete' &&
      this.isColorVisualProperty( visualProperty ) &&
      $( '#mappingConfigContent .mapping-discrete-color' ).length > 0
    );
  },

  getDiscreteColorMappingFromUI: function () {
    if ( !this.isDiscreteColorMappingReady() ) {
      return null;
    }

    var valueColors = {};
    var self = this;
    var hasEmptyColor = false;

    $( '#mappingConfigContent .mapping-discrete-color' ).each( function () {
      var $picker = $( this );
      var categoryValue = $picker.attr( 'data-category-value' );
      var color = self.getColorPickerValue( $picker );

      if ( !color ) {
        hasEmptyColor = true;
        return false;
      }

      valueColors[ categoryValue ] = color;
    } );

    if ( hasEmptyColor || _.isEmpty( valueColors ) ) {
      return null;
    }

    return {
      elementType: this.getSelectedElementType(),
      attribute: $( '#mappingAttribute' ).val(),
      visualProperty: $( '#mappingVisualProperty' ).val(),
      mappingType: 'discrete',
      valueColors: valueColors
    };
  },

  isDiscreteShapeMappingReady: function () {
    if ( !this.isSelectionComplete() ) {
      return false;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();
    var elementType = this.getSelectedElementType();

    return !!(
      meta &&
      meta.type === 'categorical' &&
      this.getSelectedMappingType() === 'discrete' &&
      this.isNodeShapeVisualProperty( visualProperty, elementType ) &&
      $( '#mappingConfigContent .mapping-discrete-shape' ).length > 0
    );
  },

  getDiscreteShapeMappingFromUI: function () {
    if ( !this.isDiscreteShapeMappingReady() ) {
      return null;
    }

    var valueShapes = {};
    var hasEmptyShape = false;

    $( '#mappingConfigContent .mapping-discrete-shape' ).each( function () {
      var $select = $( this );
      var categoryValue = $select.attr( 'data-category-value' );
      var shape = $select.val();

      if ( !shape ) {
        hasEmptyShape = true;
        return false;
      }

      valueShapes[ categoryValue ] = shape;
    } );

    if ( hasEmptyShape || _.isEmpty( valueShapes ) ) {
      return null;
    }

    return {
      elementType: 'node',
      attribute: $( '#mappingAttribute' ).val(),
      visualProperty: 'shape',
      mappingType: 'discrete',
      valueShapes: valueShapes
    };
  },

  isDiscreteEdgeStyleMappingReady: function () {
    if ( !this.isSelectionComplete() ) {
      return false;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();
    var elementType = this.getSelectedElementType();

    return !!(
      meta &&
      meta.type === 'categorical' &&
      this.getSelectedMappingType() === 'discrete' &&
      this.isEdgeStyleVisualProperty( visualProperty, elementType ) &&
      $( '#mappingConfigContent .mapping-discrete-line-style' ).length > 0
    );
  },

  getDiscreteEdgeStyleMappingFromUI: function () {
    if ( !this.isDiscreteEdgeStyleMappingReady() ) {
      return null;
    }

    var valueStyles = {};
    var hasEmptyStyle = false;

    $( '#mappingConfigContent .mapping-discrete-line-style' ).each( function () {
      var $select = $( this );
      var categoryValue = $select.attr( 'data-category-value' );
      var lineStyle = $select.val();

      if ( !lineStyle ) {
        hasEmptyStyle = true;
        return false;
      }

      valueStyles[ categoryValue ] = lineStyle;
    } );

    if ( hasEmptyStyle || _.isEmpty( valueStyles ) ) {
      return null;
    }

    return {
      elementType: 'edge',
      attribute: $( '#mappingAttribute' ).val(),
      visualProperty: 'line-style',
      mappingType: 'discrete',
      valueStyles: valueStyles
    };
  },

  isContinuousColorMappingReady: function () {
    if ( !this.isSelectionComplete() ) {
      return false;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();

    return !!(
      meta &&
      meta.type === 'numerical' &&
      this.getSelectedMappingType() === 'continuous' &&
      this.isColorVisualProperty( visualProperty ) &&
      $( '#mappingConfigContent .mapping-continuous-low' ).length > 0 &&
      $( '#mappingConfigContent .mapping-continuous-high' ).length > 0
    );
  },

  getContinuousColorMappingFromUI: function () {
    if ( !this.isContinuousColorMappingReady() ) {
      return null;
    }

    var meta = this.getSelectedAttributeMeta();
    var lowColor = this.getColorPickerValue( $( '#mappingConfigContent .mapping-continuous-low' ) );
    var highColor = this.getColorPickerValue( $( '#mappingConfigContent .mapping-continuous-high' ) );

    if ( !lowColor || !highColor ) {
      return null;
    }

    return {
      elementType: this.getSelectedElementType(),
      attribute: $( '#mappingAttribute' ).val(),
      visualProperty: $( '#mappingVisualProperty' ).val(),
      mappingType: 'continuous',
      min: meta.min,
      max: meta.max,
      lowColor: lowColor,
      highColor: highColor
    };
  },

  getMappingFromUI: function () {
    return this.getDiscreteColorMappingFromUI() ||
      this.getDiscreteShapeMappingFromUI() ||
      this.getDiscreteEdgeStyleMappingFromUI() ||
      this.getContinuousColorMappingFromUI() ||
      this.getContinuousWidthMappingFromUI();
  },

  _parsePositiveNumber: function ( value ) {
    var number = parseFloat( value );
    return !isNaN( number ) && isFinite( number ) && number > 0 ? number : null;
  },

  isContinuousWidthMappingReady: function () {
    if ( !this.isSelectionComplete() ) {
      return false;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();

    return !!(
      meta &&
      meta.type === 'numerical' &&
      this.getSelectedMappingType() === 'continuous' &&
      this.isWidthVisualProperty( visualProperty ) &&
      $( '#mappingConfigContent .mapping-continuous-width-min' ).length > 0 &&
      $( '#mappingConfigContent .mapping-continuous-width-max' ).length > 0
    );
  },

  getContinuousWidthMappingFromUI: function () {
    if ( !this.isContinuousWidthMappingReady() ) {
      return null;
    }

    var meta = this.getSelectedAttributeMeta();
    var elementType = this.getSelectedElementType();
    var minSize = this._parsePositiveNumber(
      $( '#mappingConfigContent .mapping-continuous-width-min' ).val()
    );
    var maxSize = this._parsePositiveNumber(
      $( '#mappingConfigContent .mapping-continuous-width-max' ).val()
    );

    if ( !minSize || !maxSize ) {
      return null;
    }

    return {
      elementType: elementType,
      attribute: $( '#mappingAttribute' ).val(),
      visualProperty: 'width',
      mappingType: 'continuous',
      min: meta.min,
      max: meta.max,
      minSize: minSize,
      maxSize: maxSize
    };
  },

  _formatSelectorAttributeValue: function ( value ) {
    return '"' + String( value ).replace( /\\/g, '\\\\' ).replace( /"/g, '\\"' ) + '"';
  },

  _buildAttributeSelector: function ( elementType, attribute, value ) {
    var elementSelector = elementType === 'edge' ? 'edge' : 'node';
    return elementSelector + '[' + attribute + ' = ' + this._formatSelectorAttributeValue( value ) + ']';
  },

  _buildDiscreteColorStyle: function ( visualProperty, color ) {
    if ( visualProperty === 'background-color' ) {
      return {
        'background-color': color,
        'text-outline-color': color
      };
    }

    if ( visualProperty === 'line-color' ) {
      return {
        'line-color': color,
        'target-arrow-color': color,
        'source-arrow-color': color
      };
    }

    var style = {};
    style[ visualProperty ] = color;
    return style;
  },

  buildDiscreteColorStyleRules: function ( mapping ) {
    if ( !mapping || mapping.mappingType !== 'discrete' || !mapping.valueColors ) {
      return [];
    }

    var self = this;
    var elementType = mapping.elementType === 'edge' ? 'edge' : 'node';

    return _.map( mapping.valueColors, function ( color, categoryValue ) {
      return {
        selector: self._buildAttributeSelector( elementType, mapping.attribute, categoryValue ),
        style: self._buildDiscreteColorStyle( mapping.visualProperty, color )
      };
    } );
  },

  buildDiscreteShapeStyleRules: function ( mapping ) {
    if ( !mapping || mapping.mappingType !== 'discrete' || !mapping.valueShapes ) {
      return [];
    }

    var self = this;

    return _.map( mapping.valueShapes, function ( shape, categoryValue ) {
      return {
        selector: self._buildAttributeSelector( 'node', mapping.attribute, categoryValue ),
        style: {
          shape: shape
        }
      };
    } );
  },

  buildDiscreteEdgeStyleStyleRules: function ( mapping ) {
    if ( !mapping || mapping.mappingType !== 'discrete' || !mapping.valueStyles ) {
      return [];
    }

    var self = this;

    return _.map( mapping.valueStyles, function ( lineStyle, categoryValue ) {
      return {
        selector: self._buildAttributeSelector( 'edge', mapping.attribute, categoryValue ),
        style: {
          'line-style': lineStyle
        }
      };
    } );
  },

  _buildMapDataValue: function ( attribute, min, max, minMapper, maxMapper ) {
    var mapMax = min === max ? max + 1 : max;
    return 'mapData(' + attribute + ', ' + min + ', ' + mapMax + ', ' + minMapper + ', ' + maxMapper + ')';
  },

  _buildContinuousColorStyle: function ( visualProperty, mapDataValue ) {
    if ( visualProperty === 'background-color' ) {
      return {
        'background-color': mapDataValue,
        'text-outline-color': mapDataValue
      };
    }

    if ( visualProperty === 'line-color' ) {
      return {
        'line-color': mapDataValue,
        'target-arrow-color': mapDataValue,
        'source-arrow-color': mapDataValue
      };
    }

    var style = {};
    style[ visualProperty ] = mapDataValue;
    return style;
  },

  buildContinuousColorStyleRules: function ( mapping ) {
    if ( !mapping || mapping.mappingType !== 'continuous' ) {
      return [];
    }

    var elementType = mapping.elementType === 'edge' ? 'edge' : 'node';
    var selector = elementType + '[' + mapping.attribute + ']';
    var mapDataValue = this._buildMapDataValue(
      mapping.attribute,
      mapping.min,
      mapping.max,
      mapping.lowColor,
      mapping.highColor
    );

    return [ {
      selector: selector,
      style: this._buildContinuousColorStyle( mapping.visualProperty, mapDataValue )
    } ];
  },

  buildContinuousWidthStyleRules: function ( mapping ) {
    if ( !mapping || mapping.mappingType !== 'continuous' || mapping.visualProperty !== 'width' ) {
      return [];
    }

    var elementType = mapping.elementType === 'edge' ? 'edge' : 'node';
    var selector = elementType + '[' + mapping.attribute + ']';
    var mapDataValue = this._buildMapDataValue(
      mapping.attribute,
      mapping.min,
      mapping.max,
      mapping.minSize,
      mapping.maxSize
    );

    var style = {
      width: mapDataValue
    };

    // Keep nodes proportional by scaling height with width.
    if ( elementType === 'node' ) {
      style.height = mapDataValue;
    }

    return [ {
      selector: selector,
      style: style
    } ];
  },

  buildStyleRules: function ( mapping ) {
    if ( !mapping ) {
      return [];
    }

    if ( mapping.mappingType === 'discrete' ) {
      if ( mapping.visualProperty === 'shape' ) {
        return this.buildDiscreteShapeStyleRules( mapping );
      }
      if ( mapping.visualProperty === 'line-style' ) {
        return this.buildDiscreteEdgeStyleStyleRules( mapping );
      }
      return this.buildDiscreteColorStyleRules( mapping );
    }

    if ( mapping.mappingType === 'continuous' ) {
      if ( mapping.visualProperty === 'width' ) {
        return this.buildContinuousWidthStyleRules( mapping );
      }
      return this.buildContinuousColorStyleRules( mapping );
    }

    return [];
  },

  _applyStyleRules: function ( rules ) {
    if ( _.isEmpty( rules ) ) {
      return false;
    }

    if ( typeof graphPage === 'undefined' || !graphPage.cyGraph ) {
      return false;
    }

    var cy = graphPage.cyGraph;

    if ( !this.styleBeforeMapping ) {
      this.styleBeforeMapping = cytoscapeGraph.getStylesheet( cy );
    }

    var tempStyle = cy.style();

    _.each( rules, function ( rule ) {
      tempStyle = tempStyle.selector( rule.selector ).style( rule.style );
    } );

    _.each( selectedElementsStylesheet, function ( elemStyle ) {
      tempStyle = tempStyle.selector( elemStyle.selector ).style( elemStyle.style );
    } );

    tempStyle.update();

    if ( graphPage.layoutEditor && graphPage.layoutEditor.undoRedoManager ) {
      graphPage.layoutEditor.undoRedoManager.update( {
        'action_type': 'attribute_mapping',
        'data': {
          'style': cytoscapeGraph.getStylesheet( cy ),
          'positions': cytoscapeGraph.getRenderedNodePositionsMap( cy ),
          'selected_elements': cy.elements( ':selected' ),
          'metadata': layoutLearner.computeLayoutMetadata( cy )
        }
      } );
    }

    return true;
  },

  applyMapping: function () {
    var mapping = this.getMappingFromUI();
    if ( !mapping ) {
      $.notify( {
        message: 'Complete the mapping configuration before applying.'
      }, {
        type: 'warning'
      } );
      return false;
    }

    var rules = this.buildStyleRules( mapping );
    if ( !this._applyStyleRules( rules ) ) {
      return false;
    }

    this._rememberAppliedMapping( mapping );

    $.notify( {
      message: 'Attribute mapping applied.'
    }, {
      type: 'success'
    } );

    return true;
  },

  resetMapping: function () {
    if ( !this.styleBeforeMapping ) {
      $.notify( {
        message: 'No mapping to reset.'
      }, {
        type: 'warning'
      } );
      return false;
    }

    if ( typeof graphPage === 'undefined' || !graphPage.cyGraph ) {
      return false;
    }

    var cy = graphPage.cyGraph;

    cytoscapeGraph.applyStylesheet( cy, {
      style: this.styleBeforeMapping
    } );
    this.styleBeforeMapping = null;
    this.clearAppliedMappings();

    if ( graphPage.layoutEditor && graphPage.layoutEditor.undoRedoManager ) {
      graphPage.layoutEditor.undoRedoManager.update( {
        'action_type': 'attribute_mapping_reset',
        'data': {
          'style': cytoscapeGraph.getStylesheet( cy ),
          'positions': cytoscapeGraph.getRenderedNodePositionsMap( cy ),
          'selected_elements': cy.elements( ':selected' ),
          'metadata': layoutLearner.computeLayoutMetadata( cy )
        }
      } );
    }

    $.notify( {
      message: 'Attribute mapping reset.'
    }, {
      type: 'success'
    } );

    return true;
  },

  getDefaultColor: function ( index ) {
    return this.DEFAULT_COLORS[ index % this.DEFAULT_COLORS.length ];
  },

  clearMappingConfig: function () {
    $( '#mappingConfigContent .colorpicker-component' ).each( function () {
      var $picker = $( this );
      if ( $picker.data( 'colorpicker' ) ) {
        $picker.colorpicker( 'destroy' );
      }
    } );
    $( '#mappingConfigContent' ).empty();
    $( '#mappingConfigSection' ).hide();
  },

  renderConfigMessage: function ( message ) {
    $( '#mappingConfigContent' ).html(
      $( '<p>', { 'class': 'text-muted text-center', text: message } )
    );
    $( '#mappingConfigSection' ).show();
  },

  initConfigColorPickers: function () {
    $( '#mappingConfigContent .colorpicker-component' ).each( function () {
      $( this ).colorpicker();
    } );
  },

  renderDiscreteColorConfig: function ( meta ) {
    var self = this;
    var $container = $( '<div>' );

    _.each( meta.values, function ( value, index ) {
      var $row = $( '<div>', { 'class': 'form-group' } );
      $row.append( $( '<label>', {
        'class': 'col-sm-5 control-label',
        text: String( value )
      } ) );

      var $pickerWrap = $( '<div>', { 'class': 'col-sm-7' } );
      var $picker = $( '<div>', {
        'class': 'input-group colorpicker-component mapping-discrete-color'
      } );
      $picker.attr( 'data-category-value', value );
      $picker.append( $( '<input>', {
        type: 'text',
        'class': 'form-control',
        value: self.getDefaultColor( index )
      } ) );
      $picker.append( $( '<span>', { 'class': 'input-group-addon' } ).append( $( '<i>' ) ) );

      $pickerWrap.append( $picker );
      $row.append( $pickerWrap );
      $container.append( $row );
    } );

    $( '#mappingConfigContent' ).html( $container );
    this.initConfigColorPickers();
    $( '#mappingConfigSection' ).show();
  },

  renderDiscreteShapeConfig: function ( meta ) {
    var self = this;
    var $container = $( '<div>' );

    _.each( meta.values, function ( value, index ) {
      var $row = $( '<div>', { 'class': 'form-group' } );
      $row.append( $( '<label>', {
        'class': 'col-sm-5 control-label',
        text: String( value )
      } ) );

      var $select = $( '<select>', {
        'class': 'form-control mapping-discrete-shape'
      } );
      $select.attr( 'data-category-value', value );

      var defaultShape = self.getDefaultShape( index );
      _.each( self.NODE_SHAPES, function ( shape ) {
        $select.append( $( '<option>', {
          value: shape,
          text: shape,
          selected: shape === defaultShape
        } ) );
      } );

      $row.append( $( '<div>', { 'class': 'col-sm-7' } ).append( $select ) );
      $container.append( $row );
    } );

    $( '#mappingConfigContent' ).html( $container );
    $( '#mappingConfigSection' ).show();
  },

  renderDiscreteEdgeStyleConfig: function ( meta ) {
    var self = this;
    var $container = $( '<div>' );

    _.each( meta.values, function ( value, index ) {
      var $row = $( '<div>', { 'class': 'form-group' } );
      $row.append( $( '<label>', {
        'class': 'col-sm-5 control-label',
        text: String( value )
      } ) );

      var $select = $( '<select>', {
        'class': 'form-control mapping-discrete-line-style'
      } );
      $select.attr( 'data-category-value', value );

      var defaultStyle = self.getDefaultLineStyle( index );
      _.each( self.EDGE_LINE_STYLES, function ( lineStyle ) {
        $select.append( $( '<option>', {
          value: lineStyle,
          text: lineStyle,
          selected: lineStyle === defaultStyle
        } ) );
      } );

      $row.append( $( '<div>', { 'class': 'col-sm-7' } ).append( $select ) );
      $container.append( $row );
    } );

    $( '#mappingConfigContent' ).html( $container );
    $( '#mappingConfigSection' ).show();
  },

  renderContinuousColorConfig: function ( meta ) {
    var $container = $( '<div>' );

    $container.append( $( '<p>', {
      'class': 'text-center text-muted',
      text: 'Range: ' + meta.min + ' to ' + meta.max
    } ) );

    var lowRow = $( '<div>', { 'class': 'form-group' } );
    lowRow.append( $( '<label>', {
      'class': 'col-sm-5 control-label',
      text: 'Low (' + meta.min + ')'
    } ) );
    var $lowPicker = this._buildColorPicker( '#ffffcc' );
    $lowPicker.addClass( 'mapping-continuous-low' );
    lowRow.append( $( '<div>', { 'class': 'col-sm-7' } ).append( $lowPicker ) );
    $container.append( lowRow );

    var highRow = $( '<div>', { 'class': 'form-group' } );
    highRow.append( $( '<label>', {
      'class': 'col-sm-5 control-label',
      text: 'High (' + meta.max + ')'
    } ) );
    var $highPicker = this._buildColorPicker( '#cc0000' );
    $highPicker.addClass( 'mapping-continuous-high' );
    highRow.append( $( '<div>', { 'class': 'col-sm-7' } ).append( $highPicker ) );
    $container.append( highRow );

    $( '#mappingConfigContent' ).html( $container );
    this.initConfigColorPickers();
    $( '#mappingConfigSection' ).show();
  },

  renderContinuousWidthConfig: function ( meta ) {
    var elementType = this.getSelectedElementType();
    var isEdge = elementType === 'edge';
    var minLabel = isEdge ? 'Min width' : 'Min size';
    var maxLabel = isEdge ? 'Max width' : 'Max size';
    var defaultMin = isEdge ? this.DEFAULT_MIN_EDGE_WIDTH : this.DEFAULT_MIN_NODE_SIZE;
    var defaultMax = isEdge ? this.DEFAULT_MAX_EDGE_WIDTH : this.DEFAULT_MAX_NODE_SIZE;
    var $container = $( '<div>' );

    $container.append( $( '<p>', {
      'class': 'text-center text-muted',
      text: 'Range: ' + meta.min + ' to ' + meta.max
    } ) );

    var minRow = $( '<div>', { 'class': 'form-group' } );
    minRow.append( $( '<label>', {
      'class': 'col-sm-5 control-label',
      text: minLabel + ' (' + meta.min + ')'
    } ) );
    minRow.append( $( '<div>', { 'class': 'col-sm-7' } ).append(
      $( '<input>', {
        type: 'number',
        min: 1,
        'class': 'form-control mapping-continuous-width-min',
        value: defaultMin
      } )
    ) );
    $container.append( minRow );

    var maxRow = $( '<div>', { 'class': 'form-group' } );
    maxRow.append( $( '<label>', {
      'class': 'col-sm-5 control-label',
      text: maxLabel + ' (' + meta.max + ')'
    } ) );
    maxRow.append( $( '<div>', { 'class': 'col-sm-7' } ).append(
      $( '<input>', {
        type: 'number',
        min: 1,
        'class': 'form-control mapping-continuous-width-max',
        value: defaultMax
      } )
    ) );
    $container.append( maxRow );

    $( '#mappingConfigContent' ).html( $container );
    $( '#mappingConfigSection' ).show();
  },

  _buildColorPicker: function ( defaultColor ) {
    var $picker = $( '<div>', { 'class': 'input-group colorpicker-component' } );
    $picker.append( $( '<input>', {
      type: 'text',
      'class': 'form-control',
      value: defaultColor
    } ) );
    $picker.append( $( '<span>', { 'class': 'input-group-addon' } ).append( $( '<i>' ) ) );
    return $picker;
  },

  updateMappingConfig: function () {
    this.clearMappingConfig();

    if ( !this.isSelectionComplete() ) {
      return;
    }

    var meta = this.getSelectedAttributeMeta();
    var visualProperty = $( '#mappingVisualProperty' ).val();
    var mappingType = this.getSelectedMappingType();

    if ( !meta ) {
      return;
    }

    if ( mappingType === 'discrete' && meta.type === 'categorical' ) {
      if ( this.isColorVisualProperty( visualProperty ) ) {
        this.renderDiscreteColorConfig( meta );
      } else if ( this.isNodeShapeVisualProperty( visualProperty, this.getSelectedElementType() ) ) {
        this.renderDiscreteShapeConfig( meta );
      } else if ( this.isEdgeStyleVisualProperty( visualProperty, this.getSelectedElementType() ) ) {
        this.renderDiscreteEdgeStyleConfig( meta );
      } else {
        this.renderConfigMessage( 'Configuration for this visual property is coming soon.' );
      }
      return;
    }

    if ( mappingType === 'continuous' && meta.type === 'numerical' ) {
      if ( this.isColorVisualProperty( visualProperty ) ) {
        this.renderContinuousColorConfig( meta );
      } else if ( this.isWidthVisualProperty( visualProperty ) ) {
        this.renderContinuousWidthConfig( meta );
      } else {
        this.renderConfigMessage( 'Configuration for this visual property is coming soon.' );
      }
      return;
    }

    this.renderConfigMessage( 'This attribute and mapping type combination is not supported yet.' );
  },

  populateAttributeDropdown: function () {
    var elementType = this.getSelectedElementType();
    var attributeMap = this.getAttributesForElementType( elementType );
    var attributeNames = _.sortBy( _.keys( attributeMap ) );
    var $select = $( '#mappingAttribute' );

    $select.empty();
    $select.append( $( '<option>', {
      value: '',
      text: 'Select attribute...'
    } ) );

    if ( attributeNames.length === 0 ) {
      $select.empty();
      $select.append( $( '<option>', {
        value: '',
        text: 'No mappable attributes found'
      } ) );
      $select.prop( 'disabled', true );
      return;
    }

    $select.prop( 'disabled', false );
    _.each( attributeNames, function ( name ) {
      $select.append( $( '<option>', {
        value: name,
        text: name
      } ) );
    } );
  },

  populateVisualPropertyDropdown: function () {
    var properties = this.getVisualPropertiesForSelection();
    var $select = $( '#mappingVisualProperty' );

    $select.empty();
    $select.append( $( '<option>', {
      value: '',
      text: 'Select visual property...'
    } ) );

    if ( properties.length === 0 ) {
      $select.prop( 'disabled', true );
      return;
    }

    $select.prop( 'disabled', false );
    _.each( properties, function ( property ) {
      $select.append( $( '<option>', {
        value: property.id,
        text: property.label
      } ) );
    } );
  },

  _mappingIdentityKey: function ( mapping ) {
    return [
      mapping.elementType,
      mapping.attribute,
      mapping.visualProperty,
      mapping.mappingType
    ].join( '|' );
  },

  _cloneMapping: function ( mapping ) {
    return JSON.parse( JSON.stringify( mapping ) );
  },

  _rememberAppliedMapping: function ( mapping ) {
    if ( !mapping ) {
      return;
    }

    var key = this._mappingIdentityKey( mapping );
    var clone = this._cloneMapping( mapping );

    this.appliedMappings = _.filter( this.appliedMappings, function ( saved ) {
      return attributeMapping._mappingIdentityKey( saved ) !== key;
    } );
    this.appliedMappings.push( clone );
    this.lastSavedMapping = clone;
  },

  clearAppliedMappings: function () {
    this.appliedMappings = [];
    this.lastSavedMapping = null;
  },

  getMappingsForSave: function () {
    return _.map( this.appliedMappings, function ( mapping ) {
      return attributeMapping._cloneMapping( mapping );
    } );
  },

  setAppliedMappings: function ( mappings ) {
    if ( !_.isArray( mappings ) ) {
      this.clearAppliedMappings();
      return;
    }

    this.appliedMappings = _.map( mappings, function ( mapping ) {
      return attributeMapping._cloneMapping( mapping );
    } );
    this.lastSavedMapping = this.appliedMappings.length ?
      this.appliedMappings[ this.appliedMappings.length - 1 ] :
      null;
  },

  onLayoutLoaded: function ( styleJson ) {
    var mappings = styleJson && styleJson.attribute_mappings;
    this.setAppliedMappings( mappings || [] );
    this.styleBeforeMapping = null;
  },

  _setColorPickerValue: function ( $picker, color ) {
    $picker.find( 'input' ).val( color );
    if ( $picker.data( 'colorpicker' ) ) {
      $picker.colorpicker( 'setValue', color );
    }
  },

  _populateConfigFromMapping: function ( mapping ) {
    if ( !mapping ) {
      return;
    }

    if ( mapping.mappingType === 'discrete' && mapping.valueColors ) {
      _.each( mapping.valueColors, function ( color, categoryValue ) {
        var $picker = $( '#mappingConfigContent .mapping-discrete-color' )
          .filter( '[data-category-value="' + categoryValue + '"]' );
        if ( $picker.length ) {
          attributeMapping._setColorPickerValue( $picker, color );
        }
      } );
      return;
    }

    if ( mapping.mappingType === 'discrete' && mapping.valueShapes ) {
      _.each( mapping.valueShapes, function ( shape, categoryValue ) {
        $( '#mappingConfigContent .mapping-discrete-shape' )
          .filter( '[data-category-value="' + categoryValue + '"]' )
          .val( shape );
      } );
      return;
    }

    if ( mapping.mappingType === 'discrete' && mapping.valueStyles ) {
      _.each( mapping.valueStyles, function ( lineStyle, categoryValue ) {
        $( '#mappingConfigContent .mapping-discrete-line-style' )
          .filter( '[data-category-value="' + categoryValue + '"]' )
          .val( lineStyle );
      } );
      return;
    }

    if ( mapping.mappingType === 'continuous' && mapping.lowColor && mapping.highColor ) {
      this._setColorPickerValue(
        $( '#mappingConfigContent .mapping-continuous-low' ),
        mapping.lowColor
      );
      this._setColorPickerValue(
        $( '#mappingConfigContent .mapping-continuous-high' ),
        mapping.highColor
      );
      return;
    }

    if ( mapping.mappingType === 'continuous' && mapping.minSize && mapping.maxSize ) {
      $( '#mappingConfigContent .mapping-continuous-width-min' ).val( mapping.minSize );
      $( '#mappingConfigContent .mapping-continuous-width-max' ).val( mapping.maxSize );
    }
  },

  restoreMappingToUI: function ( mapping ) {
    if ( !mapping ) {
      return;
    }

    $( '#mappingElementType' ).val( mapping.elementType === 'edge' ? 'edge' : 'node' );
    this.populateAttributeDropdown();
    $( '#mappingAttribute' ).val( mapping.attribute );
    this.syncMappingTypeFromAttribute();
    $( '#mappingVisualProperty' ).val( mapping.visualProperty );
    this.updateMappingConfig();
    this._populateConfigFromMapping( mapping );
  },

  openPanel: function () {
    this.init();
    this.styleBeforeMapping = null;
    this.populateAttributeDropdown();
    this.populateVisualPropertyDropdown();

    if ( this.lastSavedMapping ) {
      this.restoreMappingToUI( this.lastSavedMapping );
    } else {
      this.clearMappingConfig();
    }

    $( '.gs-sidebar-nav' ).removeClass( 'active' );
    $( '#attributeMappingSideBar' ).addClass( 'active' );
  },

  closePanel: function () {
    $( '.gs-sidebar-nav' ).removeClass( 'active' );
    $( '#layoutEditorSideBar' ).addClass( 'active' );
  }
};

if ( typeof graph_json !== 'undefined' && graph_json ) {
  attributeMapping.init();
}
