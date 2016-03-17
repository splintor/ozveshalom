'use strict'
const fs = require('fs');
const iconvLite = require('iconv-lite');

function reverse(s) {
    if(s.indexOf('<') >= 0) throw 'unexpected < in ' + s;
    return s.trim()
            .replace(/;$/g, '')
            .replace(/^; /, '')
            .replace(/ /g, '&space;')
            .replace(/-/g, '&minus;')
            .split(';').reverse().join(';')
            .replace(/&space;/g, ' ')
            .replace(/&minus;/g, '-')
            .replace(/(&#x...)$/, '$1;')
}

function reverseAll($, selector, debug) {
    const collection = $(selector);
    console.log('Reversing "' + selector + '" (' + collection.length + ' items)...');
    if(debug) {
        var d = $(collection[debug]);
        console.log('Reversing ' + d.html() + ' to ' + reverse(d.html()));
    }
    collection.each((i,item) => {
        item = $(item);
        item.html(reverse(item.html()));
    });
}

function reverseTR($, tr) {
    tr = $(tr);
    tr.children('td:not(:first-child)').each((i, td) => { $(td).remove(); tr.prepend($(td))});
}

function processHtml(html) {
    var cheerio = require('cheerio')
    var $ = cheerio.load(html);
    $('font table').addClass('main');
    reverseAll($, 'table.main tr td b');
    reverseAll($, 'table.main tr td a');
    reverseAll($, 'table.main tr td font');
    $('table.main tr').each((i, tr) => reverseTR($, tr));
    $('table.main tr td font').each((i, font) => {
        font = $(font);
        const a = $(font.next());
        font.remove();
        a.after(font);
        font.text(' ' + font.text());
        font.attr('style', 'font-size: 0.6em;');
    });
    const pHtml = '<p style="margin: 0;"></p>';
    $('table.main tr td a').each((i, a) => {
        a = $(a);
        a.attr('style', 'text-decoration: underline;');
        a.prev('br').remove();
        a.before(pHtml);
        var href = a.attr('href');
        a.attr('href', 'http://www.netivot-shalom.org.il/' + href);
        const p = a.prev('p');
        var font = $(a.next('font'));
        a.remove();
        p.append(a);
        if(font && font.length) {
            font.remove();
            p.append(font);
        }
    });

    $('table.main tr td b').each((i, b) => {
        b = $(b);
        b.attr('style', 'background-color:antiquewhite; padding-left: 5px;');
        b.before(pHtml);
        const p = b.prev('p');
        b.remove();
        p.append(b);
    });
    const htmlBuffer = iconvLite.encode($('font:has(table)').html().replace(/<!--[\s\S]*?-->/g, ''), 'iso-8859-8');
    fs.writeFileSync('out.html', htmlBuffer);
}

(function main() {
    var arg = process.argv[2];
    console.log('starting...', arg || '');
    if (arg === 'local') {
        const htmlBuffer1 = fs.readFileSync('page.html');
        const htmlFromFile1 = iconvLite.decode(htmlBuffer1, 'iso-8859-8');
        processHtml(htmlFromFile1);
        console.log('done (local file)');
    } else {
        console.log('getting data from \'www.netivot-shalom.org.il\'...');
        let htmlBuffer = new Buffer('', 'binary');
        require('http').get('http://www.netivot-shalom.org.il/parsha.php', response => {
            response.setEncoding('binary');
            response.on('data', chunk => {
                htmlBuffer = Buffer.concat([htmlBuffer, new Buffer(chunk, 'binary')]);
            }).
            on('end', () => {
                console.log('download done. Parsing...');
                const htmlFromFile = iconvLite.decode(htmlBuffer, 'iso-8859-8');
                processHtml(htmlFromFile);
                console.log('done');
            });
        });
    }
})();
