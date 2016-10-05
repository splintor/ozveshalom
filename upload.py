# -*- coding: utf-8 -*-
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from os import listdir
from os.path import join
from sys import getfilesystemencoding
import re
import codecs
from operator import itemgetter
from datetime import date

# wp = Client('http://ozveshalom.org.il/blog/xmlrpc-copy.php', 'ozveshalom', 'ozveshalom1')
years = {
    u'תשנ"ח': 1998,
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
    return next((names for names in parsha_list if name.lower() in [w.lower() for w in names] or name[::-1].lower() in [w.lower() for w in names]), [])


def read_heb_file(f):
    p = join(u'parsha', f)
    o = codecs.open(unicode(p), 'r', encoding='windows-1255')
    # o = open(unicode(p), 'r')

    # print f
    t = o.read()
    m = re.search('<FONT SIZE="?\+4"? COLOR="navy">(.*)</FONT>', t, flags=re.UNICODE + re.IGNORECASE)
    n = re.search('<FONT SIZE="3" COLOR="navy">((\D*)\W*(\d+))\W*(.*)</FONT>', t, flags=re.UNICODE + re.IGNORECASE)
    # if not m:
    #     print f.encode('utf-8')

    # print m.group(1)
    # print n.group(1)
    id = n.group(3)
    year = n.group(2) if ' ' in n.group(4) else n.group(4)
    # title = n.group(4) if ' ' in n.group(4) else n.group(2)
    year = year.replace('&quot;', '"').strip()
    parsha = m.group(1).strip()
    if u'תשרפ' in parsha:
        parsha = parsha[::-1]

    parsha = parsha.split(' - ')[0].replace(u'פרשת ', u'').strip().replace(u'-', u' ')
    parsha = parsha.split(', ')[0]
    parsha_names = get_names(parsha)
    if not parsha_names:
        print 'cannot find ', parsha, '\t\tfile: ', f
        exit(1)
    title = parsha.strip() + ' ' + year + u' (גליון מספר ' + id + ')'
    yearNum = years[year] if year in years else years[year[::-1]]
    if 'rei2-5759' in f:
        print 'DDD', f.encode('utf-8'), parsha.encode('utf-8'), parsha_names
    return {'id': int(id), 'year': yearNum, 'title': title, 'page': t, 'lang': 'hebrew', 'file': f, 'names': parsha_names}


def process_english_file(f):
    p = join(u'parsha-eng', f)
    o = codecs.open(unicode(p), 'r', encoding='windows-1255')
    # o = open(unicode(p), 'r')
    # t = o.read()
    p = re.match('([A-Za-z\-]*).*(57\d\d?)', f, flags=re.IGNORECASE)
    if not p:
        print 'File name does not match pattern <parsha><year>:', f
        return 1

    name = p.group(1)
    year = p.group(2)
    names = get_names(name)
    if not names:
        print 'Parsha name not found: ', f
        exit(1)

    found = False
    for p in plist:
        if name in p['names']:
            print name, p['file'].encode('utf-8'), p['names']
            for n in p['names']:
                if p['file'].startswith(n) and year in p['file']:
                    p['eng-file'] = f
                    # print 'FOUND: ', f
                    found = True
                    break

    if not found:
        print 'Heb file not found for: ', f
        exit(1)
        return 1

    return 0

# dir = u'parsha'
heb_files = listdir(u'parsha')
eng_files = listdir(u'parsha-eng')
plist = [read_heb_file(f) for f in heb_files]
counter = sum([process_english_file(f) for f in eng_files])
print counter

exit(counter)

plist.sort(key=itemgetter('id'))
current_year = 0
current_date = None
for p in plist:
    break
    post = WordPressPost()
    post.title = p['title']
    if p['year'] != current_year:
        current_year = p['year']
        current_date = date(current_year, 1, 1)
    post.content = p['page']
    post.post_status = 'publish'
    post.date = current_date
    post.date_modified  = current_date
    post.id = wp.call(NewPost(post))
    print post.id


#todo:
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