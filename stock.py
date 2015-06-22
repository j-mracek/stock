import urllib2, re, json, os.path, smtplib, time, ConfigParser, ast

data={}

Config = ConfigParser.ConfigParser()
Config.read("stock.ini")

sender = ast.literal_eval(Config.get("messenger", "sender"))
receivers=ast.literal_eval(Config.get("messenger", "receivers"))
cc=ast.literal_eval(Config.get("messenger", "cc"))
SMTP=ast.literal_eval(Config.get("messenger", "SMTP"))
currency=ast.literal_eval(Config.get("currency", "currency"))
paramet_curr=ast.literal_eval(Config.get("currency", "paramet_curr"))
#urlcurrencies=ast.literal_eval(Config.get("currency", "urlcurrencies"))
stock_set=ast.literal_eval(Config.get("stock", "stock_set"))
paramet_stock=ast.literal_eval(Config.get("stock", "paramet_stock"))
#urlstock=ast.literal_eval(Config.get("stock", "urlstock"))
xday=ast.literal_eval(Config.get("xdayaverage", "xday"))

urlstock1=ast.literal_eval(Config.get("stock", "urlstock1"))
urlcurrencies1=ast.literal_eval(Config.get("currency", "urlcurrencies1"))

#currency=["EUR","USD","GBP","JPY"]
#paramet_curr=[("EUR",2.5,"<"),("USD",30.7,">"),("GBP",25.6,"<"),("JPY",11.4,"<")] # Set "<" to email receive if actual price is higher than set value.
#paramet_stock=[("BOREALIS",2.5,"<"),("CETIN",30.7,">")] # Set "<" to email receive if actual price is higher than set value.
#stock_set=[('BOREALIS', 'GI000A1J9JJ0'), ('CETIN', 'CZ0009000089'), ('CETV', 'BMG200452024'), ('CEZ', 'CZ0005112300'), ('E4U', 'CZ0005123620'), ('ENERGOAQUA', 'CS0008419750'), ('ENERGOCHEMICA', 'CZ0008467818'), ('ERSTE GROUP BANK', 'AT0000652011'), ('FORTUNA', 'NL0009604859'), ('JACHYMOV PM', 'CS0008446753'), ('KOMERCNI BANKA', 'CZ0008019106'), ('NWR', 'GB00B42CTW68'), ('O2 C.R.', 'CZ0009093209'), ('PEGAS NONWOVENS', 'LU0275164910'), ('PHILIP MORRIS CR', 'CS0008418869'), ('PLG', 'CZ0005124420'), ('PRAZSKE SLUZBY', 'CZ0009055158'), ('RMS MEZZANINE', 'CS0008416251'), ('STOCK', 'GB00BF5SDZ96'), ('TMR', 'SK1120010287'), ('TOMA', 'CZ0005088559'), ('UNIPETROL', 'CZ0009091500'), ('VGP', 'BE0003878957'), ('VIG', 'AT0000908504')]
#urlcurrencies="http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp"
urlcurrencies="http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp?date=18.06.2015"
#urlstock="https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english"
urlstock="https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?date=6/18/2015"
#xday=7
#sender = 'mmm@seznam.cz'
#receivers = ['rrr@gmail.com']
#cc=[]
#SMTP=['192.168.3.1',25]


if os.path.isfile('stock.dat'):
    with open('stock.dat','r') as f:
        data = json.load(f)

class analyser:
    message = "Dear user of stock.py,\n"
    message += "This is an automatic report from stock.py which would like to inform you that:\n" 
    counter=0
    def messenger(self):
        counter=0
        subject="Stock.py allert"
        header  = 'From: %s\n' % sender
        header += 'To: %s\n' % ','.join(receivers)
        header += 'Cc: %s\n' % ','.join(cc)
        header += 'Subject: %s\n\n' % subject
        if analyser.counter>0:
            message = header + analyser.message
            try:
                smtpObj = smtplib.SMTP(SMTP[0],SMTP[1])
                smtpObj.sendmail(sender, receivers, message)
                print "Successfully sent email"
            except:
                print "Error: unable to send email"
    def parse(self,run,arg):
        try:
            run(*arg)
        except:
            time.sleep(5)
            try:
                run(*arg)
            except:
                analyser.message +="The function %s%s didn't work properly, may be due to unable to open url. \n" % (run.__name__,arg) 
                analyser.counter +=1
    def prn_column(self,st,tr,x,curr):
        a=data[tr[x]]['stock'][st][0]
        b=data[tr[x-1]]['stock'][st][0]
        if curr is "CZK":
            return "%10.2f(%5.2f%%)" % (a,(1-b/a)*100)
        else:
            return "%10.3f(%5.2f%%)" % (a/(data[tr[x]]['currency'][curr][0]/data[tr[x]]['currency'][curr][1]),(1-(b/data[tr[x-1]]['currency'][curr][0])/(a/data[tr[x]]['currency'][curr][0]))*100)
    def try_f(self,x,*y):
        try:
            return x(*y)
        except:
            return "%18s" % "-- no data -- "
    def average(self,y,st,curr):
        tr=sorted(data.keys())
        aver=[]
        if curr is "CZK":
            for x in range(-y,0):
                try:
                    a=data[tr[x]]['stock'][st][0]
                    aver.append(float(a))
                except:
                    print "missing value"
            return "%1.2f" % (sum(aver)/len(aver))
        else:
            for x in range(-y,0):
                try:
                    a=data[tr[x]]['stock'][st][0]
                    aver.append(float(a/(data[tr[x]]['currency'][curr][0]/data[tr[x]]['currency'][curr][1])))
                except:
                    print "missing value"                   
            try:
                return "%1.3f" % (sum(aver)/len(aver))
            except:
                print "Function Average: No values to calculate"
    
    def trend(self,n):
        tr=sorted(data.keys())
        if len(tr) < 3:
            print "Function Trend: Not enough values to evaluate (min. 3)"
        else:
            for st in data[tr[-1]]['stock'].keys():                     
                if data[tr[-1]]['stock'][st][0] > data[tr[-2]]['stock'][st][0] > data[tr[-3]]['stock'][st][0]:
                    print "-----------------------------------  Share name: %-20s-----------------------------------" % st.center(20, ' ')
                    print "%14s%18s%18s%18s%18s%18s" % ("Date", "Price in CZK","Price in %s" % (currency[0]),"Price in %s" % (currency[1]),"Price in %s" % (currency[2]),"Price in %s" % (currency[3]))
                    if len(tr) < 8:
                        print "Function Trend: Not enough values to evaluate (min. 8)"
                    else:
                        for x in range(-7,0):
                            a=data[tr[x]]['stock'][st][0]
                            b=data[tr[x-1]]['stock'][st][0]
                            print "%14s:%15s%15s%15s%15s%15s" % (tr[x],g.try_f(g.prn_column,st,tr,x,"CZK"),g.try_f(g.prn_column,st,tr,x,currency[0]),g.try_f(g.prn_column,st,tr,x,currency[1]),g.try_f(g.prn_column,st,tr,x,currency[2]),g.try_f(g.prn_column,st,tr,x,currency[3]))
                        print "%s days average: %9s%18s%18s%18s%18s" % (n,self.average(n,st,"CZK"),self.average(n,st,currency[0]),self.average(n,st,currency[1]),self.average(n,st,currency[2]),self.average(n,st,currency[3]))

