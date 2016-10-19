import multiprocessing
from sanic import Sanic
from sanic.log import log
from sanic.response import json, text
from sanic.exceptions import ServerError
import aioredis
from random import randint

app = Sanic(__name__)
app.engines = {}


@app.route("/json")
async def json_request(request):
    """Test type 1: JSON serialization"""
    return json({'message': 'Hello, World!'})


@app.route("/redis/db")
async def json_request(request):
    """Test type 2: Single database query"""
    idx = randint(1, 10000)
    with (await app.engines['redis']) as redis:
        random_number = await redis.get('world:%i' % idx)
    return json({'Id': idx, 'RandomNumber': random_number})


@app.route("/plaintext")
async def plaintext(request):
    """Test type 6: Plaintext"""
    return text("Hello, World!")


async def after_start(loop):
    app.engines['redis'] = await aioredis.create_pool(('127.0.0.1', 6379),
                                                      minsize=40,
                                                      maxsize=40,
                                                      encoding='utf-8',
                                                      loop=loop)

async def before_stop(loop):
    await app.engines['redis'].clear()


app.run(host="0.0.0.0", port=8000, debug=True, after_start=after_start, before_stop=before_stop, workers=multiprocessing.cpu_count())
