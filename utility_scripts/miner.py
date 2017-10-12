import sys
import requests
import time

class ParsedCourse:
    # will parse text accordingly
    def __init__(self, course_name, course_text, course_url):
        self.course_name = course_name
        self.course_text = course_text
        self.course_url = course_url
        # TODO parse text into fields here
        #self.course_units = course_units

def main():
    start_time = time.time()
    url = "http://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/#majorstext"
    search_base_url = 'http://catalogue.uci.edu/'
    a = requests.get(url)
    b = a.text
    c = b[b.index("Requirements for the B.S. in Computer Science"):b.index("Sample Program")] # Begin and end of first cut
    #print(c)
    c = c[c.index("University Requirements</a></strong>.</h6>"):]
    d = c.splitlines()
    parsed_course_dict = {}
    for line in d:
        if "<a href" in line:
            e = line.split("<a href=")
            for f in e:
                if '" title' in f:
                    end_of_url = f[:f.index('" title')][1:]
                    g = f[f.index('" title'):]
                    course_name = g[g.index('="') + 2: g.index('" class=')]
                    #print(course_name)
                    #print(end_of_url)
                    temp_url = "\\ ".join((search_base_url + end_of_url).split())

                    #print(temp_url)
                    h = requests.get(temp_url).text
                    find = '<div class="searchresult"><h2>' + course_name
                    if find in h:
                        i = h[h.index(find) + 27:] # +27 just to invalidate search string so I can end find
                        j = i.splitlines()
                        course_text = ''
                        for line in j:
                            if '<div class="searchresult"><h2>' in line:
                                line2 = line[:line.index('<div class="searchresult"><h2>')]
                                course_text += line2
                                break
                            if '</div><!--end #textcontainer -->' in line:
                                line3 = line[:line.index('</div><!--end #textcontainer -->')]
                                course_text += line3
                                break
                            course_text += '\n' + line
                        #[print(i) for i in course_text.splitlines()]
                        parsed_course_dict[course_name] = ParsedCourse(course_name, course_text, temp_url)
                    else:
                        print("Unable to locate info for {} at url {}".format(course_name, temp_url))
                    # TODO: loop through all, build trees, report missing info for manual review, get units, put into nice output file
                    # TODO: actually parse info

    #for k, v in parsed_course_dict.items():
        #print(k)
        #[print("\t {}".format(i)) for i in v.course_text.splitlines()]
    print("Length of parsed_course_dict: {}".format(len(parsed_course_dict)))
    print("Time taken: {}".format(time.time() - start_time))
    #print(count)

if __name__=='__main__':
    main()