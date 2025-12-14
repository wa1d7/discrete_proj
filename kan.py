# kan.py
# Implementations of Kahn's algorithm for adjacency lists and adjacency matrices

from collections import deque
from typing import Dict, List, Optional, Any

def kahn_list(adj: Dict[int, List[Any]]) -> Optional[List[int]]:
    """
    Topological sorting using Kahn's algorithm for adjacency lists.
    adj: {v: [neighbour, ...]} (unweighted) or {v: [(neighbour, weight), ...]} (weighted)
    Returns list of vertices in topological order or None if a cycle exists.
    Vertices should be keys of the dict (0..n-1 or other hashable values).
    """
    # Initialize indegree
    indegree = {v: 0 for v in adj}
    # Count indegree
    for u, neighs in adj.items():
        for entry in neighs:
            if isinstance(entry, tuple):
                v = entry[0]
            else:
                v = entry
            indegree[v] += 1

    q = deque([v for v in adj if indegree[v] == 0])
    topo = []

    while q:
        v = q.popleft()
        topo.append(v)
        for entry in adj[v]:
            w = entry[0] if isinstance(entry, tuple) else entry
            indegree[w] -= 1
            if indegree[w] == 0:
                q.append(w)

    if len(topo) != len(adj):
        return None
    return topo

def kahn_matrix(mat: List[List[Any]]) -> Optional[List[int]]:
    """
    Topological sorting using Kahn's algorithm for adjacency matrix.
    mat: n x n matrix (0 or weight)
    Returns a topological order or None if a cycle exists.
    """
    n = len(mat)
    indegree = [0] * n
    # Count indegree — sum over columns
    for v in range(n):
        s = 0
        for u in range(n):
            if mat[u][v] != 0:
                s += 1
        indegree[v] = s

    q = deque([v for v in range(n) if indegree[v] == 0])
    topo = []

    while q:
        v = q.popleft()
        topo.append(v)
        # decrease indegree for all adjacent vertices
        for w in range(n):
            if mat[v][w] != 0:
                indegree[w] -= 1
                if indegree[w] == 0:
                    q.append(w)

    if len(topo) != n:
        return None
    return topo
