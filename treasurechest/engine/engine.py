# -*- coding: utf-8 -*-
import logging
import json
import os
import re

from box import Box
from treasurechest.utils.timing import timing
from treasurechest.source.imports import FacebookPost, FacebookAlbum, InstagramPost


class Engine:

    config = None  # type: Box
    log = None

    def __init__(self, config: Box):
        self.config = config
        self.log = logging.getLogger(__name__)

    @timing
    def import_facebook_posts(self):
        cfg = self.config
        self.log.info(f"Starting import of Facebook data to blog in {self.config.blog_dir}")
        with open(os.path.join(cfg.facebook_export_dir, 'posts/your_posts_1.json')) as f:
            posts_dict = json.load(f)
            total_posts = len(posts_dict)
            self.log.info(f"Importing {total_posts} from Instagram file located in {self.config.instagram_export_dir}")
            n = 1
            skipped = 0
            for p in posts_dict:
                self.log.info(f"Importing post {n} of {total_posts}...")
                obj = FacebookPost(cfg)
                if 'attachments' in p and len(p['attachments']) > 0:
                    obj.get_attachment(p)
                elif 'data' in p:
                    obj.get_data(p)
                obj.get_tags(p)
                if obj.date:
                    obj.update_blog(n)
                else:
                    self.log.info("Skipped (no data)")
                    skipped += 1
                n += 1
            self.log.info(f"Total skipped: {skipped}")

    @timing
    def import_facebook_albums(self):
        cfg = self.config
        album_dir = os.path.join(cfg.facebook_export_dir, 'posts/album')
        albums_exist = os.path.isdir(album_dir)
        if albums_exist:
            self.log.info(f"Starting import of Facebook albums to blog in {cfg.blog_dir}")
            album_pattern = re.compile("[0-9]+.json")
            albums = [x for x in os.listdir(album_dir) if album_pattern.match(x)]
            total_albums = len(albums)
            self.log.info(f"Importing {total_albums} albums from Facebook file located in {album_dir}")
            n = 1
            for a in albums:
                with open(os.path.join(album_dir, a)) as f:
                    album_dict = json.load(f)
                    self.log.info(f"Importing album {n} of {total_albums}...")
                    obj = FacebookAlbum(cfg)
                    obj.get_album(album_dict)
                    if len(obj.media) > 0:
                        obj.update_blog(n)
                    else:
                        self.log.info("No media found for this album")
                    n += 1

    @timing
    def import_instagram_posts(self):
        cfg = self.config
        self.log.info(f"Starting import of Instagram data to blog in {self.config.blog_dir}")
        with open(os.path.join(cfg.instagram_export_dir, 'content/posts_1.json')) as f:
            posts_dict = json.load(f)
            total_posts = len(posts_dict)
            self.log.info(f"Importing {total_posts} from Instagram file located in {self.config.instagram_export_dir}")
            n = 1
            for p in posts_dict:
                self.log.info(f"Importing post {n} of {total_posts}...")
                obj = InstagramPost(cfg)
                obj.get_post(p)
                obj.update_blog(n)
                n += 1
