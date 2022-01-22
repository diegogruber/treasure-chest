import logging
import os
import re
import shutil
import ftfy
from abc import ABC, abstractmethod

from box import Box
from treasurechest.utils.helpers import get_date_from_timestamp


class Post(ABC):
    """
    Base class for site post
    """

    def __init__(self, config: Box):
        self.config = config
        self.log = logging.getLogger(__name__)
        self.author = config.author
        self.title = ""
        self.date = ""
        self.featured_image = ""
        self.categories = ""
        self.tags = []

    def mkdir_from_date(self) -> str:
        """
        Method to create the directory where the post will be saved based on its date
        """
        year = self.date[0:4]
        month = self.date[5:7]
        author = self.author.lower().replace(" ", "")
        file_dir = os.path.join(
            self.config.site_dir, f"content/posts/{author}/{year}/{month}/"
        )
        os.makedirs(file_dir, exist_ok=True)
        return file_dir

    def make_file_name(self, prefix: str, number: int) -> str:
        """
        Method to create the post file name based on its title
        """
        file_name = f"{prefix}-{number}-{'-'.join(self.title.lower().split()[:5])}"
        file_name = re.sub("[^a-z0-9\\-]+", "", file_name) + ".md"
        return file_name

    def make_header(self) -> str:
        """
        Method to create post header including title, author, date, main image, categories, and tags
        """
        # Prepare title
        title = self.title
        title = re.sub(":", "...", title)  # colon in title causes yaml trouble
        # title = re.sub('^[\'\"]', '', title)  # apostrophe at beginning of title causes yaml trouble
        if "'" not in title:
            title = f"'{title}'"
        elif '"' not in title:
            title = f'"{title}"'
        # Prepare tags
        if self.tags:
            tags = list(dict.fromkeys(self.tags))  # remove duplicate tags
            tags = [
                ftfy.fix_text(t).lower().replace("@", "").replace("#", "") for t in tags
            ]
            tags = "\n- " + "\n- ".join(tags)
        else:
            tags = ""
        if self.categories:
            categories = f"{self.author}'s {self.categories}"
        else:
            categories = ""
        # Generate header
        header = "\n".join(
            [
                "---",
                f"title: {title}",
                f"date: {self.date}",
                f"author: {self.author}",
                f"featured_image: '{self.featured_image}'",
                f"categories: {categories}",
                f"tags: {tags}",
                "---",
            ]
        )
        return header

    @abstractmethod
    def get_post(self, post: dict):
        """
        Method to extract information from json file containing posts
        """
        raise NotImplementedError("Child class must implement this method.")

    @abstractmethod
    def update_site(self, post_number: int):
        """
        Method for generating a markdown post file based on its contents
        """
        raise NotImplementedError("Child class must implement this method.")

    def create_file(
        self,
        header: str,
        content: str,
        file_dir: str,
        file_name: str,
        verbose: bool = False,
    ):
        """
        Method for creating a Hugo post file out from a header and content
        """
        dst = os.path.join(file_dir, file_name)
        if verbose:
            self.log.info(f"Creating file {dst}")
            self.log.info(header)
        with open(dst, "w") as post:
            post.write(header)
            post.write("\n" + content)


class FacebookPost(Post):
    def __init__(self, config: Box):
        super().__init__(config)
        self.categories = "Facebook Post"
        self.data = ""
        self.uri = ""
        self.loc = ""

    def update_site(self, post_number: int):
        default_text = "Facebook status update"
        if self.title:
            split_title = self.title.split()
            if len(split_title) > 10:
                content = self.title + "\n\n" + self.data.replace(self.title, "")
                self.title = " ".join(split_title[:10]) + "..."
            else:
                content = self.data
        elif self.data:
            split_data = self.data.split()
            if len(split_data) > 10:
                self.title = " ".join(split_data[:10]) + "..."
                content = self.data
            else:
                self.title = self.data
                content = default_text
        else:
            self.title = default_text
            content = ""
        if self.uri:
            author = self.author.lower().replace(" ", "")
            src = os.path.join(self.config.facebook_export_dir, self.uri)
            dst = os.path.join(
                self.config.site_dir, "static", author, "facebook", self.uri
            )
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            content += f"\n![img](/{author}/facebook/{self.uri})"
            self.featured_image = f"/{author}/facebook/{self.uri}"
        file_dir = self.mkdir_from_date()
        file_name = self.make_file_name("fb", post_number)
        header = self.make_header()
        self.create_file(header, content, file_dir, file_name)

    def get_post(self, post):
        if "attachments" in post and len(post["attachments"]) > 0:
            self.get_attachment(post)
        elif "data" in post:
            self.get_data(post)

    def get_tags(self, post: dict):
        if "tags" in post:
            self.tags = [t["name"] for t in post["tags"]]

    def get_attachment(self, post: dict):
        if "data" in post:
            self.get_data(post)
            self.title = self.data
            self.data = ""
        attachments = post["attachments"]
        for attachment in attachments:
            data = attachment["data"][0]
            if "external_context" in data:
                external = data["external_context"]
                if "url" in external:
                    self.data += "\n" + external["url"]
                if "name" in external:
                    self.data += "\n" + external["name"]
            if self.data and not self.title:
                self.title = "External content posted"
                timestamp = post["timestamp"]
                self.date = get_date_from_timestamp(timestamp)
            if "media" in data:
                self.uri = data["media"]["uri"]
            if "place" in data:
                self.get_location(data)

    def get_title(self, post: dict):
        if "title" in post:
            self.title = ftfy.fix_text(post["title"])

    def get_location(self, data: dict):
        place = data["place"]
        if "coordinate" in place:
            loc = place["coordinate"]
            loc_data = []
            for val in loc.values():
                r_val = round(val, 3)
                loc_data.append(str(r_val))
            self.loc = loc_data[0] + " " + loc_data[1]

    def get_data(self, post: dict):
        data = post["data"]
        timestamp = post["timestamp"]
        for d in data:
            if "post" in d:
                self.date = get_date_from_timestamp(timestamp)
                self.data = ftfy.fix_text(d["post"])


