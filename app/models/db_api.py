from typing import Dict, List, Tuple, Union
from app.models.DBcm import UseDataBase


async def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = tuple(column_values.values())
    placeholders = ', '.join('?' * len(column_values.keys()))
    try:
        async with UseDataBase() as cursor:
            cursor.execute(
                f'INSERT INTO {table} '
                f'({columns}) '
                f'VALUES ({placeholders}) ',
                values
            )
    except Exception as err:
        print(err.args)


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


async def select_where_and(table: str, columns: List[str], definitions: Dict) -> List[Tuple]:
    columns_joined = ', '.join(columns)
    definition_joined_placeholders = ' AND '.join(
        [f'{field}=?' for field in definitions.keys()])
    values = tuple(definitions.values())

    async with UseDataBase() as cursor:
        cursor.execute(
            f'SELECT {columns_joined} '
            f'FROM {table} '
            f'WHERE {definition_joined_placeholders}',
            values
        )
        rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


async def delete_from_where(table: str, definitions: Dict) -> None:
    definition_joined_placeholders = ' AND '.join(
        [f'{field}=?' for field in definitions.keys()])
    values = tuple(definitions.values())
    async with UseDataBase() as cursor:
        cursor.execute(
            f'DELETE '
            f'FROM {table} '
            f'WHERE {definition_joined_placeholders}',
            values
        )


async def load_all_categories() -> List[Dict]:
    return await fetchall('categories', ['partuid', 'name', 'alias'])


async def load_products(columns: List[str]) -> List[Dict]:
    return await fetchall('products',
                          columns)


async def load_product(uid: str, columns: Union[str, List[str]]) -> Dict:
    if isinstance(columns, str):
        columns_joined = columns
    elif isinstance(columns, List):
        columns_joined = ', '.join(columns)
    async with UseDataBase() as cursor:
        cursor.execute(
            f'SELECT {columns_joined} '
            f'FROM "products" '
            f'WHERE "uid" = ?',
            (uid, )
        )
        row = cursor.fetchone()
    result = []
    dict_row = {}
    for index, column in enumerate(columns):
        dict_row[column] = row[index]
    result.append(dict_row)
    return dict_row


async def load_user(user_id: int, columns: Union[str, List[str]]) -> Dict:
    if isinstance(columns, str):
        columns_joined = columns
    elif isinstance(columns, List):
        columns_joined = ', '.join(columns)
    async with UseDataBase() as cursor:
        cursor.execute(
            f'SELECT {columns_joined} '
            f'FROM "users" '
            f'WHERE "id" = ?',
            (user_id, )
        )
        row = cursor.fetchone()
    result = []
    dict_row = {}
    for index, column in enumerate(columns):
        dict_row[column] = row[index]
    result.append(dict_row)
    return dict_row


async def update_set_where(table: str, columns: Dict, definitions: Dict) -> None:
    columns_joined_with_placeholders = ','.join(
        f'{field}=?' for field in columns.keys())
    columns_value = tuple([_col for _col in columns.values()] +
                          [_def for _def in definitions.values()])
    definitions_joined_with_placeholders = ' AND '.join(
        f'{field}=?' for field in definitions.keys())

    async with UseDataBase() as cursor:
        cursor.execute(
            f'UPDATE {table} '
            f'SET {columns_joined_with_placeholders} '
            f'WHERE {definitions_joined_with_placeholders}',
            columns_value
        )
