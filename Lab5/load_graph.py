import numpy as np

def load_graph(path):
    edges = np.array([])
    with open(path, 'r', encoding='utf-8', errors='ignore') as g_file:
        next(g_file) # skip the header line

        for line in g_file:
            try:
                fields = line.split(",")
                edges = np.append(edges, [int(fields[0]), int(fields[1]), int(fields[2])], axis=None)
                edges = np.reshape(edges, (-1,3))
            except Exception as e:
                pass
    return np.min(edges), np.max(edges), edges
