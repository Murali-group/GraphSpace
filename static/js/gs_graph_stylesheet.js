var defaultStylesheet = [
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'line-style': 'solid'
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
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
        'overlay-color': 'red',
        'overlay-padding': 10,
        'overlay-opacity': 0.3
    }
},
    {
        'selector': 'edge:selected',
        'style': {
            'overlay-color': 'red',
            'overlay-padding': 10,
            'overlay-opacity': 0.3
        }
    }
]