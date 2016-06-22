## These examples were originally modified from the graphspace_interface.py main() function.
## AR: The examples in this main() function will bepart of the Programmer's Guide instead of here.  I have left it in for now for testing.

import graphspace_interface as interface
import networkx as nx
import random
import sys


def main(argv):
    """
    Usage (from within the current directory)

    This script posts two graphs.  The first graph reads 
    in an edge file and modifies the attributes for each node and
    each edge.  The second graph creates 10 random nodes and 20 
    random undirected edges, using the default attributes from 
    add_node() and add_edge() functions.

    todo:: Currently, the example file is committed with this source code. Graphs are
    posted to GraphSpace with Anna's username and password and shared with 
    her group 'testgroup'.  This should be cleaned up.

    todo:: need to make an OptionParser for this main function if we are 
    going to keep it.  

    todo:: raise exceptions for unexpected colors/widths/shapes/etc.
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

    edgefile = 'gs-interface-example-edges.txt'
    graphid = 'gs-interface-example1'
    outfile = 'gs-interface-example1.json'
    runExample1(edgefile,user,password,group,graphid,outfile)

    graphid = 'gs-interface-example2'
    outfile = 'gs-interface-example2.json'
    runExample2(user,password,group,graphid,outfile)

    print 'DONE. Check log file for errors.\n'
    return

def runExample1(edgefile,user,password,group,graphid,outfile):
    #Graph 1 (tmp): read edges in from a file.
    #Take the first two columns of the file as the edges.
    edges = []
    with open(edgefile) as fin:
        for line in fin:
            if line[0] == '#': # skip comments
                continue
            row = line.strip().split()
            edges.append((row[0],row[1]))

    #Make a directed graph NetworkX object.
    #A directed graph will work even if we 
    #want to show an undirected graph, since
    #each edge has a "directed" attribute that
    #determines whether the edge is drawn with an
    #arrow or not.
    G = nx.DiGraph(edges,directed=True)

    for n in G.nodes():
        label= 'node\n%s' % (n)
        interface.add_node_label(G,n,label)
        interface.add_node_wrap(G,n,'wrap')
        interface.add_node_color(G,n,'#ACFA58')
        interface.add_node_shape(G,n,'rectangle')
        interface.add_node_height(G,n,None,label)
        interface.add_node_width(G,n,None,label)

    for t,h in G.edges():
        interface.add_edge_directionality(G,t,h,True)
        interface.add_edge_color(G,t,h,'#000000')
        interface.add_edge_width(G,t,h,2)

    metadata = {'description':'example1','title':'Example 1 Graph','tags':[]}
    print G,graphid,outfile,user,password,metadata
    interface.postGraph(G,graphid,outfile=outfile,user=user,password=password,metadata=metadata)
    if group != None:
        interface.shareGraph(graphid,user=user,password=password,group=group)
    return

def runExample2(user,password,group,graphid,outfile):
    #############
    ## Graph 2 (tmp2): randomly generate nodes and edges.

    G = nx.DiGraph(directed=True)
    # add 10 nodes
    nodeids = ['node\n%d' % (i) for i in range(10)]
    for n in nodeids:
        interface.add_node(G,n,label=n,bubble='yellow',color='yellow')
    for i in range(20): # randomly add 20 edges
        interface.add_edge(G,random.choice(nodeids),random.choice(nodeids),width=random.choice([1,2,3,4,5]),directed=True)

    interface.validate_json(G)
    interface.postGraph(G,graphid,outfile=outfile,user=user,password=password,logfile='tmp.log')
    if group != None:
        interface.shareGraph(graphid,user=user,password=password,group=group)
    return

if __name__ == '__main__':
    main(sys.argv)