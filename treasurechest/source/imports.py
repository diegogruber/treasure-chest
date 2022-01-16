import logging
import os
import re
import shutil
import ftfy

from box import Box
from treasurechest.utils.helpers import get_date_from_timestamp, mkdir_from_date, make_file_name, make_header


class FacebookPost:

    def __init__(self, config: Box):
        self.config = config
        self.log = logging.getLogger(__name__)
        self.date = ""
        self.data = ""
        self.title = ""
        self.uri = ""
        self.tags = ""
        self.loc = ""

    def update_blog(self, post_number: int):
        author = self.config.author
        default_text = 'Facebook status update'
        if self.title:
            split_title = self.title.split()
            if len(split_title) > 10:
                title = ' '.join(split_title[:10]) + "..."
                text = self.title + "\n\n" + self.data.replace(self.title, "")
            else:
                title = self.title
                text = self.data
        elif self.data:
            split_data = self.data.split()
            if len(split_data) > 10:
                title = ' '.join(split_data[:10]) + "..."
                text = self.data
            else:
                title = self.data
                text = default_text
        else:
            title = default_text
            text = ''
        title = re.sub(':', '...', title)  # colon in title causes yaml trouble
        title = re.sub('^[\'\"]', '', title)  # apostrophe at beginning of title causes yaml trouble
        if self.uri:
            src = os.path.join(self.config.facebook_export_dir, self.uri)
            dst = os.path.join(self.config.blog_dir, "static", self.uri)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            text += f"\n![img](/facebook/{self.uri})"
        if self.tags:
            tags = self.tags.replace(' ', '\n- ')
        else:
            tags = ''
        file_dir = mkdir_from_date(self)
        file_name = make_file_name("fb", post_number, title)
        if '\'' not in title:
            title = f"'{title}'"
        elif '\"' not in title:
            title = f'"{title}"'
        header = make_header(
            title=title,
            date=self.date,
            author=author,
            categories="Facebook post",
            featured_image="/facebook/{self.uri}",
            tags=tags
        )
        self.log.info(header)
        with open(os.path.join(file_dir, file_name), 'w') as post:
            post.write(header)
            post.write("\n" + text)

    def get_tags(self, post: dict):
        if 'tags' in post:
            tags = post['tags']
            tag_data = " "
            for tag in tags:
                tag_data += ftfy.fix_text(list(tag.values())[0]).replace(" ", "-") + " "
            self.tags = tag_data

    def get_attachment(self, post: dict):
        if 'data' in post:
            self.get_data(post)
            self.title = self.data
            self.data = ''
        attachments = post['attachments']
        for attachment in attachments:
            data = attachment['data'][0]
            if 'external_context' in data:
                external = data['external_context']
                if 'url' in external:
                    self.data += '\n' + external['url']
                if 'name' in external:
                    self.data += '\n' + external['name']
            if self.data and not self.title:
                self.title = 'External content posted'
                timestamp = post['timestamp']
                self.date = get_date_from_timestamp(timestamp)
            if 'media' in data:
                self.uri = data['media']['uri']
            if 'place' in data:
                self.get_location(data)

    def get_title(self, post: dict):
        if 'title' in post:
            self.title = ftfy.fix_text(post['title'])

    def get_location(self, data: dict):
        place = data['place']
        if 'coordinate' in place:
            loc = place['coordinate']
            loc_data = []
            for val in loc.values():
                r_val = round(val, 3)
                loc_data.append(str(r_val))
            self.loc = loc_data[0] + " " + loc_data[1]

    def get_data(self, post: dict):
        data = post['data']
        timestamp = post['timestamp']
        for d in data:
            if 'post' in d:
                self.date = get_date_from_timestamp(timestamp)
                self.data = ftfy.fix_text(d['post'])


