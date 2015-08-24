#!/usr/bin/env python
import urllib2
import re
import json
import os.path
import smtplib
import time
import ConfigParser
import ast
import datetime


class Analyser:
    message = "Dear user of stock.py,\n"
    message += "This is an automatic report from stock.py which would like to inform you that:\n" 
    counter = 0

    def messenger(self):
        subject = "Stock.py alert"
        header = 'From: %s\n' % sender
        header += 'To: %s\n' % ','.join(receivers)
        header += 'Cc: %s\n' % ','.join(cc)
        header += 'Subject: %s\n\n' % subject
        if Analyser.counter > 0:
            message = header + Analyser.message
            try:
                smtp_obj = smtplib.SMTP(smtp[0], smtp[1])
                smtp_obj.sendmail(sender, receivers, message)
                print "Successfully sent email"
            except smtplib.SMTPException, error_message:
                print "Error: unable to send email due to %s" % error_message
            except StandardError, error_message:
                print "Unexpected error in function messenger: %s" % error_message

    def data_autoloader(self):
        fromdate = Config.get("data_autoloader", "fromdate")
        todate = Config.get("data_autoloader", "todate")
        first_day = datetime.datetime.strptime(fromdate, "%Y-%m-%d")
        stop_day = datetime.datetime.strptime(todate, "%Y-%m-%d")
        last_day = stop_day
        urlstock_a = Config.get("data_autoloader", "urlstock1")
        urlcurrencies_a = Config.get("data_autoloader", "urlcurrencies1")
        while first_day <= last_day:
            urlstock_b = (str(urlstock_a)+last_day.strftime("%-m/%-d/%Y"))
            urlcurr = (str(urlcurrencies_a)+last_day.strftime("%d.%m.%Y"))
            g.parse(x.search_curr, urlcurr)
            g.parse(y.search_stock, urlstock_b)
            print last_day
            last_day -= datetime.timedelta(days=1)
            
    def parse(self, function, *arguments):
        try:
            function(*arguments)
        except:
            time.sleep(5)
            try:
                function(*arguments)
            except urllib2.HTTPError, error_message:
                print "The function %s %s didn't work properly, may be due %s." % (function.__name__,
                                                                                   arguments,
                                                                                   error_message)
                Analyser.message += "The function %s %s didn't work properly, may be due %s. \n" % (function.__name__,
                                                                                                    arguments,
                                                                                                    error_message)
                Analyser.counter += 1
            except urllib2.URLError, error_message:
                print "The function %s %s didn't work properly, may be due %s." % (function.__name__,
                                                                                   arguments,
                                                                                   error_message)
                Analyser.message += "The function %s %s didn't work properly, may be due %s. \n" % (function.__name__,
                                                                                                    arguments,
                                                                                                    error_message)
                Analyser.counter += 1

    def prn_column(self, stockname, datakeys, x, curr):
        price = data[datakeys[x]]['stock'][stockname][0]
        price_old = data[datakeys[x-1]]['stock'][stockname][0]
        if curr == "CZK":
            return "%10.2f(%5.2f%%)" % (price, (1-price_old/price)*100)
        else:
            price_curr = data[datakeys[x]]['currency'][curr][0]
            price_curr_old = data[datakeys[x-1]]['currency'][curr][0]
            curr_unit = data[datakeys[x]]['currency'][curr][1]
            price_diff = (1-(price_old/price_curr_old)/(price/price_curr))*100
            return "%10.3f(%5.2f%%)" % (price/(price_curr/curr_unit), price_diff)

    def try_f(self, function, *arguments):
        try:
            return function(*arguments)
        except IndexError:
            return "%18s" % "-- no data -- "

    def average(self, xday, stockname, curr):
        data_keys = sorted(data.keys())
        calc_aver_price = []
        if curr == "CZK":
            for day in range(-xday, 0):
                try:
                    stock_price = data[data_keys[day]]['stock'][stockname][0]
                    calc_aver_price.append(float(stock_price))
                except IndexError, error_message:
                    print "missing value: %s" % error_message
            return "%1.2f" % (sum(calc_aver_price)/len(calc_aver_price))
        else:
            for day in range(-xday, 0):
                try:
                    stock_price = data[data_keys[day]]['stock'][stockname][0]
                    curr_price = (data[data_keys[day]]['currency'][curr][0]/data[data_keys[day]]['currency'][curr][1])
                    calc_aver_price.append(float(stock_price/curr_price))
                except IndexError, error_message:
                    print "missing value: %s" % error_message
            try:
                return "%1.3f" % (sum(calc_aver_price)/len(calc_aver_price))
            except ZeroDivisionError:
                return "-- no data --"
    
    def trend(self, period):
        data_keys = sorted(data.keys())
        if len(data_keys) < 3:
            Analyser.message += "Function Trend: Not enough values to evaluate (min. 3) \n"
            Analyser.counter += 1
        else:
            for stock_name in data[data_keys[-1]]['stock'].keys():
                if data[data_keys[-1]]['stock'][stock_name][0] > \
                        data[data_keys[-2]]['stock'][stock_name][0] > \
                        data[data_keys[-3]]['stock'][stock_name][0]:
                    Analyser.message += "\n%s  Share name: %-20s%s\n" % ((35*"-"), stock_name.center(20, ' '), (35*"-"))
                    Analyser.counter += 1
                    Analyser.message += "%14s%18s%18s%18s%18s%18s\n" % ("Date",
                                                                        "Price in CZK",
                                                                        "Price in %s" % (currency[0]),
                                                                        "Price in %s" % (currency[1]),
                                                                        "Price in %s" % (currency[2]),
                                                                        "Price in %s" % (currency[3]))
                    if len(data_keys) < 8:
                        Analyser.message += "Function Trend: Not enough values to evaluate (min. 8)\n"
                    else:
                        for x in range(-7, 0):
                            Analyser.message += "%14s:%15s%15s%15s%15s%15s\n" % \
                                                (data_keys[x],
                                                 g.try_f(g.prn_column, stock_name, data_keys, x, "CZK"),
                                                 g.try_f(g.prn_column, stock_name, data_keys, x, currency[0]),
                                                 g.try_f(g.prn_column, stock_name, data_keys, x, currency[1]),
                                                 g.try_f(g.prn_column, stock_name, data_keys, x, currency[2]),
                                                 g.try_f(g.prn_column, stock_name, data_keys, x, currency[3]))
                        Analyser.message += "%s days average: %9s%18s%18s%18s%18s\n" % \
                                            (period,
                                             self.average(period, stock_name, "CZK"),
                                             self.average(period, stock_name, currency[0]),
                                             self.average(period, stock_name, currency[1]),
                                             self.average(period, stock_name, currency[2]),
                                             self.average(period, stock_name, currency[3]))


