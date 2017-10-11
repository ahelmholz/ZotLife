import sys
import requests

url = sys.argv[1]
a = requests.get(url)
b = a.text
c = b[b.index("Major Requirements"):b.index("Sample Program")]
#print(c)
d = c.splitlines()
for line in d:
    if "<a href" in line:
        href_start = line.index('href') + 6
        print(line[href_start:])
        #href_end = line[href_start:].index('"')
        #href = line[href_start:href_end]
        #print(href)
