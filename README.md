# TreasureChest

`treasurechest` is a Python package to help you regain control of your treasured memories stored in social media sites such as Facebook and Instagram by importing them into a static site powered by [Hugo](https://gohugo.io), an open-source, fast, and modern static site generator.  

## Preparation

1. To use Treasure Chest you must first request a copy of your data from Facebook and/or Instagram in JSON format. You find guides for how to do this here:

    - [Requesting a copy of your data from Facebook](https://www.facebook.com/help/212802592074644) (You only need to select to download your publications, as this is the only type of data currently supported) 
    - [Requesting a copy of your data from Instagram](https://help.instagram.com/contact/505535973176353)
    
2. Set up your site with Hugo. You find a quick guide [here](https://gohugo.io/getting-started/quick-start/). I recommend using the [Diary](https://github.com/AmazingRise/hugo-theme-diary) theme instead, which allows to preview a featured image of each post. See an example [here](https://risehere.net).

3. Clone the Treasure Chest repository to your machine.

4. From the terminal, `cd` into your Treasure Chest directory and create a virtual environment with the required Python packages (requires Python >=3.6):

    ```shell
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt 
    ```
    
You're ready to go...

## Importing posts and albums to your site

Modify the configuration file `config/main.yaml` in your copy of the repo such that

- `name` contains the title of your site
- `author` has the name of the author of the posts
- `site_dir` contains the path of your Hugo site
- `facebook_export_dir` contains the path to your Facebook data
- `instagram_export_dir` contains the path to your Instagram data

`cd` into your Treasure Chest directory in the terminal. The virtual environment should be activated every time you start a new shell session before running subsequent commands:

```shell
source .venv/bin/activate
```

Use the following command to import your Facebook data:

```shell
python -m treasurechest import-from-facebook
```

By default `treasurechest` will import both posts and albums. You can also add the flag `--imports` with the option `posts` or `albums` to import only one type of data. 

Similarly, to import your Instagram posts:

```shell
python -m treasurechest import-from-instagram
```

This command does not support any options. To get additional help:

```
python -m treasurechest --help
```

If the import procedures run without error you may now deactivate the virtual environment:

```
deactivate
```

You are ready to take a look at your site! `cd` into your site's directory and run

```hugo server```

You should be able to open your site by pointing your browser to `http://localhost:1313`.



### File structure

Hugo posts use markdown syntax and are saved under the `content/` directory. `treasurechest` will save posts in the following directory structure:

```
author
└── year
    └── month
        └── prefix-postnumber-title.md
```

File names for Facebook posts are prefixed with `fb` and `fb-album`, while Instagram posts are prefixed with `insta`. Post numbers are assigned in order in which they are imported. 

`treasurechest` will try to guess sensible values for the title, date, featured image, and tags of each post. These values are included in the header of each post. Two additional fields are also included in the header:
- `author` is obtained from the configuration file
- `categories` are created based on the type of import. Facebook posts and albums will be saved under the category *[Author]'s Facebook post* and *[Author]'s Facebook album*, respectively. Instagram posts will be saved under the category *[Author]'s Instagram post*.

You may remove any files corresponding to posts that you feel are irrelevant. You can also update and modify them in any way you want. You even create new posts in your blog using the same file structure. If your server is running, you can observe the changes in real time on your browser. *The treasure is in your hands now!*
