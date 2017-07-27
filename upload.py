# -*- coding: utf-8 -*-

# NOTE: in order to run this in Console, you need to first run "chcp 862"

from datetime import datetime
from xmlrpclib import ProtocolError

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from os import listdir
from os.path import join, isfile
import re
import codecs
from operator import itemgetter
from datetime import timedelta

wp = Client('http://ozveshalom.org.il/blog/xmlrpc-copy.php', 'ozveshalom', 'ozveshalom1')
years = {
    u'תשנ"ח': 1998,
    u'תשנ"ט': 1999,
    u'תש"ס': 2000,
    u'תשס"א': 2001,
    u'תשס"ב': 2002,
    u'תשס"ג': 2003,
    u'תשס"ד': 2004,
    u'תשס"ה': 2005,
    u'תשס"ו': 2006,
    u'תשס"ז': 2007,
    u'תשס"ח': 2008,
    u'תשס"ט': 2009,
    u'תש"ע': 2010,
    u'תשע"א': 2011,
    u'תשע"ב': 2012,
    u'תשע"ג': 2013,
    u'תשע"ד': 2014,
    u'תשע"ה': 2015,
    u'תשע"ו': 2016,
}

list_file = codecs.open('list.txt', 'r', encoding='utf-8')
parsha_list = [l.strip().split('\t') for l in list_file.readlines()]


def get_names(name):
    return next((names for names in parsha_list if name.lower() in
                 [w.lower() for w in names] or name[::-1].lower() in [w.lower() for w in names]), [])


def read_heb_file(heb_filename):
    name = join('parsha', heb_filename)
    heb_file_obj = codecs.open(unicode(name), 'r', encoding='windows-1255')
    # o = open(unicode(p), 'r')

    # print f
    data = heb_file_obj.read()
    m = re.search('<FONT SIZE="?\+4"? COLOR="navy">(.*)</FONT>', data, flags=re.UNICODE + re.IGNORECASE)
    n = re.search('<FONT SIZE="3" COLOR="navy">((\D*)\W*(\d+))\W*(.*)</FONT>', data, flags=re.UNICODE + re.IGNORECASE)
    if not n:
        print heb_filename.encode('utf-8')

    gilyon_num = n.group(3)
    year = n.group(2) if ' ' in n.group(4) else n.group(4)
    # title = n.group(4) if ' ' in n.group(4) else n.group(2)
    year = year.replace('&quot;', '"').strip()
    if year not in years:
        year = year[::-1]
    year_num = years[year]
    parsha = m.group(1).strip()
    if u'תשרפ' in parsha:
        parsha = parsha[::-1]

    parsha = parsha.split(' - ')[0].replace(u'פרשת ', u'').strip().replace(u'-', u' ')
    parsha = parsha.split(', ')[0]
    parsha_names = get_names(parsha)
    if not parsha_names:
        print 'Cannot find ', parsha.encode('utf-8'), '\t\tfile: ', heb_filename.encode('utf-8')
        exit(1)
    title = parsha.strip() + ' ' + year + u' (גליון מספר ' + gilyon_num + ')'
    return {'id': int(gilyon_num), 'year': year_num, 'yearName': year, 'title': title, 'parsha': parsha, 'page': data,
            'lang': 'עברית', 'file': heb_filename, 'names': parsha_names,
            'lower_names': [n.lower() for n in parsha_names]}


def file_match(prop, name, year):
    return prop['file'].lower().startswith(name.lower()) and year in prop['file']


# noinspection SpellCheckingInspection
# file_to_debug = 'shvii'


def process_english_file(eng_filename):
    # name = join(u'parsha-eng', f)
    # o = codecs.open(unicode(name), 'r', encoding='windows-1255')
    # o = open(unicode(p), 'r')
    # t = o.read()
    # if file_to_debug in eng_filename:
    #     print 'DEBUG'

    parts = re.match('([A-Za-z\-]*).*(57\d\d?)', eng_filename, flags=re.IGNORECASE)
    if not parts:
        print 'File name does not match pattern <parsha><year>:', eng_filename
        return 1

    name = unicode(parts.group(1))
    lower_name = name.lower()
    year = parts.group(2)
    names = get_names(name)
    if not names:
        print 'Parsha name not found: ', eng_filename, name
        exit(1)

    found = False

    for item in heb_list:
        if file_match(item, name, year):
            set_eng_file(item, eng_filename)
            found = True
            break

        if lower_name in item['lower_names']:
            # print 'XXX', name, p['file'].encode('utf-8'), p['names'], year
            for n in item['names']:
                if file_match(item, n, year):
                    set_eng_file(item, eng_filename)
                    found = True
                    break

            if not found:
                for n in item['names']:
                    if check_eng_match(n, year, eng_filename):
                        found = True
                        break

    if not found:
        print 'Heb file not found for: ', eng_filename
        # exit(1)
        return 1

    return 0


