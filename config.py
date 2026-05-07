# =============================================================================
# config.py
# COMP 323 — Neurogenesis & Graph Theory Project
# All parameters in one place — edit here, not inside source files
# =============================================================================

import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
RESULTS_FIG_DIR = os.path.join(BASE_DIR, "results", "figures")
RESULTS_MET_DIR = os.path.join(BASE_DIR, "results", "metrics")

# ── Baseline graph parameters (Days 3-4) ──────────────────────────────────────
GRAPH = {
    "n_DG":              40,      # neurons in Dentate Gyrus
    "n_CA3":             30,      # neurons in CA3
    "n_CA1":             30,      # neurons in CA1
    "inhibitory_ratio":  0.20,    # 20% of neurons are inhibitory interneurons
    "seed":              42,      # random seed for reproducibility

    # Edge connectivity rules (biological)
    "dg_ca3_out":        5,       # each DG excitatory → ~5 CA3 targets (mossy fibers)
    "ca3_recurrent":     8,       # each CA3 excitatory → ~8 CA3 targets (recurrent)
    "ca3_ca1_out":       6,       # each CA3 excitatory → ~6 CA1 targets (Schaffer)
    "inhibitory_out":    4,       # each inhibitory → ~4 local excitatory targets

    # Edge weight ranges
    "weight_exc_min":    0.5,     # excitatory synapse min strength
    "weight_exc_max":    1.0,     # excitatory synapse max strength
    "weight_inh_min":   -0.8,     # inhibitory synapse min (negative)
    "weight_inh_max":   -0.3,     # inhibitory synapse max (negative)
}

# ── Neurogenesis simulation parameters (Days 8-9) ─────────────────────────────
SIMULATION = {
    "n_new_neurons":        50,   # total new neurons to add
    "new_neuron_init_age":  0.1,  # starting age attribute
    "new_neuron_init_k":    2,    # initial number of connections

    # New neuron edge weights (weak — immature synapses)
    "new_weight_min":       0.1,
    "new_weight_max":       0.3,

    # Attachment strategies to compare
    "strategies": ["random", "preferential", "local"],

    # Local attachment age thresholds
    "local_dg_only_age":    0.3,  # age < 0.3: connect within DG only
    "local_ca3_age":        0.7,  # age 0.3–0.7: expand to CA3
    # age >= 0.7: full connectivity

    # Age increment per timestep
    "age_increment":        0.05,
}

# ── Metrics to track (Days 10-11) ─────────────────────────────────────────────
METRICS = [
    "avg_clustering_coefficient",
    "avg_shortest_path_length",
    "degree_assortativity",
    "vertex_connectivity",
    "num_fundamental_circuits",
]

# ── Visualization settings ─────────────────────────────────────────────────────
VIZ = {
    "node_colors": {
        "DG":  "#534AB7",    # purple
        "CA3": "#185FA5",    # blue
        "CA1": "#BA7517",    # amber
    },
    "cut_vertex_color":  "#E84040",    # red — critical neurons
    "bridge_color":      "#E84040",    # red — critical synapses
    "tree_edge_color":   "#1D9E75",    # green — spanning tree
    "new_neuron_color":  "#FFB703",    # gold — newly added neurons
    "fig_dpi":           150,
    "fig_size_wide":     (16, 5),
    "fig_size_quad":     (16, 12),
}

# ── Report strings ─────────────────────────────────────────────────────────────
PROJECT = {
    "title":     "Neurogenesis & Graph Theory",
    "subtitle":  "Simulating New Neuron Integration in Hippocampal Networks",
    "course":    "COMP 323 — Graph Theory",
    "university":"Kathmandu University",
    "team":      "Group B",
    "reference": "Narsingh Deo, Graph Theory (Dover, 2016)",
}