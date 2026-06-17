import random
import time

ASSETS = [
    {
        "id": "bridge_1",
        "name": "City Bridge A"
    },
    {
        "id": "bridge_2",
        "name": "River Bridge B"
    },
    {
        "id": "building_1",
        "name": "Tower Alpha"
    }
]


def generate_sensor_data():

    asset = random.choice(ASSETS)

    vibration = round(random.uniform(0.2, 1.0), 2)
    stress = round(random.uniform(0.2, 1.0), 2)
    temperature = round(random.uniform(25, 45), 2)

    risk_score = int(
        vibration * 40 +
        stress * 30 +
        (temperature / 50) * 30
    )

    status = "healthy"

    if risk_score > 70:
        status = "critical"
    elif risk_score > 40:
        status = "warning"

    return {
        "asset_id": asset["id"],
        "asset_name": asset["name"],
        "timestamp": int(time.time()),
        "metrics": {
            "vibration": vibration,
            "stress": stress,
            "temperature": temperature
        },
        "risk_score": risk_score,
        "status": status
    }