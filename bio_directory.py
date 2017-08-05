# -*- coding: utf-8 -*-
import sys, argparse, re, json
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
        
ADMINISTRATION_DATE_RANGE = re.compile(r"((JANUARY|MARCH|APRIL|MAY|JULY|AUGUST|SEPTEMBER|NOVEMBER) \d+, \d{4},\s+TO\s+(JANUARY|MARCH|APRIL|MAY|JULY|AUGUST|SEPTEMBER|NOVEMBER) \d+, \d{4})")
PRESIDENTIAL_ADMINISTRATION = re.compile(r"^(First|Second|Third|Fourth)??\s*Administration of (\w+\s+(\w+\.?\s+)??(\w+\.?\s+)??\w+(, JR\.)??)$",re.M)

Presidential_Administrations = []

def Process_Presidential_Administration(data):
    extracted = False
    if PRESIDENTIAL_ADMINISTRATION.search(data):
        administration_dict = {}
        extracted = True
        administration_desc = PRESIDENTIAL_ADMINISTRATION.search(data).group(0)
        president = PRESIDENTIAL_ADMINISTRATION.search(data).group(2)
        
        data = data[PRESIDENTIAL_ADMINISTRATION.search(data).end():]
        administration_dict["type"]         = "presidential_administration"
        administration_dict["description"]  = administration_desc.strip()
        administration_dict["president"]    = president.strip()

        if ADMINISTRATION_DATE_RANGE.search(data):
            date_range = ADMINISTRATION_DATE_RANGE.search(data).group(0)
            data = data[ADMINISTRATION_DATE_RANGE.search(data).end():]
            print date_range
            administration_dict["dates"]    = date_range
            jsonstream.flush()
        
        if PRESIDENTIAL_ADMINISTRATION.search(data):
            administration_body = data[:PRESIDENTIAL_ADMINISTRATION.search(data).start()]
        else:
            administration_body = data
        if administration_body:
            administration_dict["body"]     = administration_body.strip()
        jsonstream.write(json.dumps(administration_dict))
        jsonstream.write('\n')
        jsonstream.flush()
        
        Presidential_Administrations.append( administration_dict )
        
    return data, extracted

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("pdffile")
    parser.add_argument("--txtfile")
    parser.add_argument("--jsonfile")
    parser.add_argument("--pages", type=int, default=0xffffffff)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        runtest()
    
    if args.txtfile:
        stream = open(args.txtfile, 'w')
    else:
        stream = sys.stdout
        
    if args.jsonfile:
        jsonstream = open(args.jsonfile, 'w')
    else:
        jsonstream = sys.stdout
    
    x = 0
    for data in pdfparser_page(args.pdffile):
        extracted = True
        if x < args.pages:
            stream.write("**[PAGE {:04d}]**\n".format(x))
            
            # This is pure data cleanup
            for remove, replace in ( ["(\w+)-\s+(\w)", None],
                            ["( ) +", None],
                            ["\s(\s)", None],
                            ["—", "-"]
                            ):
                data = strip_re(data, remove, replace)
            
            while data and extracted:
                data, extracted = Process_Presidential_Administration(data)            
            
            stream.write(data)
            stream.write("-"*125 + "\n")
            stream.flush()
        else:
            break
        x += 1
    if args.txtfile:
        stream.close()
