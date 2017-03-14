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