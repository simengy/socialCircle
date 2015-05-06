import snap

from girvanNuewman import read_nodeadjlist
from visualization import plotting

egonetFolderName = '../data/egonets/'


def aggregate(userList, inDEG=0, outDEG=0):

    G = snap.TUNGraph.New()

    for userId in userList:

        filename = str(userId) + '.egonet'
        read_nodeadjlist(egonetFolderName + filename, G)
    
    # removing the NODES with low degrees
    snap.DelDegKNodes(G, inDEG, outDEG)
    print '\nAfter remove Nodes with In-Degree = %d and out-Degree = %d ' % (inDEG, outDEG)
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())
    
    # 2nd layer
    plot = plotting(G, snap.gvlNeato, True)
    plot.run('aggregate_plot_2ndLayer_{}'.format('.'.join(userList)),
            title='USER_ID = {}'.format('.'.join(userList)))
    
    outerRing(G)
    plot = plotting(G, snap.gvlNeato, True)
    plot.run('aggregate_plot_1stLayer_{}'.format('.'.join(userList)),
            title='USER_ID = {}'.format('.'.join(userList)))

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

    return rmList


if __name__ == '__main__':

    userList = ['2976']
    userList = ['2630']
    aggregate(userList, 0, 0)
