import sys, argparse
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("pdffile")
    parser.add_argument("--txtfile")
    parser.add_argument("--pages", type=int, default=0xffffffff)
    args = parser.parse_args()
    
    if args.txtfile:
        stream = open(args.txtfile, 'w')
    else:
        stream = sys.stdout
    
    x = 0
    for data in pdfparser_page(args.pdffile):
        if x < args.pages:
            stream.write("**[PAGE {:04d}]**\n".format(x))
            stream.write(data)
            stream.write("-"*125 + "\n")
            stream.flush()
        else:
            break
        x += 1
    if args.txtfile:
        stream.close()
