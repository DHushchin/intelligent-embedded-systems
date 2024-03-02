from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Set
import json
from models import ProcessedAgentData, ProcessedAgentDataInDB
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

# SQLAlchemy setup
DATABASE_URL =f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)

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
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    # Convert ProcessedAgentData objects to dictionaries
    data_dicts = [row.dict() for row in data]

    # Insert data to database
    conn = engine.connect()
    conn.execute(processed_agent_data.insert(), data_dicts)
    conn.close()

    # Send data to subscribers
    await send_data_to_subscribers(data_dicts)

    return {"message": "Data inserted successfully"}


@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int):
    # Get data by id
    conn = engine.connect()
    query = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
    result = conn.execute(query)
    data = result.fetchone()
    conn.close()
    return data


@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    # Get list of data
    conn = engine.connect()
    query = processed_agent_data.select()
    result = conn.execute(query)
    data = result.fetchall()
    conn.close()
    return data


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    # Convert ProcessedAgentData object to dictionary
    data_dict = data.dict(exclude_unset=True)

    # Update data
    conn = engine.connect()
    query = (
        processed_agent_data.update()
        .where(processed_agent_data.c.id == processed_agent_data_id)
        .values(**data_dict)
    )
    conn.execute(query)
    conn.close()
    return {"message": "Data updated successfully"}


@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int):
    # Delete by id
    conn = engine.connect()
    query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
    conn.execute(query)
    conn.close()
    return {"message": "Data deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
