import urllib2, re, json, os.path

data={}
if os.path.isfile('stock.dat'):
    with open('stock.dat','r') as f:
        data = json.load(f)
#data={}
#with open('file.dat','w') as f:
  #json.dump(data, f)
class load:
    def __init__(self):
        self.date=0
    def parse(self):
        kurzy = urllib2.urlopen("http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp")
        for line in kurzy:
            m=re.search("Platnost pro (\d{2})[.](\d{2})[.](\d{4})",line)
            if m:
                print "%s-%s-%s" % (m.group(3),m.group(2),m.group(1))
                self.date="%s-%s-%s" % (m.group(3),m.group(2),m.group(1))          
            a=["EUR","USD","GBP","JPY"]
            for cur in a:
                s='%s</td><td align="right">(\d+),(\d+)<' % (cur)
                m=re.search(s,line)
                if m:
                    print float("%s.%s" % (m.group(1),m.group(2)))
                    if float("%s.%s" % (m.group(1),m.group(2))) not in data.setdefault(self.date,{}).setdefault(cur,[]):
                        data.setdefault(self.date,{}).setdefault(cur,[]).append(float("%s.%s" % (m.group(1),m.group(2))))
        kurzy.close()        
x=load()
x.parse()
print data
with open('stock.dat','w') as f:
    json.dump(data, f)
#d=[]  
#kurzy = urllib2.urlopen("http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp")
#for line in kurzy:
#    a="Platnost pro (\d{2})[.](\d{2})[.](\d{4})"
#    m=re.search(a,line)
#    if m:
#        print "%s-%s-%s" % (m.group(3),m.group(2),m.group(1))
#        d="%s-%s-%s" % (m.group(3),m.group(2),m.group(1))
#        print d
#    m=re.search('EUR</td><td align="right">(\d+),(\d+)<',line)
#    if m:
#        print float("%s.%s" % (m.group(1),m.group(2)))
#
#        data.setdefault(d,{"EUR":[]})["EUR"].append(float("%s.%s" % (m.group(1),m.group(2))))
#    m=re.search('USD</td><td align="right">(\d+),(\d+)<',line)
#    if m:
#        a=float("%s.%s" % (m.group(1),m.group(2)))
#        print a
#    m=re.search('JPY</td><td align="right">(\d+),(\d+)<',line)
#    if m:
#        a=float("%s.%s" % (m.group(1),m.group(2)))
#        print a
#    m=re.search('GBP</td><td align="right">(\d+),(\d+)<',line)
#    if m:
#        a=float("%s.%s" % (m.group(1),m.group(2)))
#        print a
#kurzy.close()
#print data

#htmlSource = sock.read()
#sock.close()
#print htmlSource
#Platnost pro 12.06.2015
#(this, 27.3, 'rate_eur', 'cs')
#(this, 24.328, 'rate_usd', 'cs')
#(this, 37.675, 'rate_gbp', 'cs')
#USD</td><td align="right">24,328<        

