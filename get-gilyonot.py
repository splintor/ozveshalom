# -*- coding: utf-8 -*-
import os
import re
import sys
import requests

english = False
english_articles = False

parsha_dir = 'parsha-eng' if english else 'parsha'
main_filename = 'eparsha' if english else 'parsha'
if english_articles:
    main_filename = 'articles'
    parsha_dir = 'articles'


def get_page():
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        print 'using local %s.html...' % main_filename
        with open('%s.html' % main_filename, 'r') as page_file:
            return page_file.read()

    url = 'http://www.netivot-shalom.org.il/%s.php' % main_filename
    print 'downloading %s...' % url
    content = requests.get(url).content
    with open('%s.html' % main_filename, 'w') as page_file:
        page_file.write(content)
    return content


years = {
    '\xe7"\xf0\xf9\xfa': 5758,
    '\xe8"\xf0\xf9\xfa': 5759,
    '\xf1"\xf0\xf9\xfa': 5760, # שלח-לך
    '\xf1"\xf9\xfa': 5760,
    '\xe0"\xf1\xf9\xfa': 5761,
    '\xe1"\xf1\xf9\xfa': 5762,
    '\xe2"\xf1\xf9\xfa': 5763,
    '\xe3"\xf1\xf9\xfa': 5764,
    '\xe4"\xf1\xf9\xfa': 5765,
    '\xe5"\xf1\xf9\xfa': 5766,
    '\xe6"\xf1\xf9\xfa': 5767,
    '\xe7"\xf1\xf9\xfa': 5768,
    '\xe8"\xf1\xf9\xfa': 5769,
    '\xf2"\xf9\xfa': 5770,
    '\xe0"\xf2\xf9\xfa': 5771,
    '\xe1"\xf2\xf9\xfa': 5772,
    '\xe2"\xf2\xf9\xfa': 5773,
    '\xe3"\xf2\xf9\xfa': 5774,
    '\xe4"\xf2\xf9\xfa': 5775,
    '\xe5"\xf2\xf9\xfa': 5776,
}


def get_heb_year(year):
    return years[year]


def process_parsha(page_name, year, special):
    if ' ' in year:
        return  # this is the "current parsha" link in the header - ignore

    if year == '':
        return  # link to root directory

    print 'processing %s...' % page_name

    if english:
        page_name = page_name.replace('\xf7', 'e')  # fix problem with link for teruma5762.php
        filename = '%s\%s' % (parsha_dir, page_name)
    else:
        filename = '%s\%s-%s' % (parsha_dir, page_name, get_heb_year(year))
        if special:
            filename += '-' + special.replace('"', '').decode('Cp1255')[::-1]
    filename += '.html'
    if os.path.exists(filename):
        print 'skipping %s... (already downloaded)' % page_name
        return

    print 'getting %s...' % page_name
    pathname = year if english else 'parshheb'
    page_content = requests.get('http://www.netivot-shalom.org.il/%s/%s.php' % (pathname, page_name)).content
    page_content = cleanup_page(page_content)
    print '- writing %s...' % filename
    with open(filename, 'w') as page_file:
        page_file.write(page_content)


def cleanup_page(content):
    content = re.sub('<font size="\+3" color=blue>[^<]*</font>', '', content)  # clean ozveshalom title
    content = re.sub('<table border=0 cellpadding=3 ALIGN="center" dir=ltr>.*</body>', '</body>', content,
                     flags=re.DOTALL)  # clean links footer
    content = re.sub('<img[^>]*>', '', content, flags=re.IGNORECASE)  # clean all images
    return content


def process_page(page):
    if not os.path.exists(parsha_dir):
        os.makedirs(parsha_dir)

    if english:
        for m in re.findall('<a href="([^/.>]*)/([^./]*).php">', page, flags=re.IGNORECASE):
            process_parsha(m[1], m[0], '')
        if not english_articles:
            process_parsha('bereishit5761', '', '')  # broken link
    else:
        for m in re.findall('(<FONT SIZE="1">([^<]*)</FONT>)*\W*<A HREF="parshheb/([^.]+)\.php">([^<]*)</A>', page, re.IGNORECASE):
            process_parsha(m[2], m[3], m[1])


def main():
    page = get_page()
    process_page(page)


if __name__ == '__main__':
    main()