class Currencies(Analyser):
    def __init__(self, currency):
        self.currency = currency
        self.date = 0

    def search_curr(self, urlcurr):
        kurzy = urllib2.urlopen(urlcurr, timeout=5)
        for line in kurzy:
            m = re.search("Platnost pro (\d{2})[.](\d{2})[.](\d{4})", line)
            if m:
                self.date = "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
            for cur in self.currency:
                s = '>(\d+)</td><td>%s</td><td align="right">(\d+),(\d+)<' % cur
                m = re.search(s, line)
                if m:
                    data.setdefault(self.date, {}).setdefault("currency", {}).setdefault(cur, ["", ""])[0] = \
                        (float("%s.%s" % (m.group(2), m.group(3))))
                    data.setdefault(self.date, {}).setdefault("currency", {}).setdefault(cur, ["", ""])[1] = \
                        (int(m.group(1)))
        kurzy.close()
        
    def alert_price(self, parameters):
        self.parameters = parameters
        if self.date != 0:
            for parameter in self.parameters:
                if parameter[2] == "<":
                    if parameter[1] < data[self.date]["currency"][parameter[0]][0]:
                        Analyser.message += 'The exchange rate for %s %s is %s CZK' \
                                            ' and this is higher than set allert ' \
                                            'value (%s CZK).\n' % (data[self.date]["currency"][parameter[0]][1],
                                                                   parameter[0],
                                                                   data[self.date]["currency"][parameter[0]][0],
                                                                   parameter[1])
                        Analyser.counter += 1
                elif parameter[2] == ">":
                    if parameter[1] > data[self.date]["currency"][parameter[0]][0]:
                        Analyser.message += 'The exchange rate for %s %s is %s CZK' \
                                            ' and this is lower than set allert' \
                                            ' value (%s CZK).\n' % (data[self.date]["currency"][parameter[0]][1],
                                                                    parameter[0],
                                                                    data[self.date]["currency"][parameter[0]][0],
                                                                    parameter[1])
                        Analyser.counter += 1
                else:
                    print "Incorrect character in paramet_stock in setting: (%s,%s,%s)" % (parameter[0],
                                                                                           parameter[1],
                                                                                           parameter[2])
        else:
            print "The page http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp" \
                  " failed to open."


