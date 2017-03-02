//var stylesheet = cytoscape.stylesheet()
//    //.selector('node[width]').css({
//    //    'width': 'data(width)'
//    //})
//    //.selector('node[height]').css({
//    //    'height': 'data(height)'
//    //})
//    //.selector('node[shape]').css({
//    //    'shape': 'data(shape)'
//    //})
//    //.selector('node[background_color]').css({
//    //    'background-color': 'data(background_color)'
//    //})
//    //.selector('node[background_blacken]').css({
//    //    'background-blacken': 'data(background_blacken)'
//    //})
//    //.selector('node[background_opacity]').css({
//    //    'background-opacity': 'data(background_opacity)'
//    //})
//    //.selector('node[border_width]').css({
//    //    'border-width': 'data(border_width)'
//    //})
//    //.selector('node[border_style]').css({
//    //    'border-style': 'data(border_style)'
//    //})
//    //.selector('node[border_color]').css({
//    //    'border-color': 'data(border_color)'
//    //})
//    //.selector('node[border_opacity]').css({
//    //    'border-opacity': 'data(border_opacity)'
//    //})
//
//    //BACKGROUND IMAGE PROPERTIES
//    //.selector('node[background_image]').css({
//    //    'background-image': 'data(background_image)'
//    //})
//    //.selector('node[background_image_opacity]').css({
//    //    'background-image-opacity': 'data(background_image_opacity)'
//    //})
//    //.selector('node[background_width]').css({
//    //    'background-width': 'data(background_width)'
//    //})
//    //.selector('node[background_height]').css({
//    //    'background-height': 'data(background_height)'
//    //})
//    //.selector('node[background_fit]').css({
//    //    'background-fit': 'data(background_fit)'
//    //})
//    //.selector('node[background_repeat]').css({
//    //    'background-repeat': 'data(background_repeat)'
//    //})
//    //.selector('node[background_position_x]').css({
//    //    'background-position-x': 'data(background_position_x)'
//    //})
//    //.selector('node[background_position_y]').css({
//    //    'background-position-y': 'data(background_position_y)'
//    //})
//    //.selector('node[background_clip]').css({
//    //    'background-clip': 'data(background_clip)'
//    //})
//
//    //LABEL PROPERTIES
//    //.selector('node[color]').css({
//    //    'color': 'data(color)'
//    //})
//    //.selector('node').css({
//    //    'content': 'style(content)'
//    //})
//    //.selector('node[font_family]').css({
//    //    'font-family': 'data(font_family)'
//    //})
//    //.selector('node[font_size]').css({
//    //    'font-size': 'data(font_size)'
//    //})
//    //.selector('node[font_style]').css({
//    //    'font-style': 'data(font_style)'
//    //})
//    //.selector('node[font_weight]').css({
//    //    'font-weight': 'data(font_weight)'
//    //})
//    //.selector('node[text_transform]').css({
//    //    'text-transform': 'data(text_transform)'
//    //})
//    //.selector('node[text_wrap]').css({
//    //    'text-wrap': 'data(text_wrap)'
//    //})
//    //.selector('node[text_max_width]').css({
//    //    'text-max-width': 'data(text_max_width)'
//    //})
//    //.selector('node[edge_text_rotation]').css({
//    //    'edge-text-rotation': 'data(edge_text_rotation)'
//    //})
//    //.selector('node[text_opacity]').css({
//    //    'text-opacity': 'data(text_opacity)'
//    //})
//    //.selector('node[text_outline_color]').css({
//    //    'text-outline-color': 'data(text_outline_color)'
//    //})
//    //.selector('node[text_outline_opacity]').css({
//    //    'text-outline-opacity': 'data(text_outline_opacity)'
//    //})
//    //.selector('node[text_outline_width]').css({
//    //    'text-outline-width': 'data(text_outline_width)'
//    //})
//    //.selector('node[text_shadow_blur]').css({
//    //    'text-shadow-blur': 'data(text_shadow_blur)'
//    //})
//    //.selector('node[text_shadow_color]').css({
//    //    'text-shadow-color': 'data(text_shadow_color)'
//    //})
//    //.selector('node[text_shadow_offset_x]').css({
//    //    'text-shadow-offset-x': 'data(text_shadow_offset_x)'
//    //})
//    //.selector('node[text_shadow_offset_y]').css({
//    //    'text-shadow-offset-y': 'data(text_shadow_offset_y)'
//    //})
//    //.selector('node[text_shadow_opacity]').css({
//    //    'text-shadow-opacity': 'data(text_shadow_opacity)'
//    //})
//    //.selector('node[text_background_shape]').css({
//    //    'text-background-shape': 'data(text_background_shape)'
//    //})
//    //.selector('node[text_border_width]').css({
//    //    'text-border-width': 'data(text_border_width)'
//    //})
//    //.selector('node[text_border_style]').css({
//    //    'text-border-style': 'data(text_border_style)'
//    //})
//    //.selector('node[text_border_color]').css({
//    //    'text-border-color': 'data(text_border_color)'
//    //})
//    //.selector('node[min_zoomed_font_size]').css({
//    //    'min-zoomed-font-size': 'data(min_zoomed_font_size)'
//    //})
//    //.selector('node[text_halign]').css({
//    //    'text-halign': 'data(text_halign)'
//    //})
//    //.selector('node[text_valign]').css({
//    //    'text-valign': 'data(text_valign)'
//    //})
//
//    //EDGE LINE PROPERTIES
//
//
//    /*
//     The default stylesheet was updated in 2.7 to have greater performance by default. This means that haystack edges are used by default, and haystacks support only mid arrows.
//     If you set your edges in your stylesheet to beziers, then you can use source and target arrows.
//
//     Refer to : http://stackoverflow.com/questions/37822572/edge-target-arrows-not-working-in-cytoscape-js-2-7-0
//     */
//
//    .selector('edge').css({
//        'curve-style': 'bezier'
//    })
//    //.selector('edge[width]').css({
//    //    'width': 'data(width)'
//    //})
//    //.selector('edge[curve_style]').css({
//    //    'curve-style': 'data(curve_style)'
//    //})
//    //.selector('edge[haystack_radius]').css({
//    //    'haystack-radius': 'data(haystack_radius)'
//    //})
//    //.selector('edge[control_point_step_size]').css({
//    //    'control-point-step-size': 'data(control_point_step_size)'
//    //})
//    //.selector('edge[control_point_distance]').css({
//    //    'control-point-distance': 'data(control_point_distance)'
//    //})
//    //.selector('edge[control_point_weight]').css({
//    //    'control-point-weight': 'data(control_point_weight)'
//    //})
//    //.selector('edge[line_color]').css({
//    //    'line-color': 'data(line_color)'
//    //})
//    //.selector('edge[line_style]').css({
//    //    'line-style': 'data(line_style)'
//    //})
//    //
//    ////EDGE ARROW PROPERTIES
//    //.selector('edge[source_arrow_color]').css({
//    //    'source-arrow-color': 'data(source_arrow_color)'
//    //})
//    //.selector('edge[source_arrow_shape]').css({
//    //    'source-arrow-shape': 'data(source_arrow_shape)'
//    //})
//    //.selector('edge[source_arrow_fill]').css({
//    //    'source-arrow-fill': 'data(source_arrow_fill)'
//    //})
//    //.selector('edge[mid_source_arrow_color]').css({
//    //    'mid-source-arrow-color': 'data(mid_source_arrow_color)'
//    //})
//    //.selector('edge[mid_source_arrow_shape]').css({
//    //    'mid-source-arrow-shape': 'data(mid_source_arrow_shape)'
//    //})
//    //.selector('edge[mid_source_arrow_fill]').css({
//    //    'mid-source-arrow-fill': 'data(mid_source_arrow_fill)'
//    //})
//    //.selector('edge[target_arrow_color]').css({
//    //    'target-arrow-color': 'data(target_arrow_color)'
//    //})
//    //.selector('edge[target_arrow_shape]').css({
//    //    'target-arrow-shape': 'data(target_arrow_shape)'
//    //})
//    //.selector('edge[target_arrow_fill]').css({
//    //    'target-arrow-fill': 'data(target_arrow_fill)'
//    //})
//    //.selector('edge[mid_target_arrow_color]').css({
//    //    'mid-target-arrow-color': 'data(mid_target_arrow_color)'
//    //})
//    //.selector('edge[mid_target_arrow_shape]').css({
//    //    'mid-target-arrow-shape': 'data(mid_target_arrow_shape)'
//    //})
//    //.selector('edge[mid_target_arrow_fill]').css({
//    //    'mid-target-arrow-fill': 'data(mid_target_arrow_fill)'
//    //})
//    .selector('node:selected')
//    .css({
//        'border-width': 3,
//        'border-color': '#ff0000'
//    })
//    .selector('edge:selected')
//    .css({
//        'width': 3,
//        'line-color': '#ff0000',
//        'target-arrow-color': '#ff0000',
//        'source-arrow-color': '#ff0000'
//    });

var defaultStylesheet = [
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier'
        }
    },
    {
        'selector': 'node',
        'style': {
            'shape': 'ellipse',
            'background-color': 'yellow',
            'border-color': '#888',
            'text-halign': 'center',
            'text-valign': 'center'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': 'black'
        }
    }
];

var selectedElementsStylesheet = [{
    'selector': 'node:selected',
    'style': {
        'border-width': 3,
        'border-color': '#ff0000'
    }
},
    {
        'selector': 'edge:selected',
        'style': {
            'width': 3,
            'line-color': '#ff0000',
            'target-arrow-color': '#ff0000',
            'source-arrow-color': '#ff0000'
        }
    }
]