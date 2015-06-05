import json
import networkx as nx
import random
from networkx.readwrite import json_graph

from aggregateGroup import aggregate


class exporterD3():

    def __init__(self, readName, dumpName, subset = None):
        
        self.dumpName = dumpName
        self.subset = subset
        self.G = nx.read_pajek(readName)


    def export(self):
    
        if self.subset:
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
            
        for claim in self.subset:

            neighbors = nx.all_neighbors(self.G, claim)
            
            for n in neighbors:
                
                if self.G.node[n]['label'] == 'Claimant':
                    
                    if random.random() < claimantRatio:
                        removeList.append(n)
                    else:
                        remainList.append(n)
        
        print 'remove', removeList
        print 'remain', remainList
        print 'claimID', self.subset
        for n in remainList:
            for m in self.subset:
                
                if random.random() > 0.5 and \
                        self.G.node[m]['label']=='ClaimID':
                    self.G.add_edge(n, m)

        # Re-index
        for n in removeList:
            self.G.remove_node(n)
        
    # The frausters are in a small portion of the population.
    # In demo, we use k-clique algorithm to find the community 
    # wich (10% +- 2%) of nodes
    def findClaimID(self, cliqueSize, mean=0.1, std=0.05):

        c = nx.k_clique_communities(self.G, cliqueSize)
        N = len(self.G)
        nodeList = None
        
        for count, n in enumerate(list(c)):
            
            print 'Community = ', count, ' Size = ', len(n)
            if nodeList is None:
                nodeList = n
            elif len(n) > (mean - std) * N and len(n) < (mean + std) * N:
                nodeList = n
                
        self.subset = list(nodeList)


if __name__ == '__main__':
    
    ID = ['0603']
    fraudRing = None
    #aggregate(ID, N_CLAIM=100)

    # retrieve to layer 0
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.export()


    # filter out the subnet in layer3 as fraud ring
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.findClaimID(cliqueSize = 2)
    d3.export()

    # retrieve to layer 1
    fraudRing = d3.subset
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.export()
        
