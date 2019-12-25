import numpy as np;
import math;
from enum import Enum;

class EdgeType(Enum):
    TREE = "TREE EDGE";
    FWD = "FORWARD EDGE";
    BACK = "BACK EDGE";
    CROSS = "CROSS EDGE";

class Edge:
    
    def fields(self):
        self.vertexA = None;
        self.vertexB = None;
        self.edgeType = None;
    
    def __init__(self, vertexA, vertexB, edgeType):
        self.fields();
        self.vertexA = vertexA;
        self.vertexB = vertexB;
        self.edgeType = edgeType;
        
    def isTheSame(self, _vertexA, _vertexB):
        return ((_vertexA == self.vertexA or 
                _vertexA == self.vertexB) and 
                (_vertexB == self.vertexA or 
                 _vertexB == self.vertexB));
 

class Vertex:
    
    def fields(self):
        self.ID = -1;
        self.directions = [];
        self.graph = None;
    
    def __init__(self, ID, graph):
        self.fields();
        self.ID = ID;
        self.graph = graph;
        
    def addDirection(self, d):
        self.directions.append(d);
    
    def search(self):
        self.graph.prenum[self.ID] = self.graph.prenumID;
        self.graph.prenumID += 1;
        
        if(len(self.directions) == 0):
            #print("Dead End! at [" + str(self.ID) + "]");
            pass;
           
        else:
            for d in self.directions:      
                #print("Now in " + str(self.ID) + " going into " + str(d.ID))
                if(self.graph.prenum[d.ID] == 0):
                    self.graph.addEdge(self, d, EdgeType.TREE);
                    d.search();
                else:
                   # print("Already visited " + str(d.ID));
                    self.revisit(d);
        self.graph.postnum[self.ID] = self.graph.postnumID;
        self.graph.postnumID += 1;
    
    def revisit(self, toVertex):
        if(self.graph.prenum[self.ID] < self.graph.prenum[toVertex.ID]):
            self.graph.addEdge(self, toVertex, EdgeType.FWD);
        else:
            if(self.graph.postnumID < self.graph.postnum[toVertex.ID]):
                self.graph.addEdge(self, toVertex, EdgeType.BACK);
            else:
                self.graph.addEdge(self, toVertex, EdgeType.CROSS);
                
                
class Graph:

    def fields(self):
        self.prenum = None; #np.full(maxedge+1, 0);
        self.prenumID = 1;

        self.postnum = None; #np.full(maxedge+1, len(matrix));
        self.postnumID = 1;

        self.vertices = [];
        self.edges = []; 
    
    def __init__(self, filename):
        self.fields();
        minedge, maxedge, matrix = Graph.load_graph(filename);
        maxedge = int(maxedge);
        matrix = np.copy(matrix);
        matrix = matrix.astype(int);
        print(matrix);

        self.prenum = np.full(maxedge+1, 0);
        self.postnum = np.full(maxedge+1, 0);
        
        self.vertices = [];
        for i in range(maxedge+1):
            self.vertices.append(Vertex(i, self));

        for i in range(len(matrix)):
            vID = matrix[i,0];
            dID = matrix[i,1];
            self.vertices[vID].addDirection(self.vertices[dID]);
    
    @staticmethod
    def load_graph(path):
        edges = np.array([]);
        with open(path, 'r', encoding='utf-8', errors='ignore') as g_file:
            next(g_file); # skip the header line

            for line in g_file:
                try:
                    fields = line.split(",");
                    edges = np.append(edges, [int(fields[0]), int(fields[1])], axis=None);
                    edges = np.reshape(edges, (-1,2))
                except Exception as e:
                    pass
        return np.min(edges), np.max(edges), edges;
    
    def addEdge(self, vertexA, vertexB, edgeType):
        isNewEdge = True;
        for edge in self.edges:
            isNewEdge = isNewEdge and not edge.isTheSame(vertexA, vertexB);
            if (not isNewEdge):
                break;
        if (isNewEdge):
            self.edges.append(Edge(vertexA, vertexB, edgeType));
        
    def startSearchAt(self, vertexID):
        #clear previous results
        self.prenum = np.full(self.prenum.shape[0], 0);
        self.postnum = np.full(self.prenum.shape[0], len(self.vertices)); 
        self.prenumID = 1;
        self.posnumID = 1;
        self.edges = [];
        #and start the search
        self.vertices[vertexID].search();