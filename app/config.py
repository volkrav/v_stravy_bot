from typing import List
from dataclasses import dataclass
from environs import Env


# щоб не використовувати __init__.py. Дослідити
@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    use_redis: bool
    bot_url: str


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class Miscellaneous:
    other_params: str = None

@dataclass
class Categories:
    categories: List[str]



@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    cat_list: Categories


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMINS'))),
            use_redis=env.bool('USE_REDIS'),
            bot_url=env.str('BOT_URL')
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        misc=Miscellaneous(),
        cat_list=Categories(list(map(str, env.list('CATEGORIES_LIST'))))
    )
