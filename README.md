
# NEXORA
### Infrastructure Dependency Intelligence & Incident Impact Simulation

NEXORA is a Relate-powered infrastructure intelligence platform that models relationships between critical building, electrical, network, and application assets.

It helps users investigate infrastructure incidents, understand connected dependencies, trace potential failure paths, and simulate how the failure of one asset could affect downstream systems.

Instead of viewing infrastructure as isolated equipment, NEXORA represents it as a connected graph.

---

## The Problem

Modern facilities depend on interconnected infrastructure. Electrical systems support network equipment, network equipment connects servers, and servers host business applications.

When a critical asset fails, the effects can extend beyond the equipment itself.

Understanding those dependencies can be difficult when infrastructure information is scattered across disconnected systems.

NEXORA addresses this challenge by representing infrastructure as a graph and using graph traversal to explore downstream dependencies.

## Key Features

### 1. Infrastructure Dependency Explorer
- Visualizes relationships between infrastructure assets.
- Models electrical, network, server, and business-service dependencies.
- Uses Relate to query connected infrastructure data.

### 2. What-If Impact Simulator
- Select an infrastructure asset and simulate its failure.
- Identifies downstream assets connected to the selected asset.
- Displays affected assets and their criticality levels.
- Helps users understand the potential scope of an incident.

### 3. Incident Intelligence
- Calculates a prototype impact score based on affected asset criticality.
- Assigns an incident severity classification.
- Provides recommended investigation steps.
- Highlights potentially important downstream dependencies.

### 4. Dependency Path Tracing
- Retrieves actual graph paths from Relate.
- Shows how a selected asset connects to downstream infrastructure.
- Displays the relationships connecting each asset.
- Makes complex infrastructure dependencies easier to investigate.

### 5. Infrastructure Inventory
- Displays modeled infrastructure assets.
- Shows asset types, criticality, and operational status.
- Provides an overview of the modeled environment.

---

## How NEXORA Works

NEXORA uses a graph-based infrastructure model.

Each infrastructure component is represented as a graph node, while connections between components are represented as relationships.

### Example Infrastructure Model

```text
NEXORA Main Building
        |
     CONTAINS
        |
Main Electrical Panel
        |
      POWERS
        |
  UPS Backup Unit
        |
      POWERS
        |
Core Network Switch
       / \
      /   \
CONNECTS  CONNECTS
    /       \
Wi-Fi AP   Application Server
                  |
                HOSTS
                  |
           Business Application
```

The application queries this graph using Relate to identify downstream dependencies and retrieve connected paths.

### Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Relate by Neo4j | Graph database and relationship queries |
| Streamlit | Interactive dashboard |
| Pandas | Infrastructure data presentation |
| PyVis | Network dependency visualization |

---

## Incident Impact Methodology

NEXORA currently uses a prototype heuristic scoring model to estimate the potential impact of a simulated failure.

The score is calculated using affected asset criticality:

- Critical asset: 40 points
- High asset: 20 points
- Medium asset: 10 points

The score is capped at 100.

### Severity Classification

| Severity | Prototype criteria |
|---|---|
| CRITICAL | 2 or more critical assets, or score of 80+ |
| HIGH | At least 1 critical asset, or score of 50+ |
| MODERATE | Score of 20–49 |
| LOW | Score below 20 |

These values are prototype investigation heuristics, not measured outage probabilities or predictions of actual infrastructure failure.

---

## Example Simulations

The current demonstration graph contains seven modeled infrastructure assets and six relationships.

| Simulated Failure | Downstream Assets | Impact Score | Severity |
|---|---:|---:|---|
| Main Electrical Panel | 5 | 100/100 | CRITICAL |
| Core Network Switch | 3 | 70/100 | HIGH |

These scenarios demonstrate how graph relationships can reveal the potential downstream scope of an infrastructure incident.

---

## Getting Started

### Prerequisites

- Python 3
- pip
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/tannertyrique46-rgb/nexora.git
cd nexora
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Run the Application

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit in your browser.

The repository includes a persistent Relate database at:

```text
data/nexora.rl
```

The application uses this database to load its modeled infrastructure graph.

---

## Project Structure

```text
nexora/
│
├── app.py
│   └── Streamlit dashboard and interactive features
│
├── simulator.py
│   └── Command-line impact simulation
│
├── seed_graph.py
│   └── Infrastructure graph initialization
│
├── data/
│   └── nexora.rl
│       └── Persistent Relate graph database
│
├── README.md
│
└── LICENSE
```

---

## Current Scope and Limitations

NEXORA is a working prototype built around a modeled infrastructure environment.

- The current infrastructure graph contains demonstration data.
- Impact scores use deterministic prototype heuristics.
- The application does not currently monitor live infrastructure.
- The simulator does not predict actual equipment failures.
- Results depend on the assets and relationships represented in the graph.

The project demonstrates how graph-based infrastructure modeling can support incident investigation and dependency analysis.

---

## Hackathon Project

**Project:** NEXORA
**Category:** Infrastructure Intelligence / Graph-Based Incident Analysis
**Core Technology:** Relate by Neo4j

Repository: https://github.com/tannertyrique46-rgb/nexora

---

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
