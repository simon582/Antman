import urllib2
from StringIO import StringIO
import zlib
 
page=1
url="http://auto.sina.com.cn/news/2014-12-05/14511366159.shtml"
request = urllib2.Request(url)
request.add_header('Accept-encoding', 'gzip')
opener = urllib2.build_opener()
response = opener.open(request)
html = response.read()
gzipped = response.headers.get('Content-Encoding')
if gzipped:
    html = zlib.decompress(html, 16+zlib.MAX_WBITS)
print html.decode('gbk','ignore')
