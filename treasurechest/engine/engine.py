# -*- coding: utf-8 -*-
import logging
import json
import os
import re

import tqdm
from box import Box
from treasurechest.utils.timing import timing
from treasurechest.source.imports import FacebookPost, FacebookAlbum, InstagramPost


class Engine:

    config = None  # type: Box
    log = None

    def __init__(self, config: Box):
        if not os.path.isdir(config.site_dir):
            raise NotADirectoryError(
                f"Could not find site directory at {config.site_dir}"
            )
        else:
            self.config = config
            self.log = logging.getLogger(__name__)

    @timing
    def import_facebook_posts(self):
        cfg = self.config
        self.log.info(f"Starting import of Facebook data to site in {cfg.site_dir}")
        fb_file = os.path.join(cfg.facebook_export_dir, "posts/your_posts_1.json")
        if os.path.isfile(fb_file):
            with open(fb_file) as f:
                posts_dict = json.load(f)
                total_posts = len(posts_dict)
                self.log.info(
                    f"Importing {total_posts} posts from Facebook file located in {cfg.facebook_export_dir}"
                )
                n = 1
                skipped = 0
                for p in tqdm.tqdm(posts_dict):
                    obj = FacebookPost(cfg)
                    obj.get_post(p)
                    obj.get_tags(p)
                    if obj.date:
                        obj.update_site(n)
                    else:
                        skipped += 1
                    n += 1
                self.log.info(f"Total skipped: {skipped}")
        else:
            raise FileExistsError(f"Could not find Facebook posts file at {fb_file}")

    @timing
    def import_facebook_albums(self):
        cfg = self.config
        album_dir = os.path.join(cfg.facebook_export_dir, "posts/album")
        albums_exist = os.path.isdir(album_dir)
        if albums_exist:
            self.log.info(
                f"Starting import of Facebook albums to site in {cfg.site_dir}"
            )
            album_pattern = re.compile("[0-9]+.json")
            albums = [x for x in os.listdir(album_dir) if album_pattern.match(x)]
            total_albums = len(albums)
            self.log.info(
                f"Importing {total_albums} albums from Facebook file located in {album_dir}"
            )
            n = 1
            for a in tqdm.tqdm(albums):
                with open(os.path.join(album_dir, a)) as f:
                    album_dict = json.load(f)
                    obj = FacebookAlbum(cfg)
                    obj.get_post(album_dict)
                    if len(obj.media) > 0:
                        obj.update_site(n)
                    n += 1
        else:
            raise NotADirectoryError(
                f"Could not find Facebook album directory at {album_dir}"
            )

    @timing
    def import_instagram_posts(self):
        cfg = self.config
        self.log.info(
            f"Starting import of Instagram data to site in {self.config.site_dir}"
        )
        insta_file = os.path.join(cfg.instagram_export_dir, "content/posts_1.json")
        if os.path.isfile(insta_file):
            with open(insta_file) as f:
                posts_dict = json.load(f)
                total_posts = len(posts_dict)
                self.log.info(
                    f"Importing {total_posts} posts from Instagram file located in {self.config.instagram_export_dir}"
                )
                n = 1
                for p in tqdm.tqdm(posts_dict):
                    obj = InstagramPost(cfg)
                    obj.get_post(p)
                    obj.update_site(n)
                    n += 1
        else:
            raise FileExistsError(f"Could not find Instagram file at {insta_file}")
