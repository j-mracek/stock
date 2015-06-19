import urllib2, re, json, os.path, smtplib, time

data={}
currency=["EUR","USD","GBP","JPY"]
paramet_curr=[("EUR",2.5,"<"),("USD",30.7,">"),("GBP",25.6,"<"),("JPY",11.4,"<")]
paramet_stock=[("BOREALIS",2.5,"<"),("CETIN",30.7,">")]
stock_set=[('BOREALIS', 'GI000A1J9JJ0'), ('CETIN', 'CZ0009000089'), ('CETV', 'BMG200452024'), ('CEZ', 'CZ0005112300'), ('E4U', 'CZ0005123620'), ('ENERGOAQUA', 'CS0008419750'), ('ENERGOCHEMICA', 'CZ0008467818'), ('ERSTE GROUP BANK', 'AT0000652011'), ('FORTUNA', 'NL0009604859'), ('JACHYMOV PM', 'CS0008446753'), ('KOMERCNI BANKA', 'CZ0008019106'), ('NWR', 'GB00B42CTW68'), ('O2 C.R.', 'CZ0009093209'), ('PEGAS NONWOVENS', 'LU0275164910'), ('PHILIP MORRIS CR', 'CS0008418869'), ('PLG', 'CZ0005124420'), ('PRAZSKE SLUZBY', 'CZ0009055158'), ('RMS MEZZANINE', 'CS0008416251'), ('STOCK', 'GB00BF5SDZ96'), ('TMR', 'SK1120010287'), ('TOMA', 'CZ0005088559'), ('UNIPETROL', 'CZ0009091500'), ('VGP', 'BE0003878957'), ('VIG', 'AT0000908504')]

if os.path.isfile('stock.dat'):
    with open('stock.dat','r') as f:
        data = json.load(f)

class load:
    def __init__(self,currency):
        self.currency=currency
        self.date=0
        self.message = ""
        self.counter=0
    def search_curr(self):
        kurzy = urllib2.urlopen("http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp")
        for line in kurzy:
            m=re.search("Platnost pro (\d{2})[.](\d{2})[.](\d{4})",line)
            if m:
                self.date="%s-%s-%s" % (m.group(3),m.group(2),m.group(1))          
            for cur in self.currency:
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
                self.counter+=1
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
                print "Incorrect character in paramet_curr or the page http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp failed to open."
        
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

class stocks:
    def __init__(self,stock):
        self.stock=stock
        self.date=0
        self.message = ""
        self.counter=0
    def search_stock(self):
        kurzy = urllib2.urlopen("https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english")
        for line in kurzy:
            m=re.search('value="(\d{1,2})/(\d{1,2})/(\d{4})"',line)
            if m:
                self.date="%s-%s-%s" % (m.group(3),m.group(1).zfill(2),m.group(2).zfill(2))
            for sh in self.stock:
                    string='</td><td>%s</td><td class="num">(\d*)[,]?(\d{1,3}[.]\d{2})</td><td class="center">CZK</td><td class="num \w+">-?\w+[.]\d{2}</td><td class="num">(\d*)[,]?(\d*)[,]?(\d+)<' % (sh[1])
                    m = re.search(string, line)
                    if m:
                        data.setdefault(self.date,{}).setdefault("stock",{}).setdefault(sh[0],["",""])[0]=(float("%s%s" % (m.group(1),m.group(2))))
                        data.setdefault(self.date,{}).setdefault("stock",{}).setdefault(sh[0],["",""])[1]=(int("%s%s%s" % (m.group(3),m.group(4),m.group(5))))
        kurzy.close()
    def parse_stock(self):
        try:
            self.search_stock()
        except:
            time.sleep(5)
            try:
               self.search_stock()
            except:
                self.message +='The page https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english failed to open.\n'  
                self.counter +=1

    def alert_price_stock(self,parameters):
        self.parameters=parameters      
        for parameter in self.parameters:
            try:
                if parameter[2] is "<":
                    if parameter[1]< data[self.date]["stock"][parameter[0]][0]:
                        self.message +='The share price of  %s is %s CZK and this is higher than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["stock"][parameter[0]][0],parameter[1])
                        self.counter+=1
                elif parameter[2] is ">":   
                    if parameter[1]> data[self.date]["stock"][parameter[0]][0]:
                        self.message +='The share price of %s is %s CZK and this is lower than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["stock"][parameter[0]][0],parameter[1])
                        self.counter+=1
            except:
                print "Incorrect character in paramet_stock or the page https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english failed to open."


x=load(currency)
x.parse_curr()
x.alert_price(paramet_curr)
#x.messenger()
print x.message
y=stocks(stock_set)

y.parse_stock()
y.alert_price_stock(paramet_stock)
print y.message
print data
with open('stock.dat','w') as f:
    json.dump(data, f)
