import urllib2, re, json, os.path, smtplib

data={}
if os.path.isfile('stock.dat'):
    with open('stock.dat','r') as f:
        data = json.load(f)

class load:
    def __init__(self):
        self.date=0
        
    def parse(self):
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
    def alert_price(self,parameters):
        self.parameters=parameters
        sender = 'mmm@seznam.cz'
        receivers = ['rrr@gmail.com']
        cc=[]
        counter=0
        subject="Stock.py allert"
        header  = 'From: %s\n' % sender
        header += 'To: %s\n' % ','.join(receivers)
        header += 'Cc: %s\n' % ','.join(cc)
        header += 'Subject: %s\n\n' % subject
        message = ""
        for parameter in self.parameters:
            if parameter[1]< data[self.date]["currency"][parameter[0]][0]:
                message +='The exchange rate for 1 %s is %s CZK and this is higher than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["currency"][parameter[0]][0],parameter[1])
                counter+=1
        if counter>0:
            message = header + message

            try:
                smtpObj = smtplib.SMTP('192.168.3.1',25)
                smtpObj.sendmail(sender, receivers, message)
                print "Successfully sent email"
            except:
                print "Error: unable to send email"
    
parameters=[("EUR",2.5),("USD",30.7),("GBP",25.6),("JPY",11.4)]
x=load()
x.parse()



print data
x.alert_price(parameters)
with open('stock.dat','w') as f:
    json.dump(data, f)
