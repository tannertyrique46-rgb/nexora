
import relate

DATABASE = "./data/nexora.rl"

GRAPH = """
CREATE
  (b:Building:Asset {
    name: 'NEXORA Main Building',
    status: 'Operational',
    criticality: 'Critical'
  }),
  (p:ElectricalPanel:Asset {
    name: 'Main Electrical Panel',
    status: 'Operational',
    criticality: 'Critical'
  }),
  (u:UPS:Asset {
    name: 'UPS Backup Unit',
    status: 'Operational',
    criticality: 'High'
  }),
  (s:NetworkSwitch:Asset {
    name: 'Core Network Switch',
    status: 'Operational',
    criticality: 'Critical'
  }),
  (a:AccessPoint:Asset {
    name: 'Office Wi-Fi Access Point',
    status: 'Operational',
    criticality: 'Medium'
  }),
  (srv:Server:Asset {
    name: 'Application Server',
    status: 'Operational',
    criticality: 'High'
  }),
  (svc:BusinessService:Asset {
    name: 'Business Application',
    status: 'Operational',
    criticality: 'Critical'
  }),

  (b)-[:CONTAINS]->(p),
  (p)-[:POWERS]->(u),
  (u)-[:POWERS]->(s),
  (s)-[:CONNECTS_TO]->(a),
  (s)-[:CONNECTS_TO]->(srv),
  (srv)-[:HOSTS]->(svc)
"""

with relate.connect(DATABASE) as conn:
    existing = conn.execute(
        "MATCH (n:Asset) RETURN count(n) AS total"
    ).single()["total"]

    if existing == 0:
        conn.execute(GRAPH)
        print("NEXORA infrastructure graph created!")
    else:
        print("Infrastructure graph already exists.")

    nodes = conn.execute(
        "MATCH (n:Asset) RETURN count(n) AS total"
    ).single()["total"]

    relationships = conn.execute(
        "MATCH ()-[r]->() RETURN count(r) AS total"
    ).single()["total"]

    print("Total assets:", nodes)
    print("Total relationships:", relationships)
