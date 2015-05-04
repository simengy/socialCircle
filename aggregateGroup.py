import snap

from girvanNuewman import read_nodeadjlist
from visualization import plotting

egonetFolderName = '../data/egonets/'


def aggregate(userList, inDEG=0, outDEG=0):

    G = snap.TUNGraph.New()

    for userId in userList:

        filename = str(userId) + '.egonet'
        G = read_nodeadjlist(egonetFolderName + filename, G)

    # removing the NODES with low degrees
    snap.DelDegKNodes(G, inDEG, outDEG)
    print '\nAfter, Remove Nodes with In-Degree = %d and out-Degree = %d ' % (inDEG, outDEG)
    print 'Graph has %d Nodes and %d Edges\n' % (G.GetNodes(), G.GetEdges())

    plot = plotting(G, snap.gvlNeato, True)
    plot.run('aggregate_plot_{}'.format('.'.join(userList)),
            title='USER_ID = {}'.format('.'.join(userList)))


if __name__ == '__main__':

    userList = ['2976']
    aggregate(userList, 0, 0)
