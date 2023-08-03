from asyncpg import Pool


async def create_game_acc(pool: Pool, uid):
    async with pool.acquire() as con:
        pass


def conv_sum(x):
    return '{:,.2f}'.format(x).replace(',', '.')
