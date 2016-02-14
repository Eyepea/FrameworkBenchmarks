from random import randint
from operator import itemgetter


async def get_random_record(container):
    pg = await container.engines['pg']

    with (await pg.cursor()) as cur:
        await cur.execute('SELECT id AS "Id", randomnumber AS "RandomNumber" FROM world WHERE id=%(idx)s LIMIT 1',
                          {'idx': randint(1, 10000)})
        world = await cur.fetchone()
    return world


async def get_random_records(container, limit):
    pg = await container.engines['pg']
    results = []
    with (await pg.cursor()) as cur:
        for i in range(limit):
            await cur.execute('SELECT id AS "Id", randomnumber AS "RandomNumber" FROM world WHERE id=%(idx)s LIMIT 1',
                              {'idx': randint(1, 10000)})
            results.append((await cur.fetchone()))

    return results


async def update_random_records(container, limit):
    results = []
    pg = await container.engines['pg']

    with (await pg.cursor()) as cur:
        for i in range(limit):
            await cur.execute('SELECT id AS "Id", randomnumber AS "RandomNumber" FROM world WHERE id=%(idx)s LIMIT 1',
                              {'idx': randint(1, 10000)})
            world = await cur.fetchone()
            await cur.execute('UPDATE world SET randomnumber=%(random_number)s WHERE id=%(idx)s',
                              {'random_number': randint(1, 10000), 'idx': world['Id']})
            results.append(world)
    return results


async def get_fortunes(container):
    pg = await container.engines['pg']

    with (await pg.cursor()) as cur:
        await cur.execute('SELECT * FROM fortune')
        fortunes = await cur.fetchall()

    fortunes.append({'id': 0, 'message': 'Additional fortune added at request time.'})

    fortunes.sort(key=itemgetter('message'))

    return fortunes