class Stocks(Analyser):
    def __init__(self, stock):
        self.stock = stock
        self.date = 0

    def search_stock(self, urlst):
        kurzy = urllib2.urlopen(urlst, timeout=5)
        for line in kurzy:
            m = re.search('value="(\d{1,2})/(\d{1,2})/(\d{4})"', line)
            if m:
                self.date = "%s-%s-%s" % (m.group(3), m.group(1).zfill(2), m.group(2).zfill(2))
            for sh in self.stock:
                    string = '</td><td>%s</td><td class="num">(\d*)[,]?(\d{1,3}[.]\d{2})</td><td ' \
                             'class="center">CZK</td><td class="num \w+">-?\w+[.]\d{2}</td><td class="num">' \
                             '(\d*)[,]?(\d*)[,]?(\d+)<' % (sh[1])
                    m = re.search(string, line)
                    if m:
                        data.setdefault(self.date, {}).setdefault("stock", {}).setdefault(sh[0], ["", ""])[0] = \
                            (float("%s%s" % (m.group(1), m.group(2))))
                        data.setdefault(self.date, {}).setdefault("stock", {}).setdefault(sh[0], ["", ""])[1] = \
                            (int("%s%s%s" % (m.group(3), m.group(4), m.group(5))))
        kurzy.close()

    def alert_price_stock(self, parameters):
        self.parameters = parameters
        if self.date != 0:
            for parameter in self.parameters:
                if parameter[2] == "<":
                    if parameter[1] < data[self.date]["stock"][parameter[0]][0]:
                        Analyser.message += 'The share price of  %s is %s CZK and this is higher than set allert ' \
                                            'value (%s CZK).\n' % (parameter[0],
                                                                   data[self.date]["stock"][parameter[0]][0],
                                                                   parameter[1])
                        Analyser.counter += 1
                elif parameter[2] == ">":
                    if parameter[1] > data[self.date]["stock"][parameter[0]][0]:
                        Analyser.message += 'The share price of %s is %s CZK and this is lower than set allert ' \
                                'value (%s CZK).\n' % (parameter[0],
                                                       data[self.date]["stock"][parameter[0]][0],
                                                       parameter[1])
                        Analyser.counter += 1
                else:
                    print "Incorrect character in paramet_stock in setting: (%s,%s,%s)" % (parameter[0],
                                                                                           parameter[1],
                                                                                           parameter[2])
        else:
            print "The page https://www.pse.cz/Kurzovni-Listek/Oficialni-KL/?language=english failed to open."
            

if __name__ == '__main__':
    data = {}

    Config = ConfigParser.ConfigParser()
    Config.read("stock.ini")

    sender = ast.literal_eval(Config.get("messenger", "sender"))
    receivers = ast.literal_eval(Config.get("messenger", "receivers"))
    cc = ast.literal_eval(Config.get("messenger", "cc"))
    smtp = ast.literal_eval(Config.get("messenger", "SMTP"))
    currency = ast.literal_eval(Config.get("currency", "currency"))
    paramet_curr = ast.literal_eval(Config.get("currency", "paramet_curr"))
    urlcurrencies = ast.literal_eval(Config.get("currency", "urlcurrencies"))
    stock_set = ast.literal_eval(Config.get("stock", "stock_set"))
    paramet_stock = ast.literal_eval(Config.get("stock", "paramet_stock"))
    urlstock = ast.literal_eval(Config.get("stock", "urlstock"))
    xday = ast.literal_eval(Config.get("xdayaverage", "xday"))

    if os.path.isfile('stock.dat'):
        with open('stock.dat', 'r') as f:
            data = json.load(f)
 
    x = Currencies(currency)
    g = Analyser()
    y = Stocks(stock_set)

    if (Config.get("run", "parsers") == "yes") or (Config.get("run", "alerts") == "yes"):
        g.parse(x.search_curr, urlcurrencies)
        g.parse(y.search_stock, urlstock)
    if Config.get("run", "alerts") == "yes":
        x.alert_price(paramet_curr)
        y.alert_price_stock(paramet_stock)
    if Config.get("run", "trends") == "yes":
        g.trend(xday)
    if Config.get("run", "data_autoloader") == "yes":
        g.data_autoloader()
        Config.set("run", "data_autoloader", "no")
        with open('stock.ini', 'wb') as configfile:
            Config.write(configfile)
    if Config.get("run", "messenger") == "yes":
        x.messenger()
        
    print Analyser.message

    with open('stock.dat', 'w') as f:
        json.dump(data, f)