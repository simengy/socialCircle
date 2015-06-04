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


    def exportD3(self):
    
        if claimList:
            self.fraudRingModifier() 
        
        #self.findClaimID()

        for n in self.G:
            self.G.node[n]['name'] = self.G.node[n]['label']
            self.G.node[n]['size'] = self.G.node[n]['color']

        d = json_graph.node_link_data(self.G)

        json.dump(d, open(self.dumpName, 'w'))
        print('wrote node-link json data to {}'.format(self.dumpName))


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
                    
        print 'length', len(remainList), len(removeList)
        for n in removeList:
            self.G.remove_node(n)
        
        for n in remainList:
            for m in self.claimList:
                if random.random() > 0.3:
                    self.G.add_edge(n, m)


    def findClaimID(self):

        for n in self.G:
            if self.G.node[n]['label'] == 'ClaimID':
                print 'ClaimID = ', n


if __name__ == '__main__':
    
    ID = ['0603']
    claimList = ['86', '45', '40']
    #aggregate(ID, 60, 0)
    
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    d3 = exporterD3(readName, dumpName, claimList)
    d3.exportD3()
    
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    
    d3 = exporterD3(readName, dumpName, claimList)
    d3.exportD3()
    
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    d3 = exporterD3(readName, dumpName, claimList)
    d3.exportD3()
