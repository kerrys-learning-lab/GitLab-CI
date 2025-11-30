from typing import List, Dict
from aiohttp import web

from boidsapi.BoidsApi.boid import Boid
from boidsapi.BoidsApi.boid_list import BoidList
from boidsapi.BoidsApi.error_model import ErrorModel
from boidsapi.BoidsApi.session_configuration import SessionConfiguration
from boidsapi.BoidsApi.session_configuration_status import SessionConfigurationStatus
from boidsapi.BoidsApi.session_configuration_status_list import SessionConfigurationStatusList
from boidsapi import util


async def session_get(request: web.Request, title=None, state=None, uuid=None, order_by=None, offset=None, limit=None) -> web.Response:
    """session_get

    Retrieve the list of Boids sessions

    :param title: Filter SessionConfigurations by title.
    :type title: str
    :param state: Filter SessionConfigurations by state.
    :type state: str
    :param uuid: 
    :type uuid: str
    :type uuid: str
    :param order_by: Field name to sort by.  Defaults to ascending. For descending, prepend a &#39;-&#39; minus.  Examples: &#39;title&#39; (sorts by title ascending), &#39;-title&#39; sorts by title descending) 
    :type order_by: str
    :param offset: Pagination offset (0-based)
    :type offset: int
    :param limit: Pagination size
    :type limit: int

    """
    return web.Response(status=200)


async def session_post(request: web.Request, body=None) -> web.Response:
    """session_post

    Create a Boids session. Required fields: title 

    :param body: 
    :type body: dict | bytes

    """
    body = SessionConfiguration.from_dict(body)
    return web.Response(status=200)


async def session_session_uuid_boid_boid_uuid_delete(request: web.Request, session_uuid, boid_uuid) -> web.Response:
    """session_session_uuid_boid_boid_uuid_delete

    

    :param session_uuid: 
    :type session_uuid: str
    :type session_uuid: str
    :param boid_uuid: 
    :type boid_uuid: str
    :type boid_uuid: str

    """
    return web.Response(status=200)


async def session_session_uuid_boid_boid_uuid_get(request: web.Request, session_uuid, boid_uuid) -> web.Response:
    """session_session_uuid_boid_boid_uuid_get

    

    :param session_uuid: 
    :type session_uuid: str
    :type session_uuid: str
    :param boid_uuid: 
    :type boid_uuid: str
    :type boid_uuid: str

    """
    return web.Response(status=200)


async def session_uuid_boid_get(request: web.Request, uuid, order_by=None, offset=None, limit=None) -> web.Response:
    """session_uuid_boid_get

    Return the list of Boids

    :param uuid: 
    :type uuid: str
    :type uuid: str
    :param order_by: Field name to sort by.  Defaults to ascending. For descending, prepend a &#39;-&#39; minus.  Examples: &#39;title&#39; (sorts by title ascending), &#39;-title&#39; sorts by title descending) 
    :type order_by: str
    :param offset: Pagination offset (0-based)
    :type offset: int
    :param limit: Pagination size
    :type limit: int

    """
    return web.Response(status=200)


async def session_uuid_boid_post(request: web.Request, uuid, body=None) -> web.Response:
    """session_uuid_boid_post

    Create a Boid.  The &#39;id&#39; and &#39;timestamp&#39; fields must not be present. The newly created Boid is assigned an ID by the simulation. 

    :param uuid: 
    :type uuid: str
    :type uuid: str
    :param body: 
    :type body: dict | bytes

    """
    body = Boid.from_dict(body)
    return web.Response(status=200)


async def session_uuid_delete(request: web.Request, uuid) -> web.Response:
    """session_uuid_delete

    

    :param uuid: 
    :type uuid: str
    :type uuid: str

    """
    return web.Response(status=200)


async def session_uuid_get(request: web.Request, uuid) -> web.Response:
    """session_uuid_get

    Retrieve the specified session

    :param uuid: 
    :type uuid: str
    :type uuid: str

    """
    return web.Response(status=200)


async def session_uuid_put(request: web.Request, uuid, body=None) -> web.Response:
    """session_uuid_put

    

    :param uuid: 
    :type uuid: str
    :type uuid: str
    :param body: 
    :type body: dict | bytes

    """
    body = SessionConfiguration.from_dict(body)
    return web.Response(status=200)
