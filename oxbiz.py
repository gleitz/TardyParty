import difflib
import re
import time
import urllib2
import xml.etree.cElementTree as ET

from datetime import datetime, timedelta

GOOGLE_TIME = '%a, %d %b %Y %H:%M:%S UT'
XML_FETCHER_URL = 'http://localhost/GoogleGroups2Rss/index.php?group=oxidized-bismuth-blogger'

result = urllib2.urlopen(XML_FETCHER_URL).read()
time.sleep(1)
tree = ET.ElementTree(file='/tmp/text.xml')

people = ['Andrew Van Dam', 'Chris Maury', 'Evan Burchard', 'Benjamin Gleitzman', 'Jam Kotenko', 'Jason Kotenko', 'Kendall Webster', 'Nicole', 'Parker Higgins', 'Rich Jones', 'Zachary Adam Ozer']

now = datetime.now()
monday = now - timedelta(days=now.weekday())
last_monday = monday - timedelta(days=7)

people_who_wrote = {}

items = tree.getroot()[0][4:] # start of messages
name_re = re.compile("\((.*)\)") # match name inside parens
for item in items:
    item_pubdate = datetime.strptime(item[5].text.strip(), GOOGLE_TIME)
    if item_pubdate > last_monday and item_pubdate < monday:
        name = name_re.search(item[4].text.strip()).groups()[0]
        if name not in people_who_wrote:
            canonical_names = difflib.get_close_matches(name, people)
            if canonical_names:
                canonical_name = canonical_names[0]
                people.remove(canonical_name)

        info_dict = {'title': item[0].text.strip(),
                     'url': item[1].text.strip()}
        people_who_wrote.setdefault(name, []).append(info_dict)

print 'People who wrote are', ', '.join(people_who_wrote.keys())
print 'People who didn\'t write are', ', '.join(people)