def check_eng_match(name, year, eng_filename):
    for heb_item in heb_list:
        if file_match(heb_item, name, year):
            set_eng_file(heb_item, eng_filename)
            return True

    return False


def set_eng_file(item, eng_filename):
    item['eng-file'] = eng_filename


def set_dates():
    current_year = 0
    current_date = None

    for item in heb_list:
        if item['year'] != current_year:
            current_year = item['year']
            current_date = datetime(current_year, 1, 1, 16, 0, 0, 0)
        else:
            current_date = current_date + timedelta(days=5)
        item['date'] = current_date


# dir = u'parsha'
heb_files = listdir(u'parsha')
eng_files = listdir(u'parsha-eng')
print 'Processing Hebrew files...'
heb_list = [read_heb_file(heb_file) for heb_file in heb_files]

list_to_post = ['eng']
heb_list.sort(key=itemgetter('id'))
set_dates()

if 'heb' in list_to_post:
    print 'Uploading Hebrew files'
    for p in heb_list:
        post = WordPressPost()
        post.title = p['title']
        post.content = p['page']
        post.post_status = 'publish'
        post.date = p['date']
        post.date_modified = p['date']
        post.terms_names = {
            'post_tag': [p['yearName'], p['parsha']],
            'category': [u'גליונות שבת שלום'],
        }

        filename = p['file']
        if isfile(join(u'parsha', filename.replace('.htm', '-converted.htm'))):
            continue
        print 'Posting ' + post.title
        # print p['date']
        post.id = wp.call(NewPost(post))
        print 'id: ', post.id

# count = 0
files = []
ids = []
if 'eng' in list_to_post:
    print 'Uploading English files'
    alignJustifyPattern = re.compile(' ALIGN="justify"', re.IGNORECASE)

    cc = []
    for eng_file in eng_files:
        process_english_file(eng_file)
        cc.append('// ' + eng_file)

    cc.sort()
    f2 = open('./eng_files.txt', 'w+')
    f2.write('\n'.join(cc))

    for p in heb_list:
        if 'eng-file' not in p:
            continue

        # if file_to_debug in p['eng-file']:
        #     print 'DEBUG 2'

        if isfile(join(u'parsha', p['file'].replace('.htm', '-converted.htm'))):
            continue

        # if '-converted' in p['file']:
        #     continue

        # count += 1
        # files.append('// ' + p['eng-file'] + ' // ' + unicode(p['id']))
        # ids.append(p['id'])
        # continue

        post = WordPressPost()
        year_heb_num = unicode(p['year'] + 3760)
        parsha_eng = p['names'][1]
        post.title = parsha_eng + ' ' + year_heb_num + ' - Gilayon #' + unicode(p['id'])
        end_date = p['date'] + timedelta(days=1)
        # print 'Reading', p['eng-file']
        content = codecs.open(join('parsha-eng', p['eng-file']), 'r', encoding='windows-1255').read()
        content = alignJustifyPattern.sub('', content)
        post.content = content
        post.post_status = 'publish'
        post.date = end_date
        post.date_modified = end_date
        post.terms_names = {
            'post_tag': [p['yearName'], p['parsha'], parsha_eng, year_heb_num],
            'category': ['Shabat Shalom'],
        }

        filename = p['eng-file']
        print 'Posting ' + post.title
        # print end_date
        try:
            post.id = wp.call(NewPost(post))
            print 'id: ', post.id
        except ProtocolError:
            print 'An error has occurred uploading ' + p['eng-file'] + '. It probably contains Hebrew characters.'

# files.sort()
# f1 = open('./files.txt', 'w+')
# f1.write('\n'.join(files))
#
# ids.sort()
# f3 = open('./ids.txt', 'w+')
# f3.write('\n'.join([unicode(id) for id in ids]))
# print 'count', count

# todo:
# handle English files that miss year
# find matching hebrew files for English files
# find the way to tag (Hebrew/English, Archive)
# upload...

# posts = wp.call(GetPosts())
# print len(posts)

# post = WordPressPost()
# post.title = 'My post'
# post.content = '<html><b>Hi</b>This is a wonderful blog post about XML-RPC.</html>'
# post.post_status = 'publish'
# post.date = datetime(2015, 1, 1)
# post.date_modified  = datetime(2015, 1, 1)
# # print dir(post)
# post.id = wp.call(NewPost(post))
# print post.id
