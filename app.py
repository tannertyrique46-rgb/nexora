import streamlit as st
import relate
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

# ==========================================
# NEXORA CONFIGURATION
# ==========================================

DATABASE = "./data/nexora.rl"

st.set_page_config(
    page_title="NEXORA | Infrastructure Intelligence",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 NEXORA")
st.caption("Infrastructure Intelligence & Dependency Analysis")


# ==========================================
# RELATE DATABASE QUERIES
# ==========================================

@st.cache_data
def load_assets():
    with relate.connect(DATABASE) as db:
        return db.execute("""
            MATCH (n:Asset)
            RETURN n.name AS name,
                   labels(n) AS asset_type,
                   n.status AS status,
                   n.criticality AS criticality
        """).data()


@st.cache_data
def load_relationships():
    with relate.connect(DATABASE) as db:
        return db.execute("""
            MATCH (a:Asset)-[r]->(b:Asset)
            RETURN a.name AS source,
                   type(r) AS relationship,
                   b.name AS target
        """).data()


def simulate_failure(asset_name):
    with relate.connect(DATABASE) as db:
        return db.execute("""
            MATCH (source:Asset {name: $asset_name})
            MATCH (source)-[*1..]->(affected:Asset)
            RETURN DISTINCT
                affected.name AS asset,
                labels(affected) AS asset_type,
                affected.criticality AS criticality,
                affected.status AS status
        """, {"asset_name": asset_name}).data()


def load_dependency_paths(asset_name):
    with relate.connect(DATABASE) as db:
        result = db.execute("""
            MATCH p=(source:Asset {name: $asset_name})
                  -[*1..]->(affected:Asset)
            RETURN p
        """, {"asset_name": asset_name})

        rows = result.data()

    paths = []

    for row in rows:
        path_data = row["p"].to_dict()

        nodes = []

        for node in path_data["nodes"]:
            properties = node["properties"]

            nodes.append({
                "name": properties.get("name", "Unknown"),
                "criticality": properties.get(
                    "criticality", "Unknown"
                ),
                "status": properties.get(
                    "status", "Unknown"
                ),
                "type": [
                    label for label in node["labels"]
                    if label != "Asset"
                ]
            })

        relationships = [
            relationship["type"]
            for relationship in path_data["relationships"]
        ]

        paths.append({
            "nodes": nodes,
            "relationships": relationships
        })

    return paths


# ==========================================
# LOAD INFRASTRUCTURE DATA
# ==========================================

assets = load_assets()
relationships = load_relationships()


# ==========================================
# INFRASTRUCTURE OVERVIEW
# ==========================================

st.subheader("Infrastructure Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Assets", len(assets))
col2.metric("Relationships", len(relationships))

col3.metric(
    "Critical Assets",
    sum(
        1 for asset in assets
        if asset["criticality"] == "Critical"
    )
)

st.divider()


# ==========================================
# DEPENDENCY EXPLORER
# ==========================================

left, right = st.columns([1.4, 1])

with left:

    st.subheader("Dependency Explorer")

    network = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#111827",
        font_color="white"
    )

    network.set_options("""
    {
      "nodes": {
        "shape": "dot",
        "size": 28,
        "font": {
          "size": 18,
          "color": "#F9FAFB"
        },
        "borderWidth": 2
      },
      "edges": {
        "width": 2,
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "color": {
          "color": "#64748b",
          "highlight": "#f59e0b"
        },
        "font": {
          "size": 13,
          "color": "#e5e7eb"
        }
      },
      "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 180,
          "springConstant": 0.08
        },
        "stabilization": {
          "enabled": true,
          "iterations": 150
        }
      }
    }
    """)

    for asset in assets:

        network.add_node(
            asset["name"],
            label=asset["name"],
            title=f'Criticality: {asset["criticality"]}',
            color=(
                "#ef4444"
                if asset["criticality"] == "Critical"
                else "#3b82f6"
            )
        )

    for relationship in relationships:

        network.add_edge(
            relationship["source"],
            relationship["target"],
            label=relationship["relationship"],
            arrows="to"
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html"
    ) as file:

        network.save_graph(file.name)
        html_path = file.name

    with open(
        html_path,
        "r",
        encoding="utf-8"
    ) as file:

        components.html(
            file.read(),
            height=670,
            scrolling=True
        )


# ==========================================
# ASSET INVENTORY
# ==========================================

