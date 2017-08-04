# -*- coding: utf-8 -*-
import sys, argparse, re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

def pdfparser_page(data):
    fp = file(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
        yield retstr.getvalue()[:-1]
        retstr.reset()
        retstr.truncate()

def strip_re(input, re_obj, sub=None):
    output=""
    
    if type(re_obj) == type(""):
        re_obj = re.compile(re_obj)
    
    hcre = re_obj.search(input)
    while hcre:
        if sub:
            output += input[:hcre.start()] + sub
        else:
            output += input[:hcre.start()] + "".join(hcre.groups())
        input = input[hcre.end():]
        hcre = re_obj.search(input)
    output += input
    return output

def runtest():
    assert "accacaccca" == strip_re("abbababbba", "b", "c"), strip_re("abbababbba", "b", "c")
    assert "aaaa" == strip_re("abbababbba", "b"), strip_re("abbababbba", "b")
    assert "aaaa" == strip_re("abbaabbba", "b"), strip_re("abbaabbba", "b")
    
    assert "biographical  data" == strip_re("""biographi-
cal  data""", "(\w+)-\s+(\w)"), strip_re("""biographi-
cal  data""", "(\w+)-\s+(\w)")
    exit()
        
ADMINISTRATION_DATE_RANGE = re.compile(r"((JANUARY|MARCH|APRIL|MAY) \d+, \d{4},\s+TO\s+(JANUARY|MARCH|APRIL|MAY) \d+, \d{4})")
PRESIDENTIAL_ADMINISTRATION = re.compile(r"^(First|Second|Third|Fourth)??\s*Administration of (\w+\s+(\w+\.?\s+)??\w+(, JR\.)??)$",re.M)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("pdffile")
    parser.add_argument("--txtfile")
    parser.add_argument("--pages", type=int, default=0xffffffff)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        runtest()
    
    if args.txtfile:
        stream = open(args.txtfile, 'w')
    else:
        stream = sys.stdout
    
    x = 0
    for data in pdfparser_page(args.pdffile):
        if x < args.pages:
            stream.write("**[PAGE {:04d}]**\n".format(x))
            
            # This is pure data cleanup
            for remove, replace in ( ["(\w+)-\s+(\w)", None],
                            ["( ) +", None],
                            ["\s(\s)", None],
                            ):
                data = strip_re(data, remove, replace)
            
            if ADMINISTRATION_DATE_RANGE.search(data):
                print ADMINISTRATION_DATE_RANGE.search(data).group(0)
            if PRESIDENTIAL_ADMINISTRATION.search(data):
                print PRESIDENTIAL_ADMINISTRATION.search(data).group(0)
                print PRESIDENTIAL_ADMINISTRATION.search(data).group(2)
            
            
            
            stream.write(data)
            stream.write("-"*125 + "\n")
            stream.flush()
        else:
            break
        x += 1
    if args.txtfile:
        stream.close()
