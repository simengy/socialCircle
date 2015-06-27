import json
import csv
import networkx as nx
import random
from datetime import datetime, timedelta
from networkx.readwrite import json_graph

from aggregateGroup import aggregate


class exporterD3():

    def __init__(self, readName, dumpName, removeList = None, remainList = None, subset = None):
        
        self.dumpName = dumpName
        self.subset = subset
        self.removeList = removeList
        self.remainList = remainList
        self.G = nx.read_pajek(readName)


    def export(self):

        GEO = ['CA', 'AZ', 'FL', 'NY', 'NC', 'OH', 'TX', 'WA', 'CO']
        TIME = [(datetime.today() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0,100)]
        groups = {}
        count = 1
        # define the node attributes:
        # display name, label/group, size/pageRank, fraud/non-fraud, betweenness, modularity
        
        for n in self.G:
            self.G.node[n]['name'] = self.G.node[n]['label']
            self.G.node[n]['label'] = self.G.node[n]['label'].split('_')[0]
            self.G.node[n]['size'] = self.G.node[n]['color']
            
            ind = int(self.G.node[n]['name'].split('_')[1])
            key = self.G.node[n]['label']

            if key not in groups:
                groups[key] = count
                count += 1
            
            self.G.node[n]['group'] = groups[key]
            
            if self.G.node[n]['label'] == 'ClaimID':

                if  ind % 5 != 0:
                    self.G.node[n]['status'] = 'open'
                else:
                    self.G.node[n]['status'] = 'close'
                
                if ind % 3 != 0:
                    self.G.node[n]['type'] = 'BI'
                else:
                    self.G.node[n]['type'] = 'non-BI'
                
                self.G.node[n]['geo'] = GEO[ind % 8]
                
                self.G.node[n]['timestamp'] = TIME[ind % 10]
            else:
                self.G.node[n]['status'] = 'Blank'
                self.G.node[n]['type'] = 'Blank'
                self.G.node[n]['timestamp'] = 'Blank'
                self.G.node[n]['geo'] = 'Blank'
        
        d = json_graph.node_link_data(self.G)

        json.dump(d, open(self.dumpName, 'w'))
        print('wrote node-link json data to {}'.format(self.dumpName))

    # convert claims subsets to fraud ring
    def fraudRingModifier(self, density, claimantRatio=0.4):
        
        if self.removeList is None and self.remainList is None:
        
            self.removeList = []
            self.remainList = []

            for claim in self.subset:

                neighbors = nx.all_neighbors(self.G, claim)
            
                for n in neighbors:
                
                    if self.G.node[n]['label'].split('_')[0] != 'ClaimID' and \
                            n not in self.removeList:
                        if random.random() < claimantRatio:
                            self.removeList.append(n)
                    
                    if n not in self.remainList:
                        self.remainList.append(n)
        
        print 'remove', self.removeList
        print 'remain', self.remainList
        print 'claimID', self.subset

        for n in self.remainList:
            for m in self.subset:
                
                if random.random() < density and \
                        self.G.node[m]['label'].split('_')[0]=='ClaimID':
                    self.G.add_edge(n, m)

        # Remove and re-index
        for n in self.removeList:
            self.G.remove_node(n)
        
    # The frausters are in a small portion of the population.
    # In demo, we use k-clique algorithm to find the community 
    # wich (10% +- 2%) of nodes
    def findClaimID(self, cliqueSize, density, mean=0.1, std=0.05):
        
        c = nx.k_clique_communities(self.G, cliqueSize)
        N = len(self.G)
        nodeList = None
        
        for count, n in enumerate(list(c)):
            
            print 'Community = ', count, ' Size = ', len(n)
            if nodeList is None:
                nodeList = n
            elif len(n) > (mean - std) * N and len(n) < (mean + std) * N:
                nodeList = n
            
        if self.subset is None:     
            self.subset = list(nodeList)
        
        if self.subset:
            self.fraudRingModifier(density=density) 

        c = nx.k_clique_communities(self.G, cliqueSize)
        maximum = 0.0

        for count, n in enumerate(list(c)): 
            
            N_claim = 0.
            N_part = 0.
            
            for NI in n:
                if self.G.node[NI]['label'].split('_')[0] == 'ClaimID':
                    N_claim += 1.0
                else:
                    N_part += 1.0
            
            for NI in n:
                ratio = N_claim / N_part
                self.G.node[NI]['modularityClass'] = count
                self.G.node[NI]['fraudScore'] = ratio

                if maximum < ratio:
                    maximum = ratio
        
       
        c = nx.k_clique_communities(self.G, cliqueSize)
 
        for count, n in enumerate(list(c)): 
            
            for NI in n:
                self.G.node[NI]['fraudScore'] /= maximum
                self.G.node[NI]['fraudScore'] *= 100
                self.G.node[NI]['fraudScore'] = int(self.G.node[NI]['fraudScore'])

    
    def KPI(self, KPINode, KPIEdge):

        pr = nx.betweenness_centrality(self.G)
        
        with open(KPINode, 'wb') as csvfile:
            
            table = csv.writer(csvfile, delimiter=',')
            table.writerow(['name', 'group', 'modularity', 'pageRank','geo', 'time', 'fraudScore' ])         
            
            for n in pr:
                
                self.G.node[n]['betweenness'] = pr[n]
                self.G.node[n]['pagerank'] = float(self.G.node[n]['size']) / 2000.0
                try:
                    table.writerow( [self.G.node[n]['name'], 
                    self.G.node[n]['group'],
                    self.G.node[n]['modularity'], 
                    self.G.node[n]['pagerank'], 
                    self.G.node[n]['geo'], 
                    self.G.node[n]['timestamp'], 
                    self.G.node[n]['fraudScore'] ])
                except:
                    print 'Node = ', n
                    KeyError() 

        with open(KPIEdge, 'wb') as csvfile:
           
            table = csv.writer(csvfile, delimiter=',')
            table.writerow(['source', 'target', 'value'])         
            
            for s, t in self.G.edges_iter():
                
                table.writerow( [self.G.node[s]['name'], 
                    self.G.node[t]['name'], 
                    5.0 ] )



