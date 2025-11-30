# coding: utf-8

import pytest
import json
from aiohttp import web

from boidsapi.BoidsApi.boid_telemetry_event import BoidTelemetryEvent
from boidsapi.BoidsApi.session_configuration_status import SessionConfigurationStatus
from boidsapi.BoidsApi.session_timestamp import SessionTimestamp
from boidsapi.BoidsApi.system_event import SystemEvent


pytestmark = pytest.mark.asyncio

async def test_pubsub_boids_boids_get(client):
    """Test case for pubsub_boids_boids_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/pubsub/boids.boids',
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_pubsub_boids_system_events_get(client):
    """Test case for pubsub_boids_system_events_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/pubsub/boids.system-events',
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_pubsub_boids_system_time_get(client):
    """Test case for pubsub_boids_system_time_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/pubsub/boids.system-time',
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_pubsub_sessions_get(client):
    """Test case for pubsub_sessions_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/pubsub/sessions',
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