class FacebookAlbum(Post):
    def __init__(self, config: Box):
        super().__init__(config)
        self.categories = "Facebook Album"
        self.media = []
        self.tags = ["album"]

    def update_site(self, album_number: int):
        timestamp = 0
        content = []
        author = self.author.lower().replace(" ", "")
        for f in self.media:
            media_uri = f["uri"]
            if not self.featured_image:
                self.featured_image = f"/{author}/facebook/{media_uri}"
            if "description" in f:
                media_title = ftfy.fix_text(f["description"]) + " "
            else:
                media_title = ""
            media_timestamp = f["creation_timestamp"]
            if media_timestamp > timestamp:
                timestamp = media_timestamp
            media_date = get_date_from_timestamp(timestamp)
            src = os.path.join(self.config.facebook_export_dir, media_uri)
            dst = os.path.join(
                self.config.site_dir, "static", author, "facebook", media_uri
            )
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            content.append(
                f"{media_title}{media_date}\n![img](/{author}/facebook/{media_uri})"
            )
        self.date = get_date_from_timestamp(timestamp)
        header = self.make_header()
        content = "\n\n".join(content)
        file_dir = self.mkdir_from_date()
        file_name = self.make_file_name("fb-album", album_number)
        self.create_file(header, content, file_dir, file_name)

    def get_post(self, album: dict):
        self.title = ftfy.fix_text(album["name"])
        self.media = album["photos"]


class InstagramPost(Post):
    def __init__(self, config: Box):
        super().__init__(config)
        self.categories = "Instagram post"
        self.media = []

    def update_site(self, post_number: int):
        if self.title == "":
            self.title = "Posted to Instagram"
            content = []
        else:
            split_title = self.title.split()
            self.tags = [x for x in split_title if x.strip()[0] in ["@", "#"]]
            if len(split_title) > 10:
                content = [self.title]
                self.title = " ".join(split_title[:10]) + "..."
            else:
                content = []

        file_dir = self.mkdir_from_date()
        file_name = self.make_file_name("insta", post_number)
        author = self.author.lower().replace(" ", "")
        for m in self.media:
            media_uri = m["uri"]
            media_title = ftfy.fix_text(m["title"])
            if "http" not in media_uri:
                src = os.path.join(self.config.instagram_export_dir, media_uri)
                dst = os.path.join(
                    self.config.site_dir, "static", author, "instagram", media_uri
                )
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                content.append(f"\n![img](/{author}/instagram/{media_uri})")
                if not self.featured_image:
                    self.featured_image = f"/{author}/instagram/{media_uri}"
            else:
                content.append(f"\n![img]({media_uri})")
            if media_title != self.title:
                content.append(f"{media_title}")
                self.tags += [
                    x for x in media_title.split() if x.strip()[0] in ["@", "#"]
                ]

        header = self.make_header()
        content = "\n".join(content)
        self.create_file(header, content, file_dir, file_name)

    def get_post(self, post: dict):
        self.media = post["media"]
        if "creation_timestamp" in post:
            timestamp = post["creation_timestamp"]
            self.title = ftfy.fix_text(post["title"])
        else:
            timestamp = self.media[0]["creation_timestamp"]
            self.title = ftfy.fix_text(self.media[0]["title"])
        self.date = get_date_from_timestamp(timestamp)
