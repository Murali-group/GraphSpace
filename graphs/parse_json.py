def parse(json):
    '''
        WILL BE REMOVED

        A function to parse networks represented in JSON to have it compatible with
        Cytoscape Web.
    '''
    keywords = [u'graph', u'data', u'k', u'nodes', u'edges', u'id', u'source', 
                u'target', u'directed', u'label', u'popup', u'tooltip', 
                u'color', u'size', u'shape', u'graph_id', u'go_function_id', 
                u'borderWidth', u'labelFontWeight', u'width', u'style', 
                u'metadata']

    json = json.split(' ')
    new_json = ''

    for w in json:
        for keyword in keywords:
            if keyword in w:
                w = w.replace('"', '')
                break

        new_json = new_json + w + ' '

    return new_json


