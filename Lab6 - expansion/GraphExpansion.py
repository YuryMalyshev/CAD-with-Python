#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np;
import math;
from enum import Enum;
import time;
import json;


# In[ ]:


class Edge:
    
    def fields(self):
        self.origin = None;
        self.destination = None;
        self.name = None;
    
    def __init__(self, origin, destination, name=None):
        self.fields(); 
        self.origin = origin;
        self.destination = destination;
        self.name = name;
    
    def toString(self):
        n = self.name;
        if(n == None):
            n = "---";
        else:
            n = "[" + n + "]"
        return "[" + str(self.origin.ID) + "]\t" + "--" + n + "->" + "\t  [" + str(self.destination.ID) + "]"


# In[ ]:


class Vertex:
    
    def fields(self):
        self.ID = None;
        self.directions = [];
        self.edges = [];
    
    def __init__(self, ID):
        self.fields();
        self.ID = ID;
        
    def addDirection(self, d, edgeName = None):
        self.directions.append(d);
        self.edges.append(Edge(self, d, edgeName));
        
    def removeDirection(self, d):
        self.directions.remove(d);
        for edge in self.edges:
            if(edge.destination == d):
                self.edges.remove(edge);
                break;
    


# In[ ]:


class Graph:
    
    def fields(self):
        self.ID = None;
        self.vertices = [];
    
    def __init__(self, ID):
        self.fields();
        self.ID = ID;
        
    def addVertex(self, vertex):
        self.vertices.append(vertex);
        
    def getVertex(self, ID):
        for v in self.vertices:
            if (v.ID == ID):
                return v;
    
    #returns True, if the graph has an embedded graph inside
    def isNonTerminal(self):
        for v in self.vertices:
            if("G" in v.ID):
                return True;
        return False;
    
    # Replaces a vertex with graph
    def replaceVertexWithGraph(self, vertex, graph):
        # Go through all named edges of the vertex representation of the graph
        for e in vertex.edges:
            if(e.name == None):
                print("[WARNING] A non terminal Vertex can't have an unnamed edge!");
            else:
                # Go through all vertices of the grapgh-to-be-inserted and find edge-vertex match
                for v in graph.vertices:
                    if( v.ID == e.name ):
                        #print("Found pin-edge match!");
                        # Map PIN to the VERTEX
                        for d in v.directions:
                            if("R" in d.ID):
                                #print("Adding " + d.ID + " as a direction to " + e.destination.ID); 
                                e.destination.addDirection(d);
                                #print("Adding " + e.destination.ID + " as a direction to " + d.ID); 
                                d.addDirection(e.destination);
                                e.destination.removeDirection(vertex);
                                d.removeDirection(v);
                                break;
                        #print("Removing " + v.ID + " From " + graph.ID);
                        graph.vertices.remove(v);
                        break;
                        
                
        # Add all vertices of expanded graph into this graph
        for v in graph.vertices:
            #print("Graph " + graph.ID + " has " + v.ID)
            self.addVertex(v);
        # Remove vertex represenation of a graph from this graph
        self.vertices.remove(vertex);
        
        print("Done inserting " + graph.ID + " into " + self.ID + " insead of " + vertex.ID + "\n");
        
                                
    # Create a copy of the graph. [Optional] Add prefix to regular vertices                
    def getCopy(self, prefix=""):
        copyGraph = Graph(self.ID);
        for v in self.vertices:
            copyVertex = Vertex(v.ID);
            copyGraph.addVertex(copyVertex);
        for cv in copyGraph.vertices:
            v = self.getVertex(cv.ID);
            for e in v.edges:
                cv.addDirection(copyGraph.getVertex(e.destination.ID), e.name);
        
        if(prefix != ""):
            for cv in copyGraph.vertices:
                if("R" in cv.ID or "G" in cv.ID):
                    cv.ID = prefix + "_" + cv.ID;
                #print(cv.ID);
        return copyGraph;
    
    # Print all edges of the graph
    def printGraph(self):
        for v in self.vertices:
            for edge in v.edges:
                print("[" + self.ID + "]   " + edge.toString());
        print();


# In[ ]:


class Loader:
    
    def __init__(self, filePath):
        
        self.graphs = [];
        
        with open(filePath) as json_file:
            data = json.load(json_file);
            
            for graph in data:
                g = Graph(graph["gname"]);
                self.graphs.append(g);
                for vertex in graph["vertices"]:
                    v = Vertex(vertex["vname"]);
                    g.addVertex(v);
                for vertex in graph["vertices"]:
                    v = g.getVertex(vertex["vname"]);
                    for dest in vertex["destinations"]:
                        dVertex = g.getVertex(dest["dname"]);
                        if(dVertex == None):
                            #print("Destination vertex [" + dest["dname"] + "] doesn't exist!");
                            pass;
                        else:
                            edgeName = None;
                            if "ename" in dest:
                                edgeName = dest["ename"];
                            v.addDirection(dVertex, edgeName);
                
                print("_"*30 + "\n" + "="*30 + "\n" + "     Original Graph " + g.ID + "\n" + "="*30 + "\n");
                g.printGraph();
                print("-"*30 + "\n\n");
        
    def expand(self, graphName, origins = []):
        graph = self.getGraph(graphName);

        if(graph == None):
            print("Unable to find graph [" + str(graphName) + "]");
            return None;
        
        graph = graph.getCopy();
        
        for g in origins:
            if(graph == g):
                print("Unable to process the expansion, graphs are pointing in a loop!");
                return None;
        origins.append(graph);
        
        for v in graph.vertices:
            if("G" in v.ID):
                #start expanding
                graphID = v.ID[v.ID.find('G'):];
                graphInstance = v.ID[:v.ID.find('G')];
                print("Expanding [" + graphID + "] Instance: [" + graphInstance + "]\n");
                addedGraph = self.expand(graphID, origins).getCopy(graphInstance + "." + graphID[1:]); #get expanded copy
                #print("Will add graph: " + addedGraph.ID + " to " + graph.ID);
                if(addedGraph == None):
                    return None;
                #print("Inserting " + addedGraph.ID + " into " + graph.ID);
                graph.replaceVertexWithGraph(v,addedGraph);
                
        print("Graph [" + graph.ID + "] is fully expanded!");
        return graph;
        
        
    def getGraph(self, name):
        for g in self.graphs:
            if(g.ID == name):
                return g;
        return None;


# In[ ]:


l2 = Loader("graphs3.json");


# In[ ]:


graph = l2.expand("G3");
if(graph != None):
    graph.printGraph();
else:
    print("ERROR");

