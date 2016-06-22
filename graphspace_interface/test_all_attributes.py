
import graphspace_interface as interface
import networkx as nx
import sys
import random
import os


def main(argv):
    """
    Makes graphs with all possible attributes.
    Nodes are labeled by the test number.
    """

    if len(argv) != 3 and len(argv) != 4:
        print 'USAGE: interface_examples.py <USERNAME> <PASSWORD> <OPTIONAL-GROUPNAME>\n'
        sys.exit()

    user = argv[1]
    password = argv[2]

    if len(argv)==3:
        group = None
    else:   
        group=argv[3]
    print 'USER=%s' % (user)
    print 'PASSWORD=%s' % (password)
    print 'GROUP=%s' % (group)

    ## build list of NetworkX graphs.
    graphs = {}
    graphs['NodeShapes'] = testNodeShapes()
    graphs['LabelPlacement'] = testLabelPlacement()
    graphs['BorderStyles'] = testBorderStyles()
    graphs['EdgeStyles'] = testEdgeStyles()
    graphs['FilteringByK'] = testKFiltering()
    graphs['Popups'] = testPopups()

    edgefile = 'test.json'
    for graphid in graphs:
        G = graphs[graphid]

        #print G,graphid,outfile,user,password,metadata
        interface.postGraph(G,graphid,outfile=edgefile,user=user,password=password,logfile='tmp.log',metadata={'tags':['AttributeGallery']})
        if group != None:
            interface.shareGraph(graphid,user=user,password=password,group=group)
    interface.makeGraphsWithTagPublic(user,password,'AttributeGallery')

    ## delete edgefile.
    #os.system('rm -f %s' % (edgefile))

    print 'DONE. Check log file tmp.log for errors.\n'
    return

def randhex():
    return '#%02x%02x%02x' % (random.randint(0,255),random.randint(0,255),random.randint(0,255))

def testNodeShapes():
    G = nx.DiGraph(directed=True)
    n = len(interface.ALLOWED_NODE_SHAPES)
    nodeids = ['%d' % (i) for i in range(n)]
    for i in range(n):
        interface.add_node(G,nodeids[i],label=nodeids[i],shape=interface.ALLOWED_NODE_SHAPES[i],color=randhex(),width=60,height=60)    
    for i in range(20): # randomly add 20 edges
        interface.add_edge(G,random.choice(nodeids),random.choice(nodeids))

    interface.validate_json(G)
    return G

def testLabelPlacement():
    G = nx.DiGraph(directed=True)
    nodeids = []
    for valign in interface.ALLOWED_TEXT_VALIGN:
        for halign in interface.ALLOWED_TEXT_HALIGN:
            nodeid = 'vertical %s\nhorizontal %s' % (valign,halign)
            interface.add_node(G,nodeid,label=nodeid,shape='roundrectangle',color=randhex(),valign=valign,halign=halign,width=120,height=40)  
            nodeids.append(nodeid)
          
    for i in range(20): # randomly add 20 edges
        interface.add_edge(G,random.choice(nodeids),random.choice(nodeids))

    interface.validate_json(G)
    return G

def testBorderStyles():
    G = nx.DiGraph(directed=True)
    nodeids = []
    for style in interface.ALLOWED_NODE_BORDER_STYLES:
        nodeid = 'thick\n%s' % (style)
        interface.add_node(G,nodeid,label=nodeid,shape='ellipse',color=randhex(),width=60,height=60,style=style,border_width=15,border_color=randhex())
        nodeids.append(nodeid)
        nodeid = 'skinny\n%s' % (style)
        interface.add_node(G,nodeid,label=nodeid,shape='ellipse',color=randhex(),width=60,height=60,style=style,border_width=5,border_color=randhex())
        nodeids.append(nodeid)
    nodeid = 'bubble\neffect'
    interface.add_node(G,nodeid,label=nodeid,shape='ellipse',color=randhex(),width=60,height=60,bubble=randhex())
    nodeids.append(nodeid)

    for i in range(20): # randomly add 20 edges
        interface.add_edge(G,random.choice(nodeids),random.choice(nodeids))

    interface.validate_json(G)
    return G

def testEdgeStyles():
    G = nx.DiGraph(directed=True)
    n = 20
    nodeids = ['%d' % (i) for i in range(n)]
    for i in range(n):
        interface.add_node(G,nodeids[i],label=nodeids[i],shape='hexagon',width=25,height=25)    
    width = 2
    for shape in interface.ALLOWED_ARROW_SHAPES:
        for style in interface.ALLOWED_EDGE_STYLES:
            for fill in interface.ALLOWED_ARROW_FILL:
                tail = random.choice(nodeids)
                head = random.choice(nodeids)
                interface.add_edge(G,tail,head,color=randhex(),directed=True,width=width,arrow_shape=shape,edge_style=style,arrow_fill=fill)
    interface.validate_json(G)
    return G

def testKFiltering():
    G = nx.DiGraph(directed=True)
    n = 10
    nodeids = ['%d' % (i) for i in range(n)]
    for i in range(n):
        interface.add_node(G,nodeids[i],label=nodeids[i],shape='star',color=randhex(),width=30,height=30,k=i+1)    
    for i in range(1,n,1):
        interface.add_edge(G,nodeids[i-1],nodeids[i],directed=True,arrow_shape='circle',k=i+1)

    interface.validate_json(G)
    return G

def testPopups():
    G = nx.DiGraph(directed=True)
    label = 'Click Me'
    popup = '</h3>Any HTML can go here</h3> Need a break? Try this website: <br> <a color="blue" target="_blank" href="http://xkcd.com/">http://xkcd.com/</a>'
    interface.add_node(G,label,label=label,shape='ellipse',color=randhex(),height=60,width=60,bubble=randhex(),popup=popup)
    label = 'Click the Solid Edge'

    interface.add_node(G,'ID1',label=label,popup='This is a white node.')
    interface.add_node(G,'ID2',label=label,popup='This is a white node.')
    popup = '</h3>Note that the Node IDs are shown at the top.</h3> Need <it>another</it> break? Try this website: <br> <a color="blue" target="_blank" href="http://phdcomics.com">ttp://phdcomics.com</a>'
    
    interface.add_edge(G,'ID1','ID2',width=4,color=randhex(),directed=True,arrow_shape='tee',popup=popup)
    interface.add_edge(G,'Click Me','ID1',edge_style='dashed',popup='This is a dashed edge.')
    interface.add_edge(G,'Click Me','ID2',edge_style='dashed',popup='This is a dashed edge.')
    interface.validate_json(G)
    return G

if __name__ == '__main__':
    main(sys.argv)