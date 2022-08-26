from typing import Dict, List, Tuple
from app.models.DBcm import UseDataBase


async def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ', '.join(columns)
    async with UseDataBase() as cursor:
        cursor.execute(
            f'SELECT {columns_joined} FROM {table}'
        )
        rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


async def load_categories() -> List[Dict]:
    return await fetchall('categories', ['partuid', 'name', 'alias'])

async def load_products() -> List[Dict]:
    return await fetchall('products',
    [
        'uid', 'title', 'price', 'descr',
        'text', 'img', 'quantity', 'gallery',
        'url', 'partuids'
    ])
