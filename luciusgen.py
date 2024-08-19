import os, sys
from datetime import datetime
from pathlib import Path
import json
import logging
import shutil

from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown
from slugify import slugify
from watchdog import observers

import conf

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()

# DO NOT MESS WITH THESE!
DB_FILE = 'posts.db'
MANDATORY_FIELDS = ['title', 'date']
CWD = os.path.dirname(os.path.abspath(__file__))
MD_EXTS=["extra", "meta", "codehilite"]

def markdown_filter_file(md_file):
    with open(md_file, 'r') as f:
        result = markdown(f.read(), extras=['target-blank-links'])
    return result

class LuciusGen:
    def __init__(self, cwd, _config):
        self.conf = _config
        self.cwd = cwd
        self.content_path = _config.CONTENT_DIR        
        self.output_path = _config.OUTPUT_DIR
        self.posts_meta = {}
        self.render = Environment(loader=FileSystemLoader(searchpath=_config.TEMPLATE_DIR))
        self.render.trim_blocks = True
        self.render.lstrip_blocks = True
        self.site_data = conf.SITE_DATA

        # pre-load the templates
        self.post_template = self.render.get_template('post.html')
        self.index_template = self.render.get_template('index.html')
        self.category_template = self.render.get_template('category.html')
        self.static_templates = {
            "whoami.html": self.render.get_template('whoami.html'),
            "links.html": self.render.get_template("links.html")
        }

    def list_content(self):
        files = Path(self.content_path).rglob('*.md')
        return files

    def generate_index(self):
        print('* Generating index.html')
        
        index_data = {
            'site': self.site_data,
            'posts': self.sorted_posts_meta(),
            'blog_path': self.conf.BLOG_DIR
        }
        index_html = self.index_template.render(index_data)
        index_file_path = os.path.join(self.cwd, self.output_path, 'index.html')
        os.makedirs(os.path.dirname(index_file_path), exist_ok=True)
        with open(index_file_path, 'w', encoding='utf-8') as file:
            file.write(index_html)
            print("  -- index.html created!")

    def generate_static(self):
        print('* Generating static files')
        
        data = {
            'site': self.site_data,
            'blog_path': self.conf.BLOG_DIR,
            'markdown_render': markdown_filter_file
        }

        for out_file, templ in self.static_templates.items():
            html = templ.render(data)
            file_path = os.path.join(self.cwd, self.output_path, out_file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html)
                print("  -- {} created!".format(out_file))


    def generate_post(self, file_path):
        print('* Generating post {}'.format(file_path))
        post_file = os.path.join(self.cwd, file_path)
        with open(post_file, 'r', encoding='utf-8') as file:
            post = markdown(file.read(), extras={'metadata':{}, 
                                                 'fenced-code-blocks':{}, 'strike':{}, 
                                                 'tables':{}, 'footnotes':{}, 'breaks': {'on_backslash': True}
                                                })
            
            is_ok = True
            # check some mandatory metadata
            for field in MANDATORY_FIELDS:
                if not post.metadata.get(field): 
                    print('  -- Metadata "{}" is obligatory!'.format(field))
                    is_ok = False

            # if not ok, dont create anything
            if not is_ok:
                print('  -- Errors found! Post not created.')
                return False
                
            # check if the slug is set, if not, create one
            slug = post.metadata.get('slug')
            if not slug:
                slug = slugify(post.metadata.get('title'), only_ascii=True)
                post.metadata['slug'] = slug

            if not post.metadata.get('category'):
                post.metadata['category'] = self.conf.DEFAULT_CATEGORY

            # generate the html file
            post_data = {
                'site': self.site_data,
                'content': post,
                'post': post.metadata,
                'blog_path': self.conf.BLOG_DIR
            }
            post_html = self.post_template.render(post_data)
            post_file_path = os.path.join(self.cwd, self.output_path, 
                self.conf.BLOG_DIR, '{}.html'.format(slug))
            os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
            with open(post_file_path, 'w', encoding='utf-8') as file:
                file.write(post_html)
                print("  -- Post created!")
    
                # store the post metadata
                self.posts_meta[str(file_path)] = post.metadata

            self.copy_post_files(os.path.dirname(file_path))

            return True

    def copy_post_files(self, root_dir):
        for src_dir in self.conf.COPY_DIRS:
            files_src = os.path.join(self.cwd, root_dir, src_dir)
            files_dst = os.path.join(self.cwd, self.conf.OUTPUT_DIR, src_dir)
            if os.path.isdir(files_src):
                print('* copying "{}" to "{}"'.format(files_src, files_dst))
                if os.path.exists(files_dst):
                    for f in os.listdir(files_src):
                        shutil.copy2(os.path.join(files_src, f), files_dst)
                else:
                    shutil.copytree(files_src, files_dst)

    def copy_template_files(self):
        for _dir in ['css', 'js', 'img']:
            files_src = os.path.join(self.cwd, self.conf.TEMPLATE_DIR, _dir)
            files_dst = os.path.join(self.cwd, self.conf.OUTPUT_DIR, _dir)
            if os.path.isdir(files_src):
                if os.path.exists(files_dst):
                    for f in os.listdir(files_src):
                        shutil.copy2(os.path.join(files_src, f), files_dst)
                else:
                    shutil.copytree(files_src, files_dst)

    def generate_CNAME(self):
        if self.conf.CNAME:
            cname_file = os.path.join(self.cwd, self.conf.OUTPUT_DIR, 'CNAME')
            with open(cname_file, 'w', encoding='utf-8') as file:
                file.write(self.conf.CNAME)

    def clear_output(self):
        output_dir = os.path.join(self.cwd, conf.OUTPUT_DIR)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


    def load_db(self):
        dbfile = os.path.join(self.cwd, DB_FILE)
        if os.path.isfile(dbfile):
            with open(dbfile, 'r', encoding='utf-8') as file:
                self.posts_meta = json.load(file)
        
    def save_db(self):
        dbfile = os.path.join(self.cwd, DB_FILE)
        with open(dbfile, 'w', encoding='utf-8') as file:
            json.dump(self.posts_meta, file)

    def sorted_posts_meta(self):
        posts = []
        for k in self.posts_meta:
            posts.append(self.posts_meta[k])
        posts.sort(reverse=True, key=lambda p: p['date'])
        return posts

    def update(self):
        self.load_db()
        files = self.list_content()
        for file in files:
            if str(file) not in self.posts_meta:
                self.generate_post(file)
               
        self.copy_template_files()
        self.generate_index()
        self.generate_categories()
        self.generate_CNAME()
        self.save_db()

    def generate_all(self):
        self.clear_output()

        files = self.list_content()
        for file in files:
            self.generate_post(file)
        
        self.copy_template_files()
        self.generate_static()
        self.generate_index()
        self.generate_categories()
        self.generate_CNAME()
        self.save_db()

    def generate_categories(self):
        print('* Creating categories files')
        categories = {}
        for idx in self.posts_meta:
            post = self.posts_meta[idx]
            cat = post['category']
            if not categories.get(cat):
                categories[cat] = []
            categories[cat].append(post)
        
        for cat in categories:
            categories[cat].sort(reverse=True, key=lambda p: p['date'])

            cat_html = self.category_template.render({
                'site': self.site_data,
                'category': cat, 
                'posts': categories[cat],
                'blog_path': self.conf.BLOG_DIR
            })
            slug = slugify(cat, only_ascii=True)
            cat_file_path = os.path.join(self.cwd, self.output_path, self.conf.BLOG_DIR, 'category', '{}.html'.format(slug))
            os.makedirs(os.path.dirname(cat_file_path), exist_ok=True)
            with open(cat_file_path, 'w', encoding='utf-8') as file:
                file.write(cat_html)
            print('  -- category/{}.html created!'.format(slug))
        

if __name__ == '__main__':
    import time
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
    import http.server
    import socketserver
    import functools

    if "--serve" in sys.argv:

        HTTP_PORT = 8000
        generator = LuciusGen(CWD, conf)
        generator.generate_all()

        def event_proc(event):
            generator.generate_all()

        patterns = ['*']
        ignore_patterns = [
            os.path.join('.', conf.OUTPUT_DIR)+'*', 
            os.path.join('.', DB_FILE)
        ]
        ignore_dirs = False
        case_sensitive = True
        event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, 
            ignore_dirs, case_sensitive)
        
        event_handler.on_any_event = event_proc

        observer = Observer()
        observer.schedule(event_handler, '.', True)

        observer.start()
        try:
            serve_path = os.path.join(CWD, conf.OUTPUT_DIR)
            Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_path)
            with socketserver.TCPServer(("", HTTP_PORT), Handler) as httpd:
                print("serving at port", HTTP_PORT)
                httpd.serve_forever()
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
    else:
        LuciusGen(CWD, conf).generate_all()
    

    