with right:

    st.subheader("Asset Inventory")

    inventory = pd.DataFrame([
        {
            "Asset": asset["name"],
            "Type": ", ".join(asset["asset_type"]),
            "Status": asset["status"],
            "Criticality": asset["criticality"]
        }
        for asset in assets
    ])

    st.dataframe(
        inventory,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# WHAT-IF IMPACT SIMULATOR
# ==========================================

st.divider()

st.subheader("⚡ What-If Impact Simulator")

st.write(
    "Select an infrastructure asset to simulate its failure "
    "and identify downstream dependencies."
)

asset_names = [
    asset["name"]
    for asset in assets
]

selected_asset = st.selectbox(
    "Select an asset",
    asset_names,
    index=(
        asset_names.index("Core Network Switch")
        if "Core Network Switch" in asset_names
        else 0
    )
)


if st.button("Simulate Failure", type="primary"):

    impacts = simulate_failure(selected_asset)

    st.markdown(
        f"### Impact Analysis: {selected_asset}"
    )

    if impacts:

        st.warning(
            f"{len(impacts)} downstream asset(s) "
            "may be affected."
        )

        impact_data = pd.DataFrame([
            {
                "Affected Asset": item["asset"],
                "Type": ", ".join(item["asset_type"]),
                "Criticality": item["criticality"],
                "Current Status": item["status"]
            }
            for item in impacts
        ])

        st.dataframe(
            impact_data,
            use_container_width=True,
            hide_index=True
        )

        # ==================================
        # IMPACT COUNTS
        # ==================================

        critical_count = sum(
            1 for item in impacts
            if item["criticality"] == "Critical"
        )

        high_count = sum(
            1 for item in impacts
            if item["criticality"] == "High"
        )

        medium_count = sum(
            1 for item in impacts
            if item["criticality"] == "Medium"
        )

        st.metric(
            "Critical Downstream Assets",
            critical_count
        )

        # ==================================
        # INCIDENT INTELLIGENCE
        # ==================================

        st.divider()

        st.subheader(
            "🧠 NEXORA Incident Intelligence"
        )

        impact_score = min(
            100,
            critical_count * 40
            + high_count * 20
            + medium_count * 10
        )

        if critical_count >= 2 or impact_score >= 80:
            severity = "CRITICAL"

        elif critical_count >= 1 or impact_score >= 50:
            severity = "HIGH"

        elif impact_score >= 20:
            severity = "MODERATE"

        else:
            severity = "LOW"

        # ==================================
        # INCIDENT METRICS
        # ==================================

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Impact Score",
            f"{impact_score}/100"
        )

        col2.metric(
            "Incident Severity",
            severity
        )

        col3.metric(
            "Affected Assets",
            len(impacts)
        )

        # ==================================
        # INCIDENT SUMMARY
        # ==================================

        st.markdown("#### Incident Summary")

        st.write(
            f"A simulated failure of **{selected_asset}** "
            f"may affect {len(impacts)} downstream assets. "
            f"The modeled dependencies include "
            f"{critical_count} critical, "
            f"{high_count} high, and "
            f"{medium_count} medium-criticality assets."
        )

        # ==================================
        # DEPENDENCY PATH TRACING
        # ==================================

        st.divider()

        st.subheader("🧭 Dependency Path Tracing")

        st.write(
            "Trace how a simulated failure propagates "
            "through connected infrastructure assets."
        )

        paths = load_dependency_paths(selected_asset)

        if paths:

            st.success(
                f"Relate identified {len(paths)} dependency path(s)."
            )

            for index, path in enumerate(paths, 1):

                nodes = path["nodes"]
                rels = path["relationships"]

                destination = nodes[-1]["name"]

                with st.expander(
                    f"Path {index}: {selected_asset} → {destination}",
                    expanded=(index == 1)
                ):

                    for node_index, node in enumerate(nodes):

                        st.markdown(
                            f"**{node_index + 1}. {node['name']}**"
                        )

                        st.caption(
                            f"Type: {', '.join(node['type'])} | "
                            f"Criticality: {node['criticality']} | "
                            f"Status: {node['status']}"
                        )

                        if node_index < len(rels):

                            st.markdown(
                                f"↓ `{rels[node_index]}`"
                            )

        else:

            st.info(
                "No downstream dependency paths were found."
            )

        st.caption(
            "Paths are retrieved from the Relate graph database. "
            "They represent modeled dependencies, not verified "
            "real-world outage propagation."
        )

        # ==================================
        # RECOMMENDED ACTIONS
        # ==================================

        st.divider()

        st.markdown(
            "#### Recommended Investigation Steps"
        )

        recommendations = [
            "Verify the condition and availability of the failed asset.",
            "Inspect upstream power, network, and equipment dependencies.",
            "Prioritize downstream assets marked Critical or High.",
            "Check affected business services and their dependencies.",
            "Validate actual impact before declaring an outage."
        ]

        for recommendation in recommendations:

            st.markdown(
                f"- {recommendation}"
            )

        st.caption(
            "Severity and impact score are prototype heuristics "
            "based on modeled asset criticality and graph connections. "
            "They are not measured outage probabilities."
        )

    else:

        st.success(
            "No downstream dependencies were found."
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "NEXORA prototype | Powered by Relate | "
    "Impact results are based on modeled dependencies, "
    "not live monitoring."
)