class FacebookAlbum:

    def __init__(self, config: Box):
        self.config = config
        self.log = logging.getLogger(__name__)
        self.title = ""
        self.date = ""
        self.media = []

    def update_blog(self, album_number: int):
        tags = '\n- album'
        timestamp = 0
        content = []
        for f in self.media:
            media_uri = f['uri']
            if 'description' in f:
                media_title = ftfy.fix_text(f['description']) + ' '
            else:
                media_title = ''
            media_timestamp = f['creation_timestamp']
            if media_timestamp > timestamp:
                timestamp = media_timestamp
            media_date = get_date_from_timestamp(timestamp)
            src = os.path.join(self.config.facebook_export_dir, media_uri)
            dst = os.path.join(self.config.blog_dir, "static", "facebook", media_uri)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            content.append(f"{media_title}{media_date}\n![img](/facebook/{media_uri})")
        self.date = get_date_from_timestamp(timestamp)
        header = make_header(
            title=f"Album - {self.title}",
            date=self.date,
            author=self.config.author,
            categories="Facebook album",
            featured_image=f"/facebook/{self.media[0]['uri']}",
            tags=tags
        )
        self.log.info(header)
        content = '\n'+'\n\n'.join(content)
        file_dir = mkdir_from_date(self)
        file_name = make_file_name("fb-album", album_number, self.title)
        with open(os.path.join(file_dir, file_name), 'w') as post:
            post.write(header)
            post.write(content)

    def get_album(self, album: dict):
        self.title = ftfy.fix_text(album['name'])
        self.media = album['photos']


class InstagramPost:

    def __init__(self, config: Box):
        self.config = config
        self.log = logging.getLogger(__name__)
        self.date = ""
        self.title = ""
        self.media = []

    def update_blog(self, post_number: int):
        author = self.config.author
        if self.title == '':
            title = 'Posted to Instagram'
            content = []
        else:
            split_title = self.title.split()
            if len(split_title) > 10:
                title = ' '.join(split_title[:10]) + "..."
                content = [self.title]
            else:
                title = self.title
                content = []
        title = re.sub(':', '...', title)  # colon in title causes yaml trouble
        title = re.sub('^[\'\"]', '', title)  # apostrophe at beginning of title causes yaml trouble

        file_dir = mkdir_from_date(self)
        file_name = make_file_name("insta", post_number, title)

        tags = [x for x in title.split() if x.strip()[0] in ['@', '#']]

        if '\'' not in title:
            title = f"'{title}'"
        elif '\"' not in title:
            title = f'"{title}"'

        for m in self.media:
            media_uri = m['uri']
            media_title = ftfy.fix_text(m['title'])
            if 'http' not in media_uri:
                src = os.path.join(self.config.instagram_export_dir, media_uri)
                dst = os.path.join(self.config.blog_dir, "static", "instagram", media_uri)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                content.append(f"\n![img](/instagram/{media_uri})")
            else:
                content.append(f"\n![img]({media_uri})")
            if media_title != self.title:
                content.append(f"{media_title}")
                tags += [x for x in media_title.split() if (x.strip()[0] in ['@', '#'] and x not in tags)]

        content = '\n'.join(content)

        tags = list(dict.fromkeys(tags))  # remove duplicate tags
        tags = [t.replace('@', '').replace('#', '') for t in tags]
        if tags:
            tags = '\n- ' + '\n- '.join(tags)
        else:
            tags = ''
        header = make_header(
            title=title,
            date=self.date,
            author=author,
            categories="Instagram post",
            featured_image=f"/instagram/{self.media[0]['uri']}",
            tags=tags
        )
        self.log.info(header)

        with open(os.path.join(file_dir, file_name), 'w') as post:
            post.write(header)
            post.write(content)

    def get_post(self, post: dict):
        self.media = post['media']
        if 'creation_timestamp' in post:
            timestamp = post['creation_timestamp']
            self.date = get_date_from_timestamp(timestamp)
            self.title = ftfy.fix_text(post['title'])
        else:
            timestamp = self.media[0]['creation_timestamp']
            self.date = get_date_from_timestamp(timestamp)
            self.title = ftfy.fix_text(self.media[0]['title'])
