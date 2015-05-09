import snap
import random

from girvanNuewman import read_nodeadjlist
from visualization import plotting
from add_edges import addEdges

egonetFolderName = '../data/egonets/'


def aggregate(userList, N_CLAIM=5, inDEG=0):

    G = snap.TUNGraph.New()

    # keep the following codes for reading facebook data
    #for userId in userList:

    #    filename = str(userId) + '.egonet'
    #    read_nodeadjlist(egonetFolderName + filename, G, MAX_DEGREE = 5)
    
    claimantList = []
    for i in xrange(N_CLAIM):
        
        temp = snap.GenStar(snap.PUNGraph, random.randrange(3, 9), False)
        countID = G.GetNodes()
        
        for NI in temp.Nodes():
            G.AddNode(countID + NI.GetId())
            if random.random() < 0.35:
                claimantList.append(countID + NI.GetId())

        for E in temp.Edges():
            G.AddEdge(E.GetSrcNId()+countID, E.GetDstNId()+countID)


    # removing the NODES with low degrees
    snap.DelDegKNodes(G, inDEG, inDEG)
    print '\nAfter remove Nodes with In-Degree = %d and out-Degree = %d ' % (inDEG, inDEG)
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())

    # Multi-layer network recovery
    plot = plotting(G, snap.gvlNeato, True)
    plot.hirachical()
   
    # group split
    pos1 = 0
    pos2 = 0
    group = [0.5, 0.3, 0.2, 0.1] # specify the portion of data to split
    neighbor = []

    N = len(plot.community)
    # normalizatoin
    group = [float(i)/sum(group) for i in group]

    for i in xrange(len(group)):

        pos2 = pos1 + int(group[i] * N)

        temp = []
        for g in plot.community[pos1:pos2]:
            
            for NI in G.Nodes():
                
                if snap.GetShortPath(G, NI.GetId(), g) == 1:

                    temp.append(NI.GetId())
                
        neighbor.append(temp)
        pos1 = pos2


    # Add extra links
    ratio = [0.0, 0.4, 0.8] # the multi-layer effect by adding links layer by layer
    in_w = 0.3 # the density of in-group edges
    between_w = 0.3 # the density of between-group edges
    in_deg = 14
    between_deg = 12

    for r in xrange(len(ratio)):
        
        # multi-layer loop
        pos1 = 0
        pos2 = 0

        for i in xrange(len(group)):
        
            # sub-group loop
            pos2 = pos1 + int(N * group[i])
            
            for node in plot.community[pos1:pos2]:
                
                if random.random() > ratio[r]:
                    continue
                
                # inter-group
                for NI in neighbor[i]:

                    if NI not in plot.community \
                            and NI not in claimantList \
                            and random.random() < in_w:
                        if G.GetNI(node).GetInDeg() <= in_deg:
                                G.AddEdge(node, NI)
                
                #intra-group: adjusting the index periodically but leave off the last element for fraud ring 
                if i == len(group)-2: 
                    k = 0
                elif i == len(group)-1:
                    continue
                else:
                    k = i + 1
                
                for NI in neighbor[k]:

                    if NI not in plot.community \
                            and NI not in claimantList \
                            and random.random() < between_w:
                        if G.GetNI(node).GetInDeg() <= between_deg:
                                G.AddEdge(node, NI)

            plot.run('aggregate_plot_round={}_{}'.format(r, '.'.join(userList)),
                    claimantList,
                    title='USER_ID = {}'.format('.'.join(userList)))
            
            pos1 = pos2
        
        
    #removeLink(G)
    #plot = plotting(G, snap.gvlNeato, True)
    #plot.run('aggregate_plot_1stLayer_{}'.format('.'.join(userList)),
    #        title='USER_ID = {}'.format('.'.join(userList)))


def removeLink(G):
    
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
    
    print '\nRemoving Nodes which is not the adjacent ones of CLAIMID' 
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())

    return nodeList, rmList


if __name__ == '__main__':

    userList = ['77']
    aggregate(userList, 50, 0)
