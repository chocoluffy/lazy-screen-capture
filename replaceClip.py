# -*- coding: utf-8 -*-
import subprocess
import os

# something to improve: copy that image url into clipboard by using `pbpaste`, and second, set this script into `.zshrc` and make an alias for it
# so that I can access it really fast and handy!!

# the path where OSX will put screen shot to, the default is set to Desktop.
dirpath = "/Users/yushunzhe/ScreenCapture/"


def read_from_clipboard():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))

import hashlib
import re
import sqlite3
from sys import argv

import tinify
import leancloud
from leancloud import File

# TinyPng API key (link: https://tinypng.com/developers)
TINY_API_KEY = <TINY_API_KEY>

# LeanCloud API id & key (link: https://leancloud.cn/docs/python_guide.html)
LEAN_CLOUD_API_ID = <LEAN_CLOUD_API_ID>
LEAN_CLOUD_API_KEY = <LEAN_CLOUD_API_KEY>

# Match image in Markdown pattern
INSERT_IMAGE_PATTERN = re.compile('(!\[.*?\]\((?!http)(.*?)\))', re.DOTALL)


# Init TinyPng and LeanCloud API
def init_api():
    tinify.key = TINY_API_KEY
    leancloud.init(LEAN_CLOUD_API_ID, LEAN_CLOUD_API_KEY)


def get_file_size(file_path):
    return float(os.path.getsize(file_path))


# Find image in target directory
def get_image_from_dir():
    return os.listdir(dirpath)[-1]



# Compress image by TinyPng (https://tinypng.com)
def compress(source, target):
    filepath = dirpath + source
    cp_filepath = dirpath + target
    # print("[%s]" % os.path.split(source)[1]),
    data = tinify.from_file(filepath)
    data.to_file(cp_filepath)
    scale = get_file_size(cp_filepath) / get_file_size(filepath)
    # print ('⬇ %.2f%%' % ((1 - scale) * 100)),


# Upload image to LeanCloud
def upload(file_path):
    cmp_file_path = dirpath + file_path
    if os.path.exists(cmp_file_path):
        img_name = os.path.split(cmp_file_path)[1]
        img_file = open(cmp_file_path)
        up_file = File(img_name, img_file)
        img_url = up_file.save().url
        # print(" url: %s" % img_url)
        return img_url


# Calculate image file hash value
def calc_hash(file):
    filepath = dirpath + file
    with open(filepath, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        file_hash = sha1obj.hexdigest()
        return file_hash


def connect_db(path):
    conn = sqlite3.connect(os.path.join(path, "ImageInfo.db"))
    conn.execute('''
       CREATE TABLE IF NOT EXISTS ImageInfo(
       hash    TEXT    NOT NULL PRIMARY KEY,
       url     TEXT    NOT NULL
       );
    ''')
    return conn


def write_db(conn, img_hash, img_url):
    conn.execute("INSERT INTO ImageInfo (hash, url) VALUES ('%s','%s')" % (img_hash, img_url))
    conn.commit()


def find_in_db(conn, img_hash):
    cursor = conn.execute('SELECT * FROM ImageInfo WHERE hash=?', (img_hash,))
    return cursor.fetchone()


def replace_img(conn):
    image = get_image_from_dir()

    # print 'start >>>>>\n'


    db_data = find_in_db(conn, calc_hash(image))
    if db_data:
        # print("[%s] >>> \nurl: %s" % (os.path.split(image)[1], db_data[1]))
        print db_data[1]
        url = db_data[1]
    else:
        compressed_img = os.path.join(os.path.split(image)[0], 'cp_' + os.path.split(image)[1])
        compress(image, compressed_img)
        url = upload(compressed_img)
        print url
        write_db(conn, calc_hash(image), url)

    write_to_clipboard(url)
    # print '\n<<<<< end'


def main(script_file):
    init_api()
    db_connect = connect_db(os.path.split(script_file[0])[0])
    replace_img(db_connect)
    db_connect.close()



if __name__ == '__main__':
    if len(argv) < 2:
        script = argv
        main(script)
    else:
        print 'please enter valid script name!'
