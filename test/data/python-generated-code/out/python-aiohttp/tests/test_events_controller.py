# coding: utf-8

import pytest
import json
from aiohttp import web

from boidsapi.BoidsApi.system_event_list import SystemEventList


pytestmark = pytest.mark.asyncio

async def test_session_uuid_event_get(client):
    """Test case for session_uuid_event_get

    
    """
    params = [('order_by', 'order_by_example'),
                    ('offset', 0),
                    ('limit', 20)]
    headers = { 
        'Accept': 'application/json',
    }
    response = await client.request(
        method='GET',
        path='/api/v1/session/{uuid}/event'.format(uuid='uuid_example'),
        headers=headers,
        params=params,
        )
    assert response.status == 200, 'Response body is : ' + (await response.read()).decode('utf-8')

