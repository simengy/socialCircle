import snap
import pandas as pd

from girvanNuewman import read_nodeadjlist


minCircleSize = 5
write_DIR = '../Metrics/'

def betweenNess(graph, userId):

    Nodes = snap.TIntFltH()
    Edges = snap.TIntPrFltH()

    snap.GetBetweennessCentr(graph, Nodes, Edges, 1.0)
    df = pd.DataFrame(columns=('Node', 'Centrality'))
    
    for node in Nodes:
        if Nodes[node] != 0:
            #print 'node: %d centrality: %f' % (node, Nodes[node])
            df.loc[node] =[node,  Nodes[node]]

    for edge in Edges:  
        break
        #print 'edge: (%d, %d) centrality: %f' % (edge.GetVal1(), edge.GetVal2(), Edges[edge])

    df.to_csv(write_DIR + 'betweenness_{}.csv'.format(userId), sep=',', index=False)


def pageRank(graph, userId):

    Nodes = snap.TIntFltH()

    snap.GetPageRank(graph, Nodes)
    df = pd.DataFrame(columns=('Node', 'PageRank'))
    
    for node in Nodes:
        #print 'node: %d pageRank: %f' % (node, Nodes[node])
        df.loc[node] =[node,  Nodes[node]]
    
    df.to_csv(write_DIR + 'pagerank_{}.csv'.format(userId), sep=',', index=False)


def modularity(graph, index, userId):

    cmtyV = snap.TCnComV()

    modularity = snap.CommunityGirvanNewman(graph, cmtyV)
    df = pd.DataFrame(columns=('Node', 'Community', 'Modularity'))
    for cmty in cmtyV:

        if cmty.Len() > minCircleSize:
            print list(cmty) 
            index += 1

            for NI in cmty:
                df.loc[NI] =[NI, index,  modularity]
                #print 'node: %d, community: %d, modularity: %f' % (NI, index, modularity)

    df.to_csv(write_DIR + 'modularity_{}.csv'.format(userId), sep=',', index=False)
    
    return index

    
if __name__ == '__main__':

    claims = pd.read_csv('../IDs/train_ID.csv')['userId']

    index = 0
    for userId in claims:
        
        print '\n###################################'
        
        print 'userID = ', userId
        filename = str(userId) + '.egonet'
        G = snap.TUNGraph.New()
        G = read_nodeadjlist('../data/egonets/'+filename, G)
        
        betweenNess(G, userId)

        pageRank(G, userId)
    
        index = modularity(G, index, userId)
        

        print '###################################\n'

