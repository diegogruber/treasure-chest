# -*- coding: utf-8 -*-
from logging.config import dictConfig
import click
from treasurechest.utils.config import Config
from treasurechest.engine.engine import Engine


@click.group()
@click.version_option(version="0.1.12")
def main():
    pass


@main.command()
@click.option('--imports', default="posts albums")
@click.option('--config', default="config/main.yml")
def import_from_facebook(config: str, imports: str):
    """Some help text for full pipeline run goes here"""
    # init the config from config/
    config = Config(config).read()
    imports = imports.split()
    # init logging package
    dictConfig(config.logging)
    engine = Engine(config)
    if 'posts' in imports:
        engine.import_facebook_posts()
    if 'albums' in imports:
        engine.import_facebook_albums()


@main.command()
@click.option('--config', default="config/main.yml")
def import_from_instagram(config: str):
    """Some help text for side analysis goes here"""
    # init the config from config/
    config = Config(config).read()
    # init logging package
    dictConfig(config.logging)
    engine = Engine(config)
    engine.import_instagram_posts()


if __name__ == "__main__":
    main()
