import snap

from girvanNuewman import read_nodeadjlist
from visualization import plotting

egonetFolderName = '../data/egonets/'


def aggregate(userList):

    G = snap.TUNGraph.New()

    for userId in userList:

        filename = str(userId) + '.egonet'
        G = read_nodeadjlist(egonetFolderName + filename, G)

    plot = plotting(G, snap.gvlNeato, True)
    plot.run('aggregate_plot', 
            title='USER_ID = '.format('.'.join(userList)))


if __name__ == '__main__':

    userList = ['3581', '2976', '25708']
    aggregate(userList)
