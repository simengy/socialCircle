import snap
import random

PLOT_DIR = '../plot'
SAVE_DIR = '../social'

class plotting:

    def __init__(self, graph, layout, printLabel=True):

        # Degree of Edge: Role, Color, Weight
        self.groups = {
                0:[['ClaimID','yellow',0.4],],
                1:[['Doctor', 'red', 0.3],
                    ['Body Shop', 'yellow', 0.3], 
                    ['Towing company', 'orange', 0.3],
                    ['Inspector', 'blue', 0.3],
                    ['Lawyer', 'purple', 0.2]],
                2:[['Claimant', 'green', 0.7]]
                }

        self.G = graph
        self.layout = layout
        self.printLabel = printLabel
        self.labels = snap.TIntStrH()
        self.NIdColorH = snap.TIntStrH()
        self.nameList = {} # nameList is only been assigned once
        
    
    def weighted_choice(self, key):
    
        total = sum(w for name, col, w in self.groups[key])
        r = random.uniform(0., total)
        upto = 0.
    
        for name, col, w in self.groups[key]:
        
            if upto + w  > r:
                return name, col
            upto += w
        
        assert False, "Shouldn't get here"

    
    def segDegree(self, degree):
        
        if degree == 0:
            return None
        else:
            return 1
            

    def hirachical(self):
        
        community = None

        # select Insured Nodes
        for NI in self.G.Nodes():
            flag = True
            
            if random.random() > 0.0 and NI.GetInDeg() >= 2:
            
                if community is None:
                    community = [NI.GetId(),]
                else:
                    for temp in community:
                        if snap.GetShortPath(self.G, NI.GetId(), temp) == 1:
                            flag = False
                            break
                    if flag == True:
                        community.append(NI.GetId())
            
        self.community = community 

    def run(self, filename, claimantList, title='title'):
        
        # First to select Insured nodes
        self.hirachical()
        
        Nodes = snap.TIntFltH()
        snap.GetPageRank(self.G, Nodes)

        for NI in self.G.Nodes():
            if NI.GetId() in self.community:
                bucket = 0
            elif NI.GetId() in claimantList:
                bucket = 2
            else:
                bucket = self.segDegree(NI.GetInDeg())
            
            # hacked 'col' in Pajek for network metric 
            if NI.GetId() not in self.nameList: 
                name, _ = self.weighted_choice(bucket)
                self.nameList[NI.GetId()] = name
            else:
                name = self.nameList[NI.GetId()]
            
            if name == 'ClaimID':
                col = 5.0
            else:
                col = Nodes[NI.GetId()] * 2000
            
            #print NI.GetId(), NI.GetInDeg(), NI.GetOutDeg(), name, col
            if self.printLabel:
                self.labels[NI.GetId()] = name
            else:
                self.labels[NI.GetId()] = str(NI.GetId())
            
            self.NIdColorH[NI.GetId()] = str(col)
            

        snap.DrawGViz(self.G, self.layout, 
                '{}/{}.png'.format(PLOT_DIR, filename),
                title, self.labels, self.NIdColorH)
        snap.SavePajek(self.G, '{}/{}.net'.format(SAVE_DIR, filename),
            self.NIdColorH, self.labels)
        

if __name__ == '__main__':

    #G = snap.GenRndGnm(snap.PUNGraph, 30, 130)
    G = snap.GenRndGnm(snap.PNEANet, 30, 50)
    plot = plotting(G, snap.gvlTwopi)
    plot.run('test', 'we like this network')
