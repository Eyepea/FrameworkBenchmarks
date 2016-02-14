import logging
import asyncio

from aiohttp.web import Response
from api_hour.plugins.aiohttp import JSON
import aiohttp_jinja2

from ..services import queries_number
from ..services.world import get_random_record, get_random_records, update_random_records, get_fortunes
from ..services import redis

LOG = logging.getLogger(__name__)

async def json(request):
    """Test type 1: JSON serialization"""
    return JSON({'message': 'Hello, World!'})

async def db(request):
    """Test type 2: Single database query"""
    container = request.app.ah_container

    return JSON((await get_random_record(container)))

async def db_redis(request):
    """Test type 2: Single database query"""
    container = request.app.ah_container

    return JSON((await redis.get_random_record(container)))

async def queries(request):
    """Test type 3: Multiple database queries"""
    container = request.app.ah_container
    limit = queries_number(request.GET.get('queries', 1))

    return JSON((await get_random_records(container, limit)))

async def queries_redis(request):
    """Test type 3: Multiple database queries"""
    container = request.app.ah_container
    limit = queries_number(request.GET.get('queries', 1))

    return JSON((await redis.get_random_records(container, limit)))

async def fortunes(request):
    """Test type 4: Fortunes"""
    container = request.app.ah_container

    return aiohttp_jinja2.render_template('fortunes.html.j2',
                                          request,
                                          {'fortunes': (await get_fortunes(container))})

async def fortunes_redis(request):
    """Test type 4: Fortunes"""
    container = request.app.ah_container

    return aiohttp_jinja2.render_template('fortunes.html.j2',
                                          request,
                                          {'fortunes': (await redis.get_fortunes(container))})

async def updates(request):
    """Test type 5: Database updates"""
    container = request.app.ah_container
    limit = queries_number(request.GET.get('queries', 1))

    return JSON((await update_random_records(container, limit)))

async def updates_redis(request):
    """Test type 5: Database updates"""
    container = request.app.ah_container
    limit = queries_number(request.GET.get('queries', 1))

    return JSON((await redis.update_random_records(container, limit)))

async def plaintext(request):
    """Test type 6: Plaintext"""
    return Response(text='Hello, World!')