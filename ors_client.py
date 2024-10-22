# Encapsulates the ORS client functionality.
# Follows Single Responsibility principle
import os
import openrouteservice

class ORSClient:
    def __init__(self):
        ORS_API_KEY = os.getenv('ors')
        if not ORS_API_KEY:
            raise ValueError("OpenRouteService API key not found. Please set the 'ors' environment variable.")
        self.client = openrouteservice.Client(key=ORS_API_KEY)

    def get_isochrone(self, coords):
        try:
            return self.client.isochrones(locations=[coords], profile='driving-car', range=[1800])
        except openrouteservice.exceptions.HTTPError as e:
            raise Exception(f"HTTPError: {e}")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")