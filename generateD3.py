import json
import networkx as nx
import random
from networkx.readwrite import json_graph

from aggregateGroup import aggregate


class exporterD3():

    def __init__(self, readName, dumpName, claimList = None):
        
        self.dumpName = dumpName
        self.claimList = claimList
        self.G = nx.read_pajek(readName)


    def export(self):
    
        if self.claimList:
            self.fraudRingModifier() 

        for n in self.G:
            self.G.node[n]['name'] = self.G.node[n]['label']
            self.G.node[n]['size'] = self.G.node[n]['color']

        d = json_graph.node_link_data(self.G)

        json.dump(d, open(self.dumpName, 'w'))
        print('wrote node-link json data to {}'.format(self.dumpName))

    # convert claims subsets to fraud ring
    def fraudRingModifier(self, claimantRatio=0.5):
    
        removeList = []
        remainList = []

        for claim in self.claimList:

            neighbors = nx.all_neighbors(self.G, claim)
            
            for n in neighbors:
                
                if self.G.node[n]['label'] == 'Claimant':
                    
                    if random.random() < claimantRatio:
                        removeList.append(n)
                    else:
                        remainList.append(n)
        
        print 'remove', removeList
        print 'remain', remainList
        for n in remainList:
            for m in self.claimList:
                
                if random.random() > 0.3 and \
                        self.G.node[m]['label']=='ClaimID':
                    self.G.add_edge(n, m)

        # Re-index
        for n in removeList:
            self.G.remove_node(n)
        
    # the frausters are small portion in the population
    # using 10% +- 5% for demo purpose 
    def findClaimID(self, cliqueSize, mean=0.1, std=0.02):

        c = nx.k_clique_communities(self.G, cliqueSize)
        N = len(self.G)
        nodeList = None
        for count, n in enumerate(list(c)):
            
            print 'Community = ', count, ' size = ', len(n) 
            if nodeList is None:
                nodeList = n
            elif len(n) > (mean - std) * N and len(n) < (mean + std) * N:
                nodeList = n
                
        self.claimList = list(nodeList)


if __name__ == '__main__':
    
    ID = ['0603']
    claimList = None
    #aggregate(ID, 100, 0)

    # target the subnet in layer3 as fraud ring
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    d3 = exporterD3(readName, dumpName, claimList)
    d3.findClaimID(2)
    d3.export()
    
    # retrieve to layer 2
    claimList = d3.claimList
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    d3 = exporterD3(readName, dumpName, claimList)
    d3.export()
    
    # retrieve to layer 1
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    d3 = exporterD3(readName, dumpName, claimList)
    d3.export()
