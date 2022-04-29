# settings
mygraphs = {
    "dataset1":{
        "sep": " ",
        "size": 49,
        "volume": 107,
    },
    "dataset2":{
        "sep": " ",
        "size": 112,
        "volume": 425,
    },
    "dataset3":{
        "sep": " ",
        "size": 183,
        "volume": 2494,
    },
    # "dataset4":{
    #     "sep": "\t",
    #     "size": 198,
    #     "volume": 2742,
    # },
    "dense1":{
        "sep": " ",
        "size": 62,
        "volume": 1187,
    },
    "sparse1":{
        "sep": "\t",
        "size": 62,
        "volume": 159,
    },
}
wij_range = [0,1000] # edges
wi_range = [0,1000] # nodes
#========================================================
import random
import pandas as pd
import scipy.io as scio
from tqdm import tqdm
import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def getGraph(reload=0):
    
    graphs = []

    # loading
    for gname in mygraphs:

        if reload == 0:
            g = scio.loadmat('./data/graph_weighted/%s.mat'%(gname))
            g = g['graph'][0][0]
            # print(g)
            graph = {
                'tag':g[0][0],
                'n': int(g[1][0]),
                'm': int(g[2][0]),
                'src': g[3][0].tolist(),
                'dst': g[4][0].tolist(),
                'wij': g[5].tolist(),
                'wi': g[6].tolist(),  
            }
            graphs.append(graph)

            graph = graph.copy()
            gname += '_homo'
            g = scio.loadmat('./data/graph_weighted/%s.mat'%(gname))
            g = g['graph'][0][0]
            # print(g)
            graph = {
                'tag':g[0][0],
                'n': int(g[1][0]),
                'm': int(g[2][0]),
                'src': g[3][0].tolist(),
                'dst': g[4][0].tolist(),
                'wij': g[5].tolist(),
                'wi': g[6].tolist(),  
            }
            graphs.append(graph)
            continue

        sep = mygraphs[gname]["sep"]
        g = pd.read_csv('./data/graph_source/%s'%(gname),sep=sep,header=0)
        n = mygraphs[gname]["volume"]

        # print(g)

        # attach random edge weight
        wij = [[0] * 4 for i in range(0,n)]
        for i in tqdm(range(0,n)):
            l , r = wij_range[0],wij_range[1]
            wij[i][1] = random.randint(l,r)
            wij[i][2] = random.randint(l,r)
            r = min(r, wij[i][1], wij[i][2]) # w1,4 <= w2,3
            wij[i][0] = random.randint(l,r)
            wij[i][3] = random.randint(l,r)
            # for i in range(0,4):
            #     g.insert(loc=len(g.columns), column='w%d'%(i+1), value=wij[i])
            # g.to_csv('./data/graph_weighted/%s.csv'%(gname),sep=' ',index=False,header=True)
        
        wij_homo = [[0] * 4 for i in range(0,n)]
        for i in tqdm(range(0,n)):
            l , r = wij_range[0],wij_range[1]
            wij_homo[i][1] = wij_homo[i][2] = random.randint(l,r) # w2=w3
            r = min(r, wij_homo[i][1], wij_homo[i][2]) # w1,4 <= w2,3
            wij_homo[i][0] = wij_homo[i][3] = random.randint(l,r) # w1=w4

        # attach random node weight
        wi = [[0] * 2 for i in range(0,n)]
        for i in tqdm(range(0,n)):
            l , r = wi_range[0],wi_range[1]
            wi[i][0] = random.randint(l,r)
            wi[i][1] = random.randint(l,r)

        graph = {
            'tag':gname,
            'n': mygraphs[gname]["size"],
            'm': mygraphs[gname]["volume"],
            'src':g['src'].values.tolist(),
            'dst':g['dst'].values.tolist(),
            'wij': wij,
            'wi':wi,  
        }
        graphs.append(graph)
        scio.savemat('./data/graph_weighted/%s.mat'%(gname), {'graph':graph})

        graph = graph.copy()
        gname += '_homo'
        graph['tag'] = gname
        graph['wij'] = wij_homo
        graphs.append(graph)
        scio.savemat('./data/graph_weighted/%s.mat'%(gname), {'graph':graph})

        logger.info('%s.mat created',gname)
    
        
    return graphs 

if __name__=='__main__':
    glist = getGraph(reload=1)
    # for g in glist:
    #     for it in g:
    #         print("==============",it,"==============")
    #         print(g[it])