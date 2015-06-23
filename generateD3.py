import json
import csv
import networkx as nx
import random
from networkx.readwrite import json_graph

from aggregateGroup import aggregate


class exporterD3():

    def __init__(self, readName, dumpName, subset = None):
        
        self.dumpName = dumpName
        self.subset = subset
        self.G = nx.read_pajek(readName)


    def export(self, removeTag=True):

        # define the node attributes:
        # display name, label/group, size/pageRank, fraud/non-fraud, betweenness, modularity 
        for n in self.G:
            self.G.node[n]['name'] = self.G.node[n]['label']
            self.G.node[n]['label'] = self.G.node[n]['label'].split('_')[0]
            self.G.node[n]['size'] = self.G.node[n]['color']
            ind = int(self.G.node[n]['name'].split('_')[1])

            if self.G.node[n]['label'] == 'ClaimID':

                if  ind % 5 != 0:
                    self.G.node[n]['status'] = 'open'
                else:
                    self.G.node[n]['status'] = 'close'
                
                if ind % 3 != 0:
                    self.G.node[n]['type'] = 'BI'
                else:
                    self.G.node[n]['type'] = 'non-BI'
            else:
                self.G.node[n]['status'] = 'Blank'
                self.G.node[n]['type'] = 'Blank'
        
        if self.subset and removeTag == True:
            self.fraudRingModifier() 
            
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
                
                if random.random() < 0.8 and \
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

            for NI in n:
                self.G.node[NI]['modularityClass'] = count
                
        self.subset = list(nodeList)

    
    def KPI(self, KPINode, KPIEdge):

        pr = nx.betweenness_centrality(self.G)
        
        with open(KPINode, 'wb') as csvfile:
            table = csv.writer(csvfile, delimiter=',')
            table.writerow(['name', 'status', 'type', 'betweenness', 'modularityClass', 'pagerank' ])         
            for n in pr:

                self.G.node[n]['betweenness'] = pr[n]
                self.G.node[n]['pagerank'] = float(self.G.node[n]['size']) / 2000.0
                table.writerow( [self.G.node[n]['name'], self.G.node[n]['status'], self.G.node[n]['type'], self.G.node[n]['betweenness'], self.G.node[n]['modularityClass'], self.G.node[n]['pagerank'] ])   


        nx.write_edgelist(self.G, KPIEdge, data=['weight'])



if __name__ == '__main__':
    
    ID = ['06122015']
    fraudRing = None
    aggregate(ID, N_CLAIM=20)

    # layer1
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.findClaimID(cliqueSize = 2)
    d3.export(removeTag=False)
    d3.KPI('./KPI/node_layer1.csv', './KPI/edge_layer1.csv')

    # filter out the subnet in layer3 as fraud ring
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.findClaimID(cliqueSize = 2)
    d3.export()
    d3.KPI('./KPI/node_layer3.csv', './KPI/edge_layer3.csv')
    fraudRing = d3.subset

    # retrieve to layer 2
    fraudRing = d3.subset
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    d3 = exporterD3(readName, dumpName, fraudRing)
    d3.findClaimID(cliqueSize = 2)
    d3.subset = fraudRing
    d3.export()
    d3.KPI('./KPI/node_layer2.csv', './KPI/edge_layer2.csv')
