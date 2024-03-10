from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    if agent_data.accelerometer.z < 10 or agent_data.accelerometer.z > 10:
        road_surface_state = "Bumpy"
    else:
        road_surface_state = "Smooth"

    processed_data_batch = ProcessedAgentData(road_state=road_surface_state, agent_data=agent_data)
    return processed_data_batch
