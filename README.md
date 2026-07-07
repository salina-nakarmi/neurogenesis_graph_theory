# Neurogenesis & Graph Theory
### Simulating New Neuron Integration in Hippocampal Networks

> **COMP 323 — Graph Theory** | Kathmandu University | B.Sc. III Year – II Semester  
> Group B · 4 Members · 2-Week Project  
> Reference: Narsingh Deo, *Graph Theory with Applications* (Dover, 2016)

---

## 📌 Project Overview

This project models the hippocampal neural network as a **directed weighted graph**
`G = (V, E, w)` and simulates adult neurogenesis by iteratively adding new neurons
using three biologically motivated attachment strategies. Using formal graph theory
tools from COMP 323, we track how structural properties evolve over 50 timesteps.

**Core Question:**  
> *How do graph-theoretic properties change as new neurons integrate into the hippocampal network — and does the attachment mechanism matter?*

---

## 🧠 Biological Background

The hippocampus contains three key subregions forming the **trisynaptic circuit**:

```
DG  ──mossy fibers──▶  CA3  ──Schaffer collaterals──▶  CA1
(neurogenesis zone)   (recurrent)                    (output)
```

New neurons are born exclusively in the **Dentate Gyrus (DG)** and gradually
integrate over 4–8 weeks (Eriksson, 1998; van Praag, 1999).

---

## 📐 Graph Theory Model

| Component | Graph Element | Attributes |
|-----------|--------------|------------|
| Neuron | Node `v ∈ V` | `region` (DG/CA3/CA1), `ntype` (excitatory/inhibitory), `age` [0,1] |
| Synapse | Directed edge `(u,v) ∈ E` | `weight` ∈ [−1, +1] |
| Synaptic strength | Weight `w(u,v)` | Positive = excitatory, Negative = inhibitory |

**COMP 323 Units exercised:**

| Unit | Topic | Application |
|------|-------|-------------|
| Unit 1 | Fundamental concepts | Degree sequences, Euler/Hamiltonian paths |
| Unit 2 | Trees | Spanning trees, fundamental circuits |
| Unit 3 | Connectivity & planarity | Cut-vertices, κ(G), Whitney's theorem, Kuratowski |
| Unit 4 | Matrix representation | Adjacency matrix A, Laplacian L, cycle matrix B |
| Unit 5 | Graph coloring | Chromatic number for excitatory/inhibitory separation |
| Unit 7 | Operations research | Min-cost flow for signal propagation |

---

## 📁 Project Structure

```
neurogenesis_graph_theory/
│
├── src/                        # All source code
│   ├── __init__.py
│   ├── graph_model.py          # Day 3-4: G=(V,E,w) construction
│   ├── connectivity.py         # Day 5-6: Unit 3 analysis
│   ├── simulation.py           # Day 8-9: Neurogenesis loop
│   ├── metrics.py              # Day 10-11: All graph metrics
│   └── visualize.py            # Plotting and graph snapshots
│
├── data/
│   ├── raw/                    # Raw graph exports (.pkl, .graphml)
│   └── processed/              # CSV metric logs from simulation
│
├── results/
│   ├── figures/                # All output plots (.png)
│   └── metrics/                # Summary tables (.csv)
│
├── tests/                      # Unit tests for each module
│   ├── test_graph_model.py
│   ├── test_connectivity.py
│   └── test_simulation.py
│
├── notebooks/                  # Jupyter exploration (optional)
│   └── exploration.ipynb
│
├── docs/                       # Supporting documents
│   └── references.md
│
├── main.py                     # Single entry point — runs everything
├── config.py                   # All parameters in one place
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/neurogenesis_graph_theory.git
cd neurogenesis_graph_theory
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the full pipeline
```bash
python main.py
```

---

## 🚀 Usage

### Run full pipeline (all phases)
```bash
python main.py
```

### Run individual phases
```bash
python main.py --phase baseline      # Days 3-4: build graph
python main.py --phase connectivity  # Days 5-6: Unit 3 analysis
python main.py --phase simulate      # Days 8-9: neurogenesis
python main.py --phase analyze       # Days 10-11: plots & metrics
```

### Run tests
```bash
pytest tests/ -v
```

---

## 📊 Key Results (Baseline)

| Metric | Value |
|--------|-------|
| Nodes (neurons) | 100 |
| Edges (synapses) | ~548 |
| Graph density | 0.057 |
| Vertex connectivity κ(G) | 3 |
| Edge connectivity λ(G) | 3 |
| Min degree δ(G) | 3 |
| Whitney's theorem κ ≤ λ ≤ δ | ✓ 3 ≤ 3 ≤ 3 |
| Fundamental circuits | 449 |
| Planarity (full graph) | Non-planar |
| Planarity (10-node subgraph) | Planar ✓ |

---

## 👥 Team & Responsibilities

| Member | Role | Modules |
|--------|------|---------|
| M1 | Lead coder — graph build + simulation | `graph_model.py`, `simulation.py` |
| M2 | Data analyst — metrics + plots | `metrics.py`, `visualize.py` |
| M3 | Graph theory lead — connectivity proofs | `connectivity.py`, `tests/` |
| M4 | Report + presentation | `docs/`, README, slides |

---

## 📚 References

- Narsingh Deo, *Graph Theory with Applications to Engineering & Computer Science*, Dover, 2016
- Andersen et al. (1971) — Trisynaptic hippocampal circuit
- Eriksson et al. (1998) — Neurogenesis in adult human hippocampus
- van Praag et al. (1999) — Running enhances neurogenesis
- Pelkey et al. (2017) — Hippocampal GABAergic inhibitory interneurons
- Turrigiano (2008) — Synaptic homeostasis
- Barabási & Albert (1999) — Emergence of scaling in random networks
- Watts & Strogatz (1998) — Collective dynamics of small-world networks
  *(grounds Proposition 1: "preserves small-world structure" — high
  clustering + short average path length — is Watts-Strogatz terminology,
  not our own; this paper was missing from the original reference list.)*
- DeFelipe (2012) — Cortical/hippocampal excitatory:inhibitory ratio
  *(grounds the 80%/20% excitatory:inhibitory split used in `config.py`.
  Note: Pelkey et al. (2017) reports a narrower ~10–15% inhibitory
  estimate specific to local hippocampal interneurons; DeFelipe's ~20%
  figure is the more commonly used convention in computational models
  and is the one our `inhibitory_ratio` actually matches.)*

---

## 📄 License

MIT License — free to use, modify, and extend for academic purposes.