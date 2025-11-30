# coding: utf-8

import pytest
import json
from aiohttp import web

from boidsapi.BoidsApi.boid import Boid
from boidsapi.BoidsApi.boid_list import BoidList
from boidsapi.BoidsApi.error_model import ErrorModel
from boidsapi.BoidsApi.session_configuration import SessionConfiguration
from boidsapi.BoidsApi.session_configuration_status import SessionConfigurationStatus
from boidsapi.BoidsApi.session_configuration_status_list import SessionConfigurationStatusList


pytestmark = pytest.mark.asyncio

async def test_session_get(client):
    """Test case for session_get

    
    """
    params = [('title', 'title_example'),
                    ('state', 'state_example'),
                    ('uuid', 'uuid_example'),
                    ('order_by', 'order_by_example'),
                    ('offset', 0),
                    ('limit', 20)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/session',
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_post(client):
    """Test case for session_post

    
    """
    body = {"world":{"width":6,"height":1},"state":"PENDING","title":"title","behavior":{"avoid_walls":True,"speed_limits":{"min":2,"max":7},"view_angle":202,"normalize_velocity":True,"view_range":5},"num_boids":0}
    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = await client.request(
        method='POST',
        path='/api/v1/session',
        headers=headers,
        json=body,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_session_uuid_boid_boid_uuid_delete(client):
    """Test case for session_session_uuid_boid_boid_uuid_delete

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='DELETE',
        path='/api/v1/session/{session_uuid}/boid/{boid_uuid}'.format(session_uuid='session_uuid_example', boid_uuid='boid_uuid_example'),
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_session_uuid_boid_boid_uuid_get(client):
    """Test case for session_session_uuid_boid_boid_uuid_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/session/{session_uuid}/boid/{boid_uuid}'.format(session_uuid='session_uuid_example', boid_uuid='boid_uuid_example'),
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_uuid_boid_get(client):
    """Test case for session_uuid_boid_get

    
    """
    params = [('order_by', 'order_by_example'),
                    ('offset', 0),
                    ('limit', 20)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/session/{uuid}/boid'.format(uuid='uuid_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_uuid_boid_post(client):
    """Test case for session_uuid_boid_post

    
    """
    body = {"position":{"x":1.4658129805029452,"y":5.962133916683182,"z":5.637376656633329},"velocity":{"x":1.4658129805029452,"y":5.962133916683182,"z":5.637376656633329},"uuid":"046b6c7f-0b8a-43b9-b35d-6489e6daee91","url":"https://openapi-generator.tech"}
    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = await client.request(
        method='POST',
        path='/api/v1/session/{uuid}/boid'.format(uuid='uuid_example'),
        headers=headers,
        json=body,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_uuid_delete(client):
    """Test case for session_uuid_delete

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='DELETE',
        path='/api/v1/session/{uuid}'.format(uuid='uuid_example'),
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_uuid_get(client):
    """Test case for session_uuid_get

    
    """
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/session/{uuid}'.format(uuid='uuid_example'),
        headers=headers,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')


pytestmark = pytest.mark.asyncio

async def test_session_uuid_put(client):
    """Test case for session_uuid_put

    
    """
    body = {"world":{"width":6,"height":1},"state":"PENDING","title":"title","behavior":{"avoid_walls":True,"speed_limits":{"min":2,"max":7},"view_angle":202,"normalize_velocity":True,"view_range":5},"num_boids":0}
    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = await client.request(
        method='PUT',
        path='/api/v1/session/{uuid}'.format(uuid='uuid_example'),
        headers=headers,
        json=body,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

