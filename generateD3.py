import json
import networkx as nx
from networkx.readwrite import json_graph

from aggregateGroup import aggregate


def exportD3(readName, dumpName):
    
    #G = nx.path_graph(4)
    #G = nx.barbell_graph(6,3)
    G = nx.read_pajek(readName)

    for n in G:
        print 'node', n
        G.node[n]['name'] = G.node[n]['label']
        G.node[n]['size'] = G.node[n]['color']

    d = json_graph.node_link_data(G)

    json.dump(d, open(dumpName, 'w'))
    print('wrote node-link json data to {}'.format(dumpName))


if __name__ == '__main__':
    
    ID = ['77']
    
    #aggregate(ID, 60, 0)
    
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    exportD3(readName, dumpName)
    
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    exportD3(readName, dumpName)
    
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    exportD3(readName, dumpName)
