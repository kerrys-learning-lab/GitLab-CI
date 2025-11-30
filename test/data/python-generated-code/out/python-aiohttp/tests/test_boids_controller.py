# coding: utf-8

import pytest
import json
from aiohttp import web

from boidsapi.BoidsApi.boid import Boid
from boidsapi.BoidsApi.boid_list import BoidList
from boidsapi.BoidsApi.error_model import ErrorModel


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