class currencies(analyser):
    def __init__(self,currency):
        self.currency=currency
        self.date=0
    def search_curr(self):
        kurzy = urllib2.urlopen(urlcurrencies)
        for line in kurzy:
            m=re.search("Platnost pro (\d{2})[.](\d{2})[.](\d{4})",line)
            if m:
                self.date="%s-%s-%s" % (m.group(3),m.group(2),m.group(1))          
            for cur in self.currency:
                s='>(\d+)</td><td>%s</td><td align="right">(\d+),(\d+)<' % (cur)
                m=re.search(s,line)
                if m:
                    data.setdefault(self.date,{}).setdefault("currency",{}).setdefault(cur,["",""])[0]=(float("%s.%s" % (m.group(2),m.group(3))))
                    data.setdefault(self.date,{}).setdefault("currency",{}).setdefault(cur,["",""])[1]=(int(m.group(1)))
        kurzy.close()
        
    def alert_price(self,parameters):
        self.parameters=parameters        
        if self.date is not 0:
            for parameter in self.parameters:
                if parameter[2] is "<":
                    if parameter[1]< data[self.date]["currency"][parameter[0]][0]:
                        analyser.message +='The exchange rate for %s %s is %s CZK and this is higher than set allert value (%s CZK).\n' % (data[self.date]["currency"][parameter[0]][1],parameter[0],data[self.date]["currency"][parameter[0]][0],parameter[1])
                        analyser.counter+=1
                elif parameter[2] is ">":   
                    if parameter[1]> data[self.date]["currency"][parameter[0]][0]:
                        analyser.message +='The exchange rate for %s %s is %s CZK and this is lower than set allert value (%s CZK).\n' % (data[self.date]["currency"][parameter[0]][1],parameter[0],data[self.date]["currency"][parameter[0]][0],parameter[1])
                        analyser.counter+=1
                else:
                    print "Incorrect character in paramet_stock in setting: (%s,%s,%s)" % (parameter[0],parameter[1],parameter[2])
        else:
            print "The page http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp failed to open."
        
class stocks(analyser):
    def __init__(self,stock):
        self.stock=stock
        self.date=0
    def search_stock(self):
        kurzy = urllib2.urlopen(urlstock)
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
    def alert_price_stock(self,parameters):
        self.parameters=parameters      
        if self.date is not 0:
            for parameter in self.parameters:
                if parameter[2] is "<":
                    if parameter[1]< data[self.date]["stock"][parameter[0]][0]:
                        analyser.message +='The share price of  %s is %s CZK and this is higher than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["stock"][parameter[0]][0],parameter[1])
                        analyser.counter+=1
                elif parameter[2] is ">":   
                    if parameter[1]> data[self.date]["stock"][parameter[0]][0]:
                        analyser.message +='The share price of %s is %s CZK and this is lower than set allert value (%s CZK).\n' % (parameter[0],data[self.date]["stock"][parameter[0]][0],parameter[1])
                        analyser.counter+=1
                else:
                    print "Incorrect character in paramet_stock in setting: (%s,%s,%s)" % (parameter[0],parameter[1],parameter[2])
        else:
             print "The page https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english failed to open."
            

x=currencies(currency)
g=analyser()
g.parse(x.search_curr,())
x.alert_price(paramet_curr)
y=stocks(stock_set)
g.parse(y.search_stock,())
y.alert_price_stock(paramet_stock)
g.trend(xday)
#x.messenger()
print analyser.message
print analyser.counter
for key in sorted(data.keys()):
    for val in data[key]["currency"].keys():
        print key,"currency",val,data[key]["currency"][val]
with open('stock.dat','w') as f:
    json.dump(data, f)
