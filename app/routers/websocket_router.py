from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from plotly import data
from app.services.alert_engine import evaluate_alert

from app.websocket.connection_manager import manager
from app.services.streaming_service import generate_sensor_data

router = APIRouter()


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            data = generate_sensor_data()
            alert = evaluate_alert(data)
            payload = {
                "sensor_data": data,
                "alert": alert
            }
            await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(websocket)