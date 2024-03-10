import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        # Convert the processed road data to a dictionary.
        processed_agent_data_batch_dict = pydantic_core.parse_obj_as(
            List[dict], processed_agent_data_batch
        )

        # Send a POST request to the Store API to save the processed road data.
        response = requests.post(
            f"{self.api_base_url}/processed-agent-data",
            json=processed_agent_data_batch_dict,
        )

        if response.status_code in [200, 201]:
            logging.info(
                f"Successfully saved {len(processed_agent_data_batch)} processed agent data."
            )
            return True
        else:
            logging.error(
                f"Failed to save processed agent data. Status code: {response.status_code}."
            )
            return False
