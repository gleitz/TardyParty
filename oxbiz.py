import os
import difflib
import re
import time
import urllib2
import xml.etree.cElementTree as ET

from datetime import datetime, timedelta

GOOGLE_TIME = '%a, %d %b %Y %H:%M:%S UTC'
XML_FETCHER_URL = 'http://localhost:9001/GoogleGroups2Rss/index.php?group=oxidized-bismuth-blogger'

result = urllib2.urlopen(XML_FETCHER_URL).read()
time.sleep(1)
tree = ET.ElementTree(file='/tmp/text.xml')

people = ['David Brodsky', 'Jorin Vogel', 'savannahjune', 'Nicole Ricasata', 'Chris Ballinger', 'Chris Maury', 'Evan Burchard', 'Jan-Christoph Borchardt', 'Jam Kotenko', 'Jason Kotenko', 'Kendall Webster', 'Matt Gattis', 'Rich Jones', 'Benjamin Gleitzman', 'Geoff', 'Parker Phinney', 'Chris Christakis', 'Dmitri Sullivan', 'Janet Li']

now = datetime.now()
monday = now - timedelta(days=(now.weekday() - 1))
last_monday = monday - timedelta(days=8)

people_who_wrote = {}

items = tree.getroot()[0][4:] # start of messages
name_re = re.compile("\((.*)\)") # match name inside parens
for item in items:
    item_pubdate = datetime.strptime(item[5].text.strip(), GOOGLE_TIME)
    if item_pubdate > last_monday and item_pubdate < monday:
        if 'Re:' in item[0].text.strip():
            continue
        clean_name = item[4].text.strip()
        if '(' not in clean_name:
            continue
        name = name_re.search(clean_name).groups()[0]
        if name not in people_who_wrote:
            canonical_names = difflib.get_close_matches(name, people)
            if canonical_names:
                canonical_name = canonical_names[0]
                people.remove(canonical_name)
        info_dict = {'title': item[0].text.strip(),
                     'url': item[1].text.strip()}
        people_who_wrote.setdefault(name, []).append(info_dict)

EMAIL_FORM = u'''
<p>My dearest idea generator,</p>

<p>Here are the standings for the week of {0}. As a reminder, everyone is obliged to post at least one idea before 4:20 AM Monday morning.</p>

<p>This week's most excellent oxbiz bloggers:</p>

<p>{1}</p>

<p>People who need a little motivation:</p>

<p>{2}</p>

<p>Yours,<br/>
Benjamin</p>
'''

last_monday_str = datetime.strftime(last_monday, '%m/%d')

winner_list = []
for name, p in people_who_wrote.items():
    p = p[0]
    winner_list.append(u'<li><img src="https://mail.google.com/mail/e/B60" goomoji="B60" style="margin:0px 0.2ex;vertical-align:middle"> <a href="{0}">{2}</a> - {1}</li>'.format(p['url'], name, p['title']))

loser_list = []
for loser in people:
    loser_list.append('<li><img src="https://mail.google.com/mail/e/1E3" style="margin:0px 0.2ex;vertical-align:middle" goomoji="1E3"> <a href="{}">{}</a></li>'.format('https://dl.dropbox.com/u/101688/website/mp3/sad.mp3', loser))

winners = '<ul>' + '\n'.join(winner_list) + '</ul>'
losers = '<ul>' + '\n'.join(loser_list) + '</ul>'
email_str = EMAIL_FORM.format(last_monday_str, winners, losers)

f = open('/tmp/oxbiz.html', 'w')
email_str = email_str.encode('utf-8')
f.write(email_str)
f.close()

os.system('open /tmp/oxbiz.html')

print email_str
# print 'People who wrote are', ', '.join(people_who_wrote.keys())
# print 'People who didn\'t write are', ', '.join(people)
