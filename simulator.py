
import relate

DATABASE = "./data/nexora.rl"


def simulate_failure(asset_name):
    with relate.connect(DATABASE) as db:
        result = db.execute(
            """
            MATCH (source:Asset {name: $asset_name})
            MATCH (source)-[*1..]->(affected:Asset)
            RETURN DISTINCT
                affected.name AS asset,
                labels(affected) AS asset_type,
                affected.criticality AS criticality,
                affected.status AS status
            """,
            {"asset_name": asset_name}
        ).data()

    return result


if __name__ == "__main__":
    target = "Core Network Switch"

    print("\nNEXORA — WHAT-IF IMPACT SIMULATOR")
    print("=" * 40)
    print("Simulating failure:", target)
    print("-" * 40)

    impacts = simulate_failure(target)

    if impacts:
        for item in impacts:
            print("Affected asset:", item["asset"])
            print("Type:", item["asset_type"])
            print("Criticality:", item["criticality"])
            print("-" * 30)
    else:
        print("No downstream impacts found.")
