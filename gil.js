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
    $('table.main tr td a').each((i, a) => $(a).attr('style', 'text-decoration: underline;'));

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

//function loadXMLDoc(filePath) {
//    var xml2js = require('xml2js');
//    var json;
//    try {
//        var fileData = fs.readFileSync(filePath, 'utf-8');
//
//        var parser = new xml2js.Parser();
//        var funcResult;
//        parser.parseString(fileData.substring(0, fileData.length), function (err, result) {
//            if(err) {
//                console.log("Error in parsing: ", err);
//                throw err;
//            }
//            funcResult = result;
//        });
//
//        return funcResult;
//    } catch (ex) {console.log("Exception: ", ex)}
//}
//
//function buildTD(td) {
//    if(!td || !td.B || !td.B[0]) { return '';}
//    var h = '<li>' + reverse(td.B[0]);
//    td.A.forEach(A => {
//        //h += '<br><a href="' + A.$.HREF + '">' + reverse(A._) + '</a>';
//    })
//    return h + '</li>';
//}
