from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models import ProcessedAgentData, ProcessedAgentDataInDB
from db import engine, processed_agent_data
from typing import List, Set
import json


# FastAPI app setup
app = FastAPI()

# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()

# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))


# FastAPI CRUDL endpoints
@app.post("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    conn = engine.connect()
    return_data = []
    for item in data:
        stmt = processed_agent_data.insert().values(
            road_state=item.road_state,
            x=item.agent_data.accelerometer.x,
            y=item.agent_data.accelerometer.y,
            z=item.agent_data.accelerometer.z,
            latitude=item.agent_data.gps.latitude,
            longitude=item.agent_data.gps.longitude,
            timestamp=item.agent_data.timestamp
        )
        result = conn.execute(stmt)
        conn.commit()
        returned_id = result.inserted_primary_key[0]
        returned_item = ProcessedAgentDataInDB(
            id=returned_id,
            road_state=item.road_state,
            x=item.agent_data.accelerometer.x,
            y=item.agent_data.accelerometer.y,
            z=item.agent_data.accelerometer.z,
            latitude=item.agent_data.gps.latitude,
            longitude=item.agent_data.gps.longitude,
            timestamp=item.agent_data.timestamp
        )
        return_data.append(returned_item)
        await send_data_to_subscribers(returned_item.model_dump())
    conn.close()
    return return_data


@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    conn = engine.connect()
    stmt = processed_agent_data.select()
    result = conn.execute(stmt)

    return_data = []
    for item in result:
        return_data.append(ProcessedAgentDataInDB(
            id=item.id,
            road_state=item.road_state,
            x=item.x,
            y=item.y,
            z=item.z,
            latitude=item.latitude,
            longitude=item.longitude,
            timestamp=item.timestamp
        ))
    conn.close()

    return return_data


@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    conn = engine.connect()
    stmt = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
    result = conn.execute(stmt)
    item = result.first()
    return_data = ProcessedAgentDataInDB(
        id=item.id,
        road_state=item.road_state,
        x=item.x,
        y=item.y,
        z=item.z,
        latitude=item.latitude,
        longitude=item.longitude,
        timestamp=item.timestamp
    )
    conn.close()
    return return_data


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    conn = engine.connect()
    stmt = processed_agent_data.update().where(processed_agent_data.c.id == processed_agent_data_id).values(
        road_state=data.road_state,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=data.agent_data.timestamp
    )
    result = conn.execute(stmt)
    conn.commit()
    conn.close()
    return_data = ProcessedAgentDataInDB(
        id=processed_agent_data_id,
        road_state=data.road_state,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=data.agent_data.timestamp
    )
    return return_data


@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
    conn = engine.connect()
    return_data = read_processed_agent_data(processed_agent_data_id)
    stmt = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
    result = conn.execute(stmt)
    conn.commit()
    conn.close()
    return return_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
