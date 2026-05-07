"""
COMP 323 - Graph Theory Project
Neurogenesis & Graph Theory: Simulating New Neuron Integration
Days 3-4: Graph Model Design

Team roles:
  M1 - writes this file
  M2 - runs and verifies each section
  M3 - computes metrics (connectivity, cut-vertices)
  M4 - documents findings for the report
"""

import networkx as nx
import numpy as np
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

random.seed(42)
np.random.seed(42)

# ============================================================
# SECTION 1: Graph definition & node creation
# COMP 323 Unit 1 - Types of Graphs, Degrees
# ============================================================

def create_hippocampal_graph(n_DG=40, n_CA3=30, n_CA1=30):
    """
    Build a directed weighted graph G = (V, E, w) modeling
    the hippocampal network.

    Node attributes:
      region : 'DG' | 'CA3' | 'CA1'
      ntype  : 'excitatory' | 'inhibitory'
      age    : float 0.0 (new) to 1.0 (mature)

    Edge attributes:
      weight : float  synaptic strength
               positive = excitatory, negative = inhibitory
    """
    G = nx.DiGraph()
    node_id = 0

    region_counts = {'DG': n_DG, 'CA3': n_CA3, 'CA1': n_CA1}
    region_nodes  = {'DG': [], 'CA3': [], 'CA1': []}

    for region, count in region_counts.items():
        for _ in range(count):
            # 20% of neurons in each region are inhibitory interneurons
            ntype = 'inhibitory' if random.random() < 0.2 else 'excitatory'
            G.add_node(node_id, region=region, ntype=ntype, age=1.0)
            region_nodes[region].append(node_id)
            node_id += 1

    # --------------------------------------------------------
    # SECTION 2: Edge creation - biological connectivity rules
    # COMP 323 Unit 1 - Paths, Subgraphs
    # --------------------------------------------------------

    def add_edge(u, v, G, excitatory=True):
        """Add directed edge with biologically realistic weight."""
        if u == v:
            return
        w = round(random.uniform(0.5, 1.0), 2) if excitatory \
            else round(random.uniform(-0.8, -0.3), 2)
        G.add_edge(u, v, weight=w)

    # Rule 1: DG -> CA3  (mossy fiber pathway)
    # Each DG excitatory neuron connects to ~5 CA3 neurons
    for u in region_nodes['DG']:
        if G.nodes[u]['ntype'] == 'excitatory':
            targets = random.sample(region_nodes['CA3'], k=min(5, n_CA3))
            for v in targets:
                add_edge(u, v, G, excitatory=True)

    # Rule 2: CA3 -> CA3  (recurrent collaterals - unique to CA3)
    # Each CA3 neuron connects to ~8 other CA3 neurons
    for u in region_nodes['CA3']:
        if G.nodes[u]['ntype'] == 'excitatory':
            others = [v for v in region_nodes['CA3'] if v != u]
            targets = random.sample(others, k=min(8, len(others)))
            for v in targets:
                add_edge(u, v, G, excitatory=True)

    # Rule 3: CA3 -> CA1  (Schaffer collaterals)
    for u in region_nodes['CA3']:
        if G.nodes[u]['ntype'] == 'excitatory':
            targets = random.sample(region_nodes['CA1'], k=min(6, n_CA1))
            for v in targets:
                add_edge(u, v, G, excitatory=True)

    # Rule 4: Local inhibitory connections within each region
    for region in ['DG', 'CA3', 'CA1']:
        inhibitory = [v for v in region_nodes[region]
                      if G.nodes[v]['ntype'] == 'inhibitory']
        excitatory = [v for v in region_nodes[region]
                      if G.nodes[v]['ntype'] == 'excitatory']
        for inh in inhibitory:
            targets = random.sample(excitatory, k=min(4, len(excitatory)))
            for v in targets:
                add_edge(inh, v, G, excitatory=False)

    return G, region_nodes

# ============================================================
# SECTION 3: Adjacency matrix & degree analysis
# COMP 323 Unit 4 - Adjacency Matrix
# COMP 323 Unit 1 - Degree Sequences
# ============================================================

def analyze_graph(G, region_nodes):
    print("=" * 55)
    print("  COMP 323 - Graph Theory Analysis (Days 3-4)")
    print("=" * 55)

    print(f"\n[Unit 1] Basic graph properties")
    print(f"  Total nodes (neurons) : {G.number_of_nodes()}")
    print(f"  Total edges (synapses): {G.number_of_edges()}")
    print(f"  Graph density         : {nx.density(G):.4f}")

    # Degree sequence (Unit 1)
    in_degrees  = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]
    print(f"\n[Unit 1] Degree sequence")
    print(f"  Max in-degree  : {max(in_degrees)}")
    print(f"  Max out-degree : {max(out_degrees)}")
    print(f"  Avg in-degree  : {np.mean(in_degrees):.2f}")
    print(f"  Avg out-degree : {np.mean(out_degrees):.2f}")

    # Adjacency matrix - small subgraph (Unit 4)
    sample = region_nodes['DG'][:5]
    sub = G.subgraph(sample)
    A = nx.to_numpy_array(sub, weight='weight')
    print(f"\n[Unit 4] Adjacency matrix (first 5 DG nodes):")
    print(np.round(A, 2))

    # Laplacian matrix (Unit 4)
    # Use unsigned weights for Laplacian
    G_unsigned = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        G_unsigned.add_edge(u, v, weight=abs(d['weight']))
    sub_u = G_unsigned.subgraph(sample)
    L = nx.laplacian_matrix(sub_u.to_undirected()).toarray()
    print(f"\n[Unit 4] Laplacian matrix L = D - A (same 5 nodes):")
    print(np.round(L, 2))

    # Connectivity (Unit 3)
    print(f"\n[Unit 3] Connectivity analysis")
    wcc = nx.number_weakly_connected_components(G)
    scc = nx.number_strongly_connected_components(G)
    print(f"  Weakly connected components  : {wcc}")
    print(f"  Strongly connected components: {scc}")
    print(f"  Is weakly connected?         : {nx.is_weakly_connected(G)}")

    # Cut vertices on undirected version (Unit 3)
    G_und = G.to_undirected()
    cut_verts = list(nx.articulation_points(G_und))
    print(f"  Cut-vertices (articulation)  : {len(cut_verts)} found")
    if cut_verts:
        sample_cv = cut_verts[:5]
        for cv in sample_cv:
            print(f"    Node {cv:3d} | region={G.nodes[cv]['region']} "
                  f"| type={G.nodes[cv]['ntype']}")

    # Shortest path DG -> CA1 (Unit 1)
    print(f"\n[Unit 1] Shortest paths DG -> CA1")
    dg_node  = region_nodes['DG'][0]
    ca1_node = region_nodes['CA1'][0]
    try:
        path = nx.shortest_path(G, dg_node, ca1_node)
        print(f"  Path: {' -> '.join(str(p) for p in path)}")
        print(f"  Path regions: {' -> '.join(G.nodes[p]['region'] for p in path)}")
        print(f"  Path length : {len(path)-1} hops")
    except nx.NetworkXNoPath:
        print("  No direct path found.")

    return in_degrees, out_degrees, cut_verts

