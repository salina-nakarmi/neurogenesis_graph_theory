import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# For reproducibility across team members
random.seed(42)
np.random.seed(42)

def calculate_edge_weight(source_ntype, age_factor):
    """Total Weight = Polarity * Synaptic Strength * Maturation Factor"""
    polarity = 1.0 if source_ntype == 'excitatory' else -1.0
    synaptic_strength = random.uniform(0.5, 0.9)
    maturation_factor = age_factor
    return round(polarity * synaptic_strength * maturation_factor, 3)

# FIX 1: Set default n_immature=0 for a clean, mature baseline graph
def create_hippocampal_graph(n_DG=40, n_CA3=30, n_CA1=30, n_immature=0):
    """Constructs the Directed Weighted Graph G = (V, E)"""
    G = nx.DiGraph()
    node_id = 0
    regions = {'DG': [], 'CA3': [], 'CA1': []}
    
    # 1. Mature Nodes
    for region, count in [('DG', n_DG), ('CA3', n_CA3), ('CA1', n_CA1)]:
        for _ in range(count):
            ntype = 'inhibitory' if random.random() < 0.2 else 'excitatory'
            G.add_node(node_id, region=region, ntype=ntype, age=1.0)
            regions[region].append(node_id)
            node_id += 1
            
    # 2. Immature Nodes (DG Only)
    immature_nodes = []
    for _ in range(n_immature):
        G.add_node(node_id, region='DG', ntype='excitatory', age=0.1)
        regions['DG'].append(node_id)
        immature_nodes.append(node_id)
        node_id += 1

    # 3. Wiring Edges
    # Rule 1: DG -> CA3
    for u in regions['DG']:
        u_data = G.nodes[u]
        # Only allow mature nodes to project outward
        if u_data['ntype'] == 'excitatory' and u_data['age'] >= 0.5:
            # FIX 2: Increased k from 4 to 8 to boost baseline connectivity strength
            targets = random.sample(regions['CA3'], k=min(8, len(regions['CA3'])))
            for v in targets:
                weight = calculate_edge_weight(u_data['ntype'], u_data['age'])
                G.add_edge(u, v, weight=weight)

    # Rule 2: CA3 -> CA3 Recurrent Loops
    for u in regions['CA3']:
        u_data = G.nodes[u]
        if u_data['ntype'] == 'excitatory':
            possible_targets = [v for v in regions['CA3'] if v != u]
            # FIX 2: Increased k from 6 to 10 to ensure a robust recurrent core
            targets = random.sample(possible_targets, k=min(10, len(possible_targets)))
            for v in targets:
                weight = calculate_edge_weight(u_data['ntype'], u_data['age'])
                G.add_edge(u, v, weight=weight)

    # Rule 3: CA3 -> CA1
    for u in regions['CA3']:
        u_data = G.nodes[u]
        if u_data['ntype'] == 'excitatory':
            # FIX 2: Increased k from 5 to 8 to avoid information bottlenecks
            targets = random.sample(regions['CA1'], k=min(8, len(regions['CA1'])))
            for v in targets:
                weight = calculate_edge_weight(u_data['ntype'], u_data['age'])
                G.add_edge(u, v, weight=weight)

    # Rule 4: Local Inhibitory Regulation
    for region_name, node_list in regions.items():
        inhibitory_hubs = [n for n in node_list if G.nodes[n]['ntype'] == 'inhibitory']
        excitatory_targets = [n for n in node_list if G.nodes[n]['ntype'] == 'excitatory']
        for inh_node in inhibitory_hubs:
            inh_data = G.nodes[inh_node]
            # FIX 2: Increased k from 5 to 10 so interneurons adequately cover local pools
            targets = random.sample(excitatory_targets, k=min(10, len(excitatory_targets)))
            for v in targets:
                weight = calculate_edge_weight(inh_data['ntype'], inh_data['age'])
                G.add_edge(inh_node, v, weight=weight)

    # Rule 5: Early Integration Inputs into Newborns
    dg_inhibitory = [n for n in regions['DG'] if G.nodes[n]['ntype'] == 'inhibitory']
    for imm_node in immature_nodes:
        if dg_inhibitory:
            feeders = random.sample(dg_inhibitory, k=min(2, len(dg_inhibitory)))
            for u in feeders:
                u_data = G.nodes[u]
                weight = calculate_edge_weight(u_data['ntype'], u_data['age'])
                G.add_edge(u, imm_node, weight=weight)

    return G, regions, immature_nodes

def plot_and_save_graph(G, regions, immature_nodes):
    """Generates a clean layered layout plot and saves it as an image."""
    plt.figure(figsize=(12, 8))
    pos = {}
    
    for i, n in enumerate(regions['DG']):
        x_offset = -0.1 if n in immature_nodes else 0.0
        pos[n] = (x_offset, i / len(regions['DG']))
        
    for i, n in enumerate(regions['CA3']):
        pos[n] = (1.0, i / len(regions['CA3']))
        
    for i, n in enumerate(regions['CA1']):
        pos[n] = (2.0, i / len(regions['CA1']))

    colors = []
    sizes = []
    for n in G.nodes():
        node_data = G.nodes[n]
        if n in immature_nodes:
            colors.append('#E6AD12')
            sizes.append(120)
        elif node_data['ntype'] == 'inhibitory':
            colors.append('#C83737')
            sizes.append(60)
        else:
            mapping = {'DG': '#4A69BD', 'CA3': '#10AC84', 'CA1': '#5f27cd'}
            colors.append(mapping[node_data['region']])
            sizes.append(80)

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, alpha=0.9)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=8, 
                           edge_color='#D2D2D2', width=0.4, alpha=0.4)

    legend_elements = [
        mpatches.Patch(color='#4A69BD', label='Mature DG Excitatory'),
        mpatches.Patch(color='#10AC84', label='Mature CA3 Excitatory'),
        mpatches.Patch(color='#5f27cd', label='Mature CA1 Excitatory'),
        mpatches.Patch(color='#C83737', label='Inhibitory Interneuron (All Regions)'),
        mpatches.Patch(color='#E6AD12', label='Immature Newborn Cell (DG)'),
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=10)
    plt.title("Hippocampal Neural Graph Model (Structural Layout Framework)", fontsize=14, fontweight='bold')
    plt.axis('off')
    
    output_filename = "hippocampus_layout.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n Visual network plot successfully rendered and saved as: '{output_filename}'")

# --- EXECUTION PROFILE ---
if __name__ == "__main__":
    # Clean baseline configuration initialization
    hippocampus, layer_map, new_cells = create_hippocampal_graph()
    
    # Execute visualization generation 
    plot_and_save_graph(hippocampus, layer_map, new_cells)
    
    # Verification script for Graph Metrics 
    # Convert to undirected graph for classical connectivity metrics
    G_undirected = hippocampus.to_undirected()
    
    print("\n--- GRAPH CONNECTIVITY PROFILE VERIFICATION ---")
    print(f"Minimum Degree δ(G): {min(dict(G_undirected.degree()).values())}")
    print(f"Is Connected?        {nx.is_connected(G_undirected)}")
    if nx.is_connected(G_undirected):
        print(f"Node Connectivity κ(G): {nx.node_connectivity(G_undirected)}")
        print(f"Edge Connectivity λ(G): {nx.edge_connectivity(G_undirected)}")
