import snap
import random

from girvanNuewman import read_nodeadjlist
from visualization import plotting
from add_edges import addEdges

egonetFolderName = '../data/egonets/'


def aggregate(userList, N_CLAIM=5, inDEG=0):

    G = snap.TUNGraph.New()

    #for userId in userList:

    #    filename = str(userId) + '.egonet'
    #    read_nodeadjlist(egonetFolderName + filename, G, MAX_DEGREE = 5)
    
    # removing the NODES with low degrees
    
    claimantList = []
    for i in xrange(N_CLAIM):
        
        temp = snap.GenStar(snap.PUNGraph, random.randrange(3, 8), False)
        countID = G.GetNodes()
        
        for NI in temp.Nodes():
            G.AddNode(countID + NI.GetId())
            if random.random() < 0.35:
                claimantList.append(countID + NI.GetId())


        for E in temp.Edges():
            G.AddEdge(E.GetSrcNId()+countID, E.GetDstNId()+countID)


    snap.DelDegKNodes(G, inDEG, inDEG)
    print '\nAfter remove Nodes with In-Degree = %d and out-Degree = %d ' % (inDEG, inDEG)
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())

    # 2nd layer
    plot = plotting(G, snap.gvlNeato, True)
    plot.hirachical()
    

    # Add links
    ratio = [1.0, 0.6, 0.2]
    for r in xrange(len(ratio)):

        for node in plot.community:
            if random.random() < ratio[r]:
                continue
            for NI in G.Nodes():    
                if NI.GetId() not in plot.community \
                        and NI.GetId() not in claimantList \
                        and random.random() < 0.40:
                    if G.GetNI(node).GetInDeg() <= 11:
                            G.AddEdge(node, NI.GetId())
    
        plot.run('aggregate_plot_round={}_{}'.format(r, '.'.join(userList)),
                claimantList,
                title='USER_ID = {}'.format('.'.join(userList)))
        
    #outerRing(G)
    #plot = plotting(G, snap.gvlNeato, True)
    #plot.run('aggregate_plot_1stLayer_{}'.format('.'.join(userList)),
    #        title='USER_ID = {}'.format('.'.join(userList)))


def outerRing(G):
    
    plot = plotting(G, snap.gvlNeato, True)
    # 1st layer
    plot.hirachical()
    print 'XXXX', len(plot.community), plot.community 
    nodeList = []
   
    for node in plot.community:
        for NI in G.Nodes():
            if snap.GetShortPath(G, NI.GetId(), node) == 1:
                if NI.GetId() not in nodeList:
                    nodeList.append(NI.GetId())
        print 'YYY', node, nodeList 

    nodeList.extend(plot.community)
    rmList = snap.TIntV()

    for NI in G.Nodes():
        if NI.GetId() not in nodeList:
            rmList.Add(NI.GetId())

    print 'ZZZ', rmList.Len()
    snap.DelNodes(G, rmList)
    
    print '\nRemove Nodes which is not the adjacent ones of CLAIMID' 
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())

    return nodeList, rmList


if __name__ == '__main__':

    userList = ['2630']
    aggregate(userList, 50, 0)