# ============================================================
# SECTION 4: Visualizations for Day 4 verification
# ============================================================

def visualize(G, region_nodes, in_degrees, out_degrees):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("COMP 323 — Hippocampal Graph: Day 3-4 Analysis",
                 fontsize=13, fontweight='bold')

    # --- Plot 1: Degree distribution (Unit 1) ---
    ax = axes[0]
    ax.hist(in_degrees,  bins=15, alpha=0.7, color='#534AB7', label='In-degree')
    ax.hist(out_degrees, bins=15, alpha=0.7, color='#1D9E75', label='Out-degree')
    ax.set_title("Degree distribution (Unit 1)", fontsize=11)
    ax.set_xlabel("Degree")
    ax.set_ylabel("Count")
    ax.legend()

    # --- Plot 2: Adjacency matrix heatmap (Unit 4) ---
    ax = axes[1]
    sample_nodes = region_nodes['DG'][:8] + \
                   region_nodes['CA3'][:8] + \
                   region_nodes['CA1'][:8]
    sub = G.subgraph(sample_nodes)
    A   = nx.to_numpy_array(sub, weight='weight', nodelist=sample_nodes)
    im  = ax.imshow(A, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
    ax.set_title("Adjacency matrix A (Unit 4)\n8 nodes from each region", fontsize=11)
    ax.set_xlabel("Target neuron")
    ax.set_ylabel("Source neuron")
    # region boundary lines
    for boundary in [8, 16]:
        ax.axhline(boundary - 0.5, color='black', linewidth=1.5)
        ax.axvline(boundary - 0.5, color='black', linewidth=1.5)
    plt.colorbar(im, ax=ax, fraction=0.046)
    region_labels = ['DG'] * 8 + ['CA3'] * 8 + ['CA1'] * 8
    tick_pos   = [3.5, 11.5, 19.5]
    tick_label = ['DG (8)', 'CA3 (8)', 'CA1 (8)']
    ax.set_xticks(tick_pos); ax.set_xticklabels(tick_label)
    ax.set_yticks(tick_pos); ax.set_yticklabels(tick_label)

    # --- Plot 3: Network graph layout (Unit 1) ---
    ax = axes[2]
    color_map = {'DG': '#534AB7', 'CA3': '#185FA5', 'CA1': '#BA7517'}
    node_colors = [color_map[G.nodes[n]['region']] for n in G.nodes()]
    node_sizes  = [60 if G.nodes[n]['ntype'] == 'excitatory' else 30
                   for n in G.nodes()]
    pos = {}
    for i, n in enumerate(region_nodes['DG']):
        pos[n] = (0.0 + random.uniform(-0.15, 0.15),
                  i / len(region_nodes['DG']) + random.uniform(-0.05, 0.05))
    for i, n in enumerate(region_nodes['CA3']):
        pos[n] = (0.5 + random.uniform(-0.15, 0.15),
                  i / len(region_nodes['CA3']) + random.uniform(-0.05, 0.05))
    for i, n in enumerate(region_nodes['CA1']):
        pos[n] = (1.0 + random.uniform(-0.15, 0.15),
                  i / len(region_nodes['CA1']) + random.uniform(-0.05, 0.05))

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.85)
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.08,
                           arrows=True, arrowsize=6,
                           edge_color='#888780', width=0.5)
    ax.set_title("Network layout (Unit 1)\nDG | CA3 | CA1", fontsize=11)
    ax.axis('off')
    legend_patches = [
        mpatches.Patch(color='#534AB7', label='DG'),
        mpatches.Patch(color='#185FA5', label='CA3'),
        mpatches.Patch(color='#BA7517', label='CA1'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/day3_4_graph_analysis.png',
                dpi=150, bbox_inches='tight')
    print("\n  Plot saved -> day3_4_graph_analysis.png")
    plt.close()


# ============================================================
# MAIN - run everything
# ============================================================
if __name__ == "__main__":
    G, region_nodes = create_hippocampal_graph(n_DG=40, n_CA3=30, n_CA1=30)
    in_deg, out_deg, cut_verts = analyze_graph(G, region_nodes)
    visualize(G, region_nodes, in_deg, out_deg)
    print("\n  Graph object saved for Week 2 simulation.")
    print("  Next: Days 5-6 - connectivity & cut-vertex deep dive (Unit 3)")