if __name__ == '__main__':
    
    ID = ['06122015']
    fraudRing = None
    removeNodes = None
    remainNodes = None
    aggregate(ID, N_CLAIM=60)


    # filter out the subnet in layer3 as fraud ring
    readName = '../social/aggregate_plot_round=2_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force2/force.json'
    d3 = exporterD3(readName, dumpName, removeNodes, remainNodes, fraudRing)
    d3.findClaimID(cliqueSize = 2, density = 0.5)
    d3.export()
    d3.KPI('./KPI/node_layer3.csv', './KPI/edge_layer3.csv')
    fraudRing = d3.subset
    removeNodes = d3.removeList
    remainNodes = d3.remainList
    
    # layer1
    readName = '../social/aggregate_plot_round=0_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force0/force.json'
    d3 = exporterD3(readName, dumpName, removeNodes, remainNodes, fraudRing)
    d3.findClaimID(cliqueSize = 2, density = 0.0)
    d3.export()
    d3.KPI('./KPI/node_layer1.csv', './KPI/edge_layer1.csv')


    # retrieve to layer 2
    fraudRing = d3.subset
    readName = '../social/aggregate_plot_round=1_{}.net'.format('.'.join(ID))
    dumpName = '/var/www/homepage/public/d3/force1/force.json'
    d3 = exporterD3(readName, dumpName, removeNodes, remainNodes, fraudRing)
    d3.findClaimID(cliqueSize = 2, density = 0.3)
    d3.export()
    d3.KPI('./KPI/node_layer2.csv', './KPI/edge_layer2.csv')
