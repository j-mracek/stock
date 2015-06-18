import urllib2, re, json, os.path, smtplib, time

data={}
parameters=[("EUR",2.5,"<"),("USD",30.7,">"),("GBP",25.6,"<"),("JPY",11.4,"<")]

if os.path.isfile('stock.dat'):
    with open('stock.dat','r') as f:
        data = json.load(f)

class load:
    def __init__(self):
        self.date=0
        self.message = ""
        self.counter=0
    def search_curr(self):
        kurzy = urllib2.urlopen("http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp")
        for line in kurzy:
            m=re.search("Platnost pro (\d{2})[.](\d{2})[.](\d{4})",line)
            if m:
                self.date="%s-%s-%s" % (m.group(3),m.group(2),m.group(1))          
            a=["EUR","USD","GBP","JPY"]
            for cur in a:
                s='%s</td><td align="right">(\d+),(\d+)<' % (cur)
                m=re.search(s,line)
                if m:
                    if float("%s.%s" % (m.group(1),m.group(2))) not in data.setdefault(self.date,{}).setdefault("currency",{}).setdefault(cur,[]):
                        data.setdefault(self.date,{}).setdefault("currency",{}).setdefault(cur,[]).append(float("%s.%s" % (m.group(1),m.group(2))))
        kurzy.close()
    def parse_curr(self):
        try:
            self.search_curr()
        except:
            time.sleep(120)
            try:
               self.search_curr()
            except:
                self.message +='The page http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp failed to open.\n'
    def alert_price(self,parameters):
        self.parameters=parameters
        
        for parameter in self.parameters:
            try:
                if parameter[2] is "<":
                    if parameter[1]< data[self.date]["currency"][parameter[0]][0]:
                        self.message +='The exchange rate for 1 %s is %s CZK and this is higher than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["currency"][parameter[0]][0],parameter[1])
                        self.counter+=1
                elif parameter[2] is ">":   
                    if parameter[1]> data[self.date]["currency"][parameter[0]][0]:
                        self.message +='The exchange rate for 1 %s is %s CZK and this is lower than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["currency"][parameter[0]][0],parameter[1])
                        self.counter+=1
            except:
                return "hallo"
        
    def messenger(self):
        sender = 'mmm@seznam.cz'
        receivers = ['rrr@gmail.com']
        cc=[]
        counter=0
        subject="Stock.py allert"
        header  = 'From: %s\n' % sender
        header += 'To: %s\n' % ','.join(receivers)
        header += 'Cc: %s\n' % ','.join(cc)
        header += 'Subject: %s\n\n' % subject
        if self.counter>0:
            message = header + self.message
            try:
                smtpObj = smtplib.SMTP('192.168.3.1',25)
                smtpObj.sendmail(sender, receivers, self.message)
                print "Successfully sent email"
            except:
                print "Error: unable to send email"

x=load()
x.parse_curr()
print data
x.alert_price(parameters)
#x.messenger()
#print x.counter

with open('stock.dat','w') as f:
    json.dump(data, f)
