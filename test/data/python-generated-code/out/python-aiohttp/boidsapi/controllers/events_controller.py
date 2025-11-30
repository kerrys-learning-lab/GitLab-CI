from typing import List, Dict
from aiohttp import web

from boidsapi.BoidsApi.system_event_list import SystemEventList
from boidsapi import util


async def session_uuid_event_get(request: web.Request, uuid, order_by=None, offset=None, limit=None) -> web.Response:
    """session_uuid_event_get

    Retrieve system events in descending time order (most recent first)

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
