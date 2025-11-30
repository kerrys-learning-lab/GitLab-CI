from typing import List, Dict
from aiohttp import web

from boidsapi.BoidsApi.boid_telemetry_event import BoidTelemetryEvent
from boidsapi.BoidsApi.session_configuration_status import SessionConfigurationStatus
from boidsapi.BoidsApi.session_timestamp import SessionTimestamp
from boidsapi.BoidsApi.system_event import SystemEvent
from boidsapi import util


async def pubsub_boids_boids_get(request: web.Request, ) -> web.Response:
    """pubsub_boids_boids_get

    


    """
    return web.Response(status=200)


async def pubsub_boids_system_events_get(request: web.Request, ) -> web.Response:
    """pubsub_boids_system_events_get

    


    """
    return web.Response(status=200)


async def pubsub_boids_system_time_get(request: web.Request, ) -> web.Response:
    """pubsub_boids_system_time_get

    


    """
    return web.Response(status=200)


async def pubsub_sessions_get(request: web.Request, ) -> web.Response:
    """pubsub_sessions_get

    


    """
    return web.Response(status=200)
