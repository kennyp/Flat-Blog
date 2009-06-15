#!/usr/bin/env python
from optparse import OptionParser
from sys import (stderr,exit)
import re
import string
from markdown import (Markdown,TextPreprocessor)
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from BeautifulSoup import BeautifulSoup

# Constants
INLINESTYLES = False

def main():
    # setup the option parser
    parser = OptionParser(usage="usage: %prog [options] [articles]",version="%prog 1.0")
    parser.add_option("-p","--publish",action="store_false",help="render then publish",dest="publish",default=True)
    parser.add_option("-r","--render",action="store_false",help="only render",dest="publish")
    parser.add_option("--stdout",action="store_true",help="render to stdout",dest="stdout",default=False)

    # Parse the options
    (options, articles) = parser.parse_args()
    stdout = options.stdout
    publish = options.publish and not stdout

    if len(articles) == 0:
        print >> stderr,"At least one file is required"
        exit(1)

    for article in articles:
        print "Processing: " + article
        render_article(article,stdout)
        if publish:
            publish_article(article)

def render_article(article,stdout=True):
    print "\tRendering"
    with open('input/_head.html','r') as head_file:
        head = head_file.read()
    with open('input/_tail.html','r') as tail_file:
        tail = tail_file.read()
    with open(article,'r') as a:
        article_contents = a.read()
    rendered_article = head + BeautifulSoup(render_text(article_contents)).prettify() + tail
    if stdout:
        print rendered_article

def publish_article(article):
    print "\tPublishing"

def render_text(text):
    md = Markdown()
    md.textPreprocessors.insert(0, WrapPreprocessor())
    md.textPreprocessors.insert(1, CodeBlockPreprocessor())
    return md.convert(text)

class WrapPreprocessor(TextPreprocessor):

    def run(self, lines):
        with open('input/_layout.markdown','r') as layout:
            layout_contents = layout.read()
        pattern = re.compile(r'\[partial:(.+?)\]', re.S)
        partials = pattern.findall(layout_contents)
        for partial in partials:
            with open('input/' + partial,'r') as partial_file:
                layout_contents = string.replace(layout_contents, '[partial:'+partial+']', partial_file.read())
        return string.replace(layout_contents,'[article_contents]',lines)

class CodeBlockPreprocessor(TextPreprocessor):

    pattern = re.compile(
        r'\[sourcecode:(.+?)\](.+?)\[/sourcecode\]', re.S)

    formatter = HtmlFormatter(noclasses=INLINESTYLES)

    def run(self, lines):
        def repl(m):
            try:
                lexer = get_lexer_by_name(m.group(1))
            except ValueError:
                lexer = TextLexer()
            code = highlight(m.group(2), lexer, self.formatter)
            code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
            return '\n\n<div class="code">%s</div>\n\n' % code
        return self.pattern.sub(
            repl, lines)

# See if we're the main script
if __name__ == "__main__":
    main()
