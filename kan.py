from collections import deque
from typing import Dict, List, Optional, Any

def kahn_list(adj: Dict[int, List[Any]]) -> Optional[List[int]]:
    indegree = {v: 0 for v in adj}
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
    n = len(mat)
    indegree = [0] * n
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
        for w in range(n):
            if mat[v][w] != 0:
                indegree[w] -= 1
                if indegree[w] == 0:
                    q.append(w)

    if len(topo) != n:
        return None
    return topo
