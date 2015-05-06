import snap
import pandas as pd
from datetime import datetime

from visualization import plotting


#%% set script params
# params
MAX_DEGREE = 5
tooLittleFriendsInCircleThreshold = 5
tooManyNodesThreshold = 200
submissionNumber = datetime.strftime(datetime.today(), '%Y-%m-%d_%H:%M:%S')

# folder paths
egonetFolderName = '../data/egonets/'
submissionFolderName = '../IDs/'


#%% some function definitions
def read_nodeadjlist(filename, G):
    
    #G = snap.TUNGraph.New()
    
    for line in open(filename):
        e1, es = line.split(':')
        es = es.split()
        
        # There are duplicate edges
        try:
            G.AddNode(int(e1))
        except Exception, err:
            #print "Warning: ", err
            pass
         
        for e in es:

            try:
                G.AddNode(int(e))
            except:
                #print "Warning2: "
                pass
            
            if e == e1: continue            
            if G.GetNI(int(e1)).GetDeg() >= MAX_DEGREE:
                break
            if G.GetNI(int(e)).GetDeg() >= MAX_DEGREE:
                continue
            try:
                G.AddEdge(int(e1), int(e))
            except:
                #print "Warning3: "
                pass

    print 'G: Nodes %d, Edges %d' % (G.GetNodes(), G.GetEdges())


def findCommunity():
    #%% make a submission
    submission = pd.read_csv(submissionFolderName + 'sample_submission.csv')
    #submission = pd.read_csv(submissionFolderName + 'train_ID.csv')
    
    for userId in list(submission['UserId']):

        # read graph
        filename = str(userId) + '.egonet'
        G = snap.TUNGraph.New()
        read_nodeadjlist(egonetFolderName + filename, G)

        # do not calculate for large graphs (it takes too long)
        if G.GetNodes() > tooManyNodesThreshold:
            print 'skipping user ' + str(userId)    
            continue
        else:
            print 'predicting for user ' + str(userId)

        # visualization
        plot = plotting(G, snap.gvlNeato)
        plot.run('gviz_plot_{}'.format(userId), 
                title='UserID = {}'.format(userId))
    
        # find comunities by using GirvanNewman
        listOfCircles = []
        CmtyV = snap.TCnComV()
        modularity = snap.CommunityGirvanNewman(G, CmtyV)
        for Cmty in CmtyV:
            #print 'Community'
            
            # leave only relativly large communities
            if len(Cmty) >= tooLittleFriendsInCircleThreshold:
                listOfCircles.append(list(Cmty))
            
            for NI in Cmty:
                #print NI
                continue
        print 'The modularity of the network is %f' % modularity
    
        # populate prediction string
        predictionString = ''
        for Cmty in listOfCircles:
            for NI in Cmty:
                predictionString = predictionString + str(NI) + ' '
        
        predictionString = predictionString[:-1]

        # if no prediction was created, use 'all friends in one circle'
        if len(listOfCircles) > 0:
            submission.ix[submission['UserId'] == userId, 'Predicted'] = predictionString


    submission.to_csv(submissionFolderName + str(submissionNumber) + '.csv', index=False)


if __name__ == '__main__':

    findCommunity()
