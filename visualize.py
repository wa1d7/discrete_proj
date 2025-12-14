import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional, Any

try:
    import networkx as nx
    _HAS_NX = True
except Exception:
    _HAS_NX = False

def visualize_adjacency_matrix(mat: List[List[Any]],
                               labels: Optional[List[str]] = None,
                               figsize: tuple = (6,6),
                               annotate: bool = True,
                               save_path: Optional[str] = None,
                               show: bool = True,
                               overwrite: bool = False):
    mat_arr = np.array(mat)
    n = mat_arr.shape[0]
    if mat_arr.shape[0] != mat_arr.shape[1]:
        raise ValueError("Matrix must be square n x n.")

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(mat_arr)

    idx = list(range(n))
    if labels is None:
        labels = [str(i) for i in idx]

    ax.set_xticks(idx)
    ax.set_yticks(idx)
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels)

    if annotate:
        for i in range(n):
            for j in range(n):
                ax.text(j, i, str(mat_arr[i, j]),
                        ha="center", va="center", fontsize=8)

    ax.set_title("Adjacency matrix")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()

    if save_path:
        if os.path.exists(save_path) and not overwrite:
            plt.close(fig)
            return False
        else:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            fig.savefig(save_path, dpi=200)
    if show:
        plt.show()
    plt.close(fig)
    return True

def adjacency_list_to_matrix(adj: Dict[int, List[Any]], n: Optional[int] = None) -> List[List[int]]:
    max_v = -1
    for u, neighs in adj.items():
        if isinstance(u, int):
            max_v = max(max_v, u)
        for e in neighs:
            v = e[0] if isinstance(e, tuple) else e
            if isinstance(v, int):
                max_v = max(max_v, v)
    if n is None:
        n = max_v + 1 if max_v >= 0 else 0
    mat = [[0]*n for _ in range(n)]
    for u, neighs in adj.items():
        for e in neighs:
            v = e[0] if isinstance(e, tuple) else e
            mat[u][v] = 1
    return mat

def _format_adj_text(adj: Dict[int, List[Any]]) -> str:
    lines = []
    for u in sorted(adj.keys()):
        neighs = adj[u]
        formatted = []
        for e in neighs:
            if isinstance(e, tuple):
                formatted.append(f"{e[0]}(w={e[1]})")
            else:
                formatted.append(str(e))
        lines.append(f"{u} -> {', '.join(formatted)}")
    return "\n".join(lines)

def visualize_adjacency_list(adj: Dict[int, List[Any]],
                             labels: Optional[List[str]] = None,
                             as_matrix: bool = True,
                             matrix_figsize: tuple = (6,6),
                             graph_figsize: tuple = (6,6),
                             save_matrix_path: Optional[str] = None,
                             save_graph_path: Optional[str] = None,
                             save_adj_txt_path: Optional[str] = None,
                             show: bool = True,
                             overwrite: bool = False):
    results = {"matrix": False, "graph": False, "adj_txt": False}

    if as_matrix:
        mat = adjacency_list_to_matrix(adj)
        ok = visualize_adjacency_matrix(mat, labels=labels, figsize=matrix_figsize,
                                       annotate=True, save_path=save_matrix_path,
                                       show=show, overwrite=overwrite)
        results["matrix"] = bool(ok)

    if _HAS_NX:
        G = nx.DiGraph()
        nodes = list(adj.keys())
        G.add_nodes_from(nodes)
        for u, neighs in adj.items():
            for e in neighs:
                v = e[0] if isinstance(e, tuple) else e
                G.add_edge(u, v)

        plt.figure(figsize=graph_figsize)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, arrows=True)
        plt.title("Adjacency list (graph view)")

        if save_graph_path:
            if os.path.exists(save_graph_path) and not overwrite:
                results["graph"] = False
            else:
                os.makedirs(os.path.dirname(save_graph_path) or ".", exist_ok=True)
                plt.savefig(save_graph_path, dpi=200)
                results["graph"] = True

        if show:
            plt.show()
        plt.close()
    else:
        text = _format_adj_text(adj)
        if save_adj_txt_path:
            if os.path.exists(save_adj_txt_path) and not overwrite:
                results["adj_txt"] = False
            else:
                os.makedirs(os.path.dirname(save_adj_txt_path) or ".", exist_ok=True)
                with open(save_adj_txt_path, "w", encoding="utf-8") as f:
                    f.write(text)
                results["adj_txt"] = True
        else:
            print("networkx is not installed — adjacency list output:")
            print(text)
    return results
