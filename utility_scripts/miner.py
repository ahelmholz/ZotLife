import sys
import requests

url = "http://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/#majorstext"
search_base_url = 'http://catalogue.uci.edu/'
a = requests.get(url)
b = a.text
c = b[b.index("Requirements for the B.S. in Computer Science"):b.index("Sample Program")] # Begin and end of first cut
#print(c)
c = c[c.index("University Requirements</a></strong>.</h6>"):]
d = c.splitlines()
count = 0
for line in d:
    if "<a href" in line:
        e = line.split("<a href=")
        for f in e:
            if '" title' in f:
                end_of_url = f[:f.index('" title')][1:]
                g = f[f.index('" title'):]
                course_name = g[g.index('="') + 2: g.index('" class=')]
                #print(course_name)
                print(end_of_url)
                count +=1
                temp_url = "\\ ".join((search_base_url + end_of_url).split())

                print(temp_url)
                h = requests.get(temp_url).text
                find = '<div class="searchresult"><h2>' + course_name
                if find in h:
                    i = h[h.index(find) + 27:] # +27 just to invalidate search string so I can end find
                    j = i.splitlines()
                    for line in j:
                        if '<div class="searchresult"><h2>' in line:
                            break
                        print(line)
                exit()
                # TODO: loop through all, build trees, report missing info for manual review, get units, put into nice output file
                # TODO: actually parse info
        #count += 1

#print(count)