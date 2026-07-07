"""
simulation.py — Days 8-9 deliverable. THE single source of truth for the
neurogenesis wiring rules.

WHAT THIS FILE DOES: starts from the baseline graph (graph_model.py),
then adds 50 new DG neurons one at a time using one of three attachment
strategies:

  Random        — connects to random inhibitory/CA3 targets (brief §6.2)
  Preferential  — connects to targets weighted by current degree, P(v) = deg(v)/sum(deg)
  Local         — age-gated: DG-only while age < local_dg_only_age,
                  expands to CA3 once age crosses local_dg_only_age,
                  expands to CA1 once age crosses local_ca3_age.
                  (This is the "local attachment" strategy from brief §3.2/B3
                  — earlier code had mislabeled a fixed denser-wiring rule
                  as "Niche_Targeted"; that didn't age-gate anything.)

At every timestep it logs the metrics needed to test all three central
propositions in the brief (§7):
  - Kappa/Lambda/Min_Degree/Avg_Degree/Clustering_Coeff, every step
  - Avg_Shortest_Path, every step               (Proposition 1)
  - Fundamental_Circuits, Is_Planar, at t=0/25/50 only, i.e. config
    SIMULATION["checkpoints"] — these are cheap but not free, and the
    brief only asks us to verify them at those 3 checkpoints (Prop 2, 3).
    t=0 is logged explicitly before any newborn is added, so each
    strategy's log is self-contained (previously t=0 had to be borrowed
    from connectivity.py's separate baseline run).

Undirected conversion uses connectivity.py's to_undirected_abs(), matching
Assumption C2 in the brief (metrics computed on the undirected graph with
absolute-value weights) — this used to be done two different, inconsistent
ways across files.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx
import numpy as np
import random
import csv

from graph_model import create_hippocampal_graph, calculate_edge_weight
from connectivity import to_undirected_abs
from config import GRAPH, SIMULATION


def get_preferential_targets(G, pool, k):
    """Selects targets based on node degree probability (Preferential Attachment)."""
    degrees = np.array([G.degree(n) for n in pool], dtype=float)
    if degrees.sum() == 0:
        return random.sample(pool, k=k)
    probs = degrees / degrees.sum()
    return list(np.random.choice(pool, size=k, replace=False, p=probs))


# ─────────────────────────────────────────────────────────────────────────
# Wiring rules — one function per strategy, called once per new neuron
# ─────────────────────────────────────────────────────────────────────────

def _wire_random(G, regions, new_node):
    dg_inh = [n for n in regions['DG'] if G.nodes[n]['ntype'] == 'inhibitory' and n != new_node]
    if dg_inh:
        for u in random.sample(dg_inh, k=min(2, len(dg_inh))):
            G.add_edge(u, new_node, weight=calculate_edge_weight('inhibitory', 1.0))
    if regions['CA3']:
        for v in random.sample(regions['CA3'], k=min(3, len(regions['CA3']))):
            G.add_edge(new_node, v, weight=calculate_edge_weight('excitatory', 0.1))


def _wire_preferential(G, regions, new_node):
    dg_inh = [n for n in regions['DG'] if G.nodes[n]['ntype'] == 'inhibitory' and n != new_node]
    if dg_inh:
        for u in get_preferential_targets(G, dg_inh, k=min(2, len(dg_inh))):
            G.add_edge(u, new_node, weight=calculate_edge_weight('inhibitory', 1.0))
    if regions['CA3']:
        for v in get_preferential_targets(G, regions['CA3'], k=min(3, len(regions['CA3']))):
            G.add_edge(new_node, v, weight=calculate_edge_weight('excitatory', 0.1))


def _wire_local_birth(G, regions, new_node):
    """At birth (age = new_neuron_init_age < local_dg_only_age): DG-only wiring."""
    dg_inh = [n for n in regions['DG'] if G.nodes[n]['ntype'] == 'inhibitory' and n != new_node]
    if dg_inh:
        for u in random.sample(dg_inh, k=min(2, len(dg_inh))):
            G.add_edge(u, new_node, weight=calculate_edge_weight('inhibitory', 1.0))


def _wire_local_expand_ca3(G, regions, node):
    """Neuron crossed local_dg_only_age: gains its first CA3 projections."""
    if regions['CA3']:
        for v in random.sample(regions['CA3'], k=min(3, len(regions['CA3']))):
            G.add_edge(node, v, weight=calculate_edge_weight('excitatory', 0.4))


def _wire_local_expand_ca1(G, regions, node):
    """Neuron crossed local_ca3_age: reaches full maturity, gains CA1 projections."""
    if regions['CA1']:
        for v in random.sample(regions['CA1'], k=min(2, len(regions['CA1']))):
            G.add_edge(node, v, weight=calculate_edge_weight('excitatory', 0.8))


# ─────────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────────

def _avg_shortest_path(G_und):
    """Average shortest path length; falls back to the largest connected
    component if the graph is (temporarily) disconnected."""
    if nx.is_connected(G_und):
        return round(nx.average_shortest_path_length(G_und), 4)
    largest_cc = max(nx.connected_components(G_und), key=len)
    sub = G_und.subgraph(largest_cc)
    return round(nx.average_shortest_path_length(sub), 4)


def _fundamental_circuits(G_und):
    """m - (n - 1): non-tree edges = fundamental circuits (Narsingh Deo §2.5)."""
    n, m = G_und.number_of_nodes(), G_und.number_of_edges()
    T = nx.minimum_spanning_tree(G_und, weight="weight")
    return m - T.number_of_edges()


# ─────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────

def run_neurogenesis_experiment(strategy_name, n_newborns=None, return_graph=False):
    """Runs the neuron-integration loop and returns per-timestep metric logs.

    If return_graph=True, also returns the final (G, regions) so callers
    like functional_simulation.py can run further experiments on the same
    network instead of re-implementing the wiring rules themselves.
    """
    n_newborns = SIMULATION["n_newborns"] if n_newborns is None else n_newborns
    checkpoints = set(SIMULATION["checkpoints"])

    # Re-seed here (not just once at graph_model import time) so every
    # strategy starts from an IDENTICAL baseline graph. Without this,
    # whichever strategy runs first consumes random-module state that the
    # next strategy's create_hippocampal_graph() call inherits — meaning
    # "baseline" silently differed strategy to strategy (caught via the
    # t=0 fundamental-circuit counts not matching across strategies).
    random.seed(GRAPH["seed"])
    np.random.seed(GRAPH["seed"])

    G, regions, _ = create_hippocampal_graph(n_immature=0)
    immature_tracker = []  # nodes still maturing, only used by "Local"
    logs = []

    # ── t=0 baseline checkpoint, logged BEFORE any newborn is added ──
    # (previously missing: the loop started at i=1, so t=0 was never
    # recorded here and had to be borrowed from connectivity.py's
    # separate run — same seed/config so numerically identical, but not
    # self-contained. Now every strategy's log starts from its own t=0.)
    G_und0 = to_undirected_abs(G)
    circuits0 = _fundamental_circuits(G_und0)
    is_planar0, _ = nx.check_planarity(G_und0)
    logs.append({
        'Strategy': strategy_name,
        'Newborns_Added': 0,
        'Kappa': nx.node_connectivity(G_und0) if nx.is_connected(G_und0) else 0,
        'Lambda': nx.edge_connectivity(G_und0) if nx.is_connected(G_und0) else 0,
        'Min_Degree': min(dict(G_und0.degree()).values()),
        'Avg_Degree': round(np.mean(list(dict(G_und0.degree()).values())), 3),
        'Clustering_Coeff': round(nx.average_clustering(G_und0), 4),
        'Avg_Shortest_Path': _avg_shortest_path(G_und0),
        'Fundamental_Circuits': circuits0,
        'Is_Planar': is_planar0,
    })

    for i in range(1, n_newborns + 1):
        new_node = max(G.nodes()) + 1
        G.add_node(new_node, region='DG', ntype='excitatory',
                   age=SIMULATION["new_neuron_init_age"])
        regions['DG'].append(new_node)

        if strategy_name == "Random":
            _wire_random(G, regions, new_node)
        elif strategy_name == "Preferential":
            _wire_preferential(G, regions, new_node)
        elif strategy_name == "Local":
            _wire_local_birth(G, regions, new_node)
            immature_tracker.append(new_node)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # Local strategy: age every immature neuron, expand wiring on crossing thresholds
        if strategy_name == "Local":
            for node in immature_tracker:
                old_age = G.nodes[node]['age']
                new_age = min(1.0, old_age + SIMULATION["age_increment"])
                G.nodes[node]['age'] = new_age
                if old_age < SIMULATION["local_dg_only_age"] <= new_age:
                    _wire_local_expand_ca3(G, regions, node)
                if old_age < SIMULATION["local_ca3_age"] <= new_age:
                    _wire_local_expand_ca1(G, regions, node)

        # ── Metrics (Assumption C2: undirected, absolute-weight version) ──
        G_und = to_undirected_abs(G)
        min_deg = min(dict(G_und.degree()).values())
        avg_deg = np.mean(list(dict(G_und.degree()).values()))
        clust_coeff = nx.average_clustering(G_und)

        if nx.is_connected(G_und):
            kappa = nx.node_connectivity(G_und)
            lambda_val = nx.edge_connectivity(G_und)
        else:
            kappa, lambda_val = 0, 0

        avg_path = _avg_shortest_path(G_und)

        # Expensive/checkpoint-only metrics (Propositions 2 & 3)
        circuits, is_planar = None, None
        if i in checkpoints or i == n_newborns:
            circuits = _fundamental_circuits(G_und)
            is_planar, _ = nx.check_planarity(G_und)

        logs.append({
            'Strategy': strategy_name,
            'Newborns_Added': i,
            'Kappa': kappa,
            'Lambda': lambda_val,
            'Min_Degree': min_deg,
            'Avg_Degree': round(avg_deg, 3),
            'Clustering_Coeff': round(clust_coeff, 4),
            'Avg_Shortest_Path': avg_path,
            'Fundamental_Circuits': circuits,
            'Is_Planar': is_planar,
        })

    if return_graph:
        return logs, G, regions
    return logs


# --- EXECUTION PROFILE ---
if __name__ == "__main__":
    print("Starting Week 2 Neurogenesis Simulations...")
    all_results = []

    for strategy in SIMULATION["strategies"]:
        print(f"-> Simulating implementation: {strategy}")
        strategy_logs = run_neurogenesis_experiment(strategy)
        all_results.extend(strategy_logs)

    csv_file = "simulation_metrics.csv"
    fields = ['Strategy', 'Newborns_Added', 'Kappa', 'Lambda', 'Min_Degree',
              'Avg_Degree', 'Clustering_Coeff', 'Avg_Shortest_Path',
              'Fundamental_Circuits', 'Is_Planar']

    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n[Milestone Reached] Simulation complete. Logs saved to: '{csv_file}'")