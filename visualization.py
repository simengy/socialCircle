import snap
import random

PLOT_DIR = '../plot'
SAVE_DIR = '../social'

class plotting:

    def __init__(self, graph, layout, printLabel=True):

        # Choice, Color, Weight
        self.groups = [['Claimant', 'green', 0.75],
                ['Doctor', 'red', 0.1], 
                ['Body Shop', 'yellow', 0.05], 
                ['Agent', 'blue', 0.1]]

        self.G = graph
        self.layout = layout
        self.printLabel = printLabel
        self.labels = snap.TIntStrH()
        self.NIdColorH = snap.TIntStrH()
        
    def weighted_choice(self):
    
        total = sum(w for name, col, w in self.groups)
        r = random.uniform(0., total)
        upto = 0.
    
        for name, col, w in self.groups:
        
            if upto + w  > r:
                return name, col
            upto += w
        
        assert False, "Shouldn't get here"

    def run(self, filename, title='title'):
        
        for NI in self.G.Nodes():
    
            name, col = self.weighted_choice()
            
            print NI.GetId(), name, col
            if self.printLabel:
                self.labels[NI.GetId()] = name
            else:
                self.labels[NI.GetId()] = str(NI.GetId())
            
            self.NIdColorH[NI.GetId()] = col
            

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
