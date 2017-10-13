import sys
import requests
import time

# TODO: split on OR/AND and organize....
# TODO: handle course ranges...(That's not irratating at all.)
class ParsedCourse:
    # will parse text accordingly
    def __init__(self, course_name, course_text, course_url):
        self.course_name = course_name
        self.course_text = course_text
        self.course_url = course_url
        self.course_prereqs = []
        self.course_coreqs = []
        self.course_restrictions = ''
        self.course_units = None # check for None
        self.special = [] # to be written to file as comments for manual resolution (1 entry == 1 line)
        self.parse_course_text()

    def parse_course_text(self):
        search_base_url = 'http://catalogue.uci.edu/' # TODO move to make accessible
        #print("\n*****************************************************************************")
        #print(self.course_url + "\n")
        #print(self.course_text)
        temp_text = self.course_text # in case I modify the text
        if 'Units' in temp_text:
            # assumes unit is a single digit with a space before 'Units'
            if temp_text[temp_text.index('Units') - 2].isdigit():
                self.course_units = temp_text[temp_text.index('Units') - 2]
                #print(self.course_units)
            else:
                print("Units not found in {}".format(course.course_name))
        else:
            print("Units not found in {}".format(course.course_name))
        if 'coreq' in temp_text.lower():
            coreq_text1 = temp_text[temp_text.index("oreq"):] # c left off because of inconsistent capitalization
            coreq_text2 = coreq_text1[:coreq_text1.index('</p>')]
            #print(coreq_text2) # TODO: handle
        if 'prereq' in temp_text.lower():
            prereq_text1 = temp_text[temp_text.index("rerequisite"):]
            prereq_text2 = prereq_text1[:prereq_text1.index('</p>')]
            #print(prereq_text2)
            if 'or' in prereq_text2:
                split_on_or = prereq_text2.split(' or ')# must have spaces
                for x in split_on_or:
                    if '/search/?P=' in x:
                        temp_text2 = x[x.index('/search/?P=') + 11:]
                        temp_text3 = temp_text2[:temp_text2.index('"')] # temp_text3 is also course name
                        # TODO: construct search url, make call and add to dict
                        # url looks something like temp_url = "\\ ".join((search_base_url + above_token + tt3).split())
                        #print(temp_text3)
                    else:
                        # TODO: handle 'better' and 'with a grade of C'
                        # add all others to special
                        pass

            else:
                pass
                # TODO handle by adding to special
        if 'restriction' in temp_text.lower():
            res_text1 = temp_text[temp_text.index("Restriction"):]
            res_text2 = res_text1[:res_text1.index('</p>')]
            #print(res_text2) # TODO: handle by adding to special

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

                    # TODO: put in def
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
                    # END PUT IN DEF
                    # TODO share parsed_course_dict among defs
                    # TODO: loop through all, build trees, report missing info for manual review, get units, put into nice output file

    #for k, v in parsed_course_dict.items():
        #print(k)
        #[print("\t {}".format(i)) for i in v.course_text.splitlines()]
    print("Length of parsed_course_dict: {}".format(len(parsed_course_dict)))
    print("Time taken: {}".format(time.time() - start_time))
    #print(count)

if __name__=='__main__':
    main()
