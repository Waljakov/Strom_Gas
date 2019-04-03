#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Gas
# Mit diesem Script kann der veranschlagte Gasverbrauch mit dem realen verglichen werden

import matplotlib.pyplot as plt 
import matplotlib.dates as dates
import numpy as np
import datetime
import pandas as pd

# Daten einlesen
daten = np.loadtxt("Gaszaehler.txt", dtype=(str), skiprows=1,)
datum = daten[:,0]
stand_all = daten[:,1]
stand_all = stand_all.astype(np.float)*10
dates_list_all=[datetime.datetime.strptime(dat, "%d.%m.%Y") for dat in datum]

dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%Y')
df_raw = pd.read_csv('Gaszaehler.txt', sep='\t', lineterminator='\n', low_memory=False, 
                     parse_dates=["Datum"], date_parser=dateparse)

print(df_raw.Datum.dt.month)
# Variablen
StartMessung = 0 # Startmesspunkt der Auswahl
EndMessung = len(stand_all)-1 # Endmesspunkt der Auswahl
kosten_kWh = 0.0562 # kosten pro kWh in EUR
kosten_monat = 9.29 # Monatliche Fixkosten
Voranschlag_verbrauch = 2500 # Prognostizierter Jahresverbrauch in kWh

NullStand = stand_all[StartMessung]
NullDatum = dates_list_all[StartMessung]
EndStand = stand_all[EndMessung]
EndDatum = dates_list_all[EndMessung]

dates_list = []
stand = []
for i in np.arange(StartMessung, EndMessung+1):
    dates_list.append(dates_list_all[i])
    stand.append(stand_all[i])
print()
print("Veranschlagter Jahresverbrauch des Anbieters:", Voranschlag_verbrauch, "kWh.")
print()
print("Auswahl", NullDatum.strftime("%d.%m.%Y"), "bis", EndDatum.strftime("%d.%m.%Y"), ":")


# Durchschnittsverbrauch und Jahreshochrechnung
delta_time = EndDatum-NullDatum
delta_time_all =dates_list_all[len(dates_list_all)-1] - dates_list_all[0]
verbrauch_total = EndStand-NullStand
mean_monatsverbrauch = 31*verbrauch_total/delta_time.days
print("Durchschnittlicher Monatsverbrauch:", round(mean_monatsverbrauch,2), "kWh")
print("Voraussichtlicher Jahresverbrauch:", round(mean_monatsverbrauch*12,2), "kWh.")

# Datafit
dates_numbers_all=dates.date2num(dates_list_all)
dates_numbers=dates.date2num(dates_list)
linfit = np.poly1d(np.polyfit(dates_numbers,stand,1))
linfit_all = np.poly1d(np.polyfit(dates_numbers_all,stand_all,1))
xfit=np.linspace(dates_numbers[0], dates_numbers[len(dates_numbers)-1], 100)
xfit_all=np.linspace(dates_numbers_all[0], dates_numbers_all[len(dates_numbers_all)-1]+10, 100)


# veranschlagter Verbrauch
def veranschlagt(start, end): # start, end als datenum (Zahl)
    return Voranschlag_verbrauch/335.*(end-start)

# Kosten
def Kosten(startdat, enddat, verbrauch): # startdat und enddat als datenum (Zahl), startstand und entstand sind zaehlerstanddifferenz
    startDate=dates.num2date(startdat)
    endDate=dates.num2date(enddat)
    if isinstance(startdat,list):
        Monats_kost=[]
        for i in range(0,len(startdat)):
            Monats_kost.append((endDate[i].month-startDate[i].month + 1 + (endDate[i].year - startDate[i].year)*12)*kosten_monat)
    else:
        Monats_kost = (endDate.month-startDate.month + 1 + (endDate.year - startDate.year)*12)*kosten_monat
    return verbrauch * kosten_kWh + Monats_kost


# Kostendifferenz
kost=Kosten(dates_numbers[0],dates_numbers[len(dates_numbers)-1],EndStand-NullStand)
kost_diff = Kosten(dates_numbers[0],dates_numbers[len(dates_numbers)-1],veranschlagt(dates_numbers[0],dates_numbers[len(dates_numbers)-1])) - kost
kost_all=Kosten(dates_numbers_all[0],dates_numbers_all[len(dates_numbers_all)-1],stand_all[len(stand_all)-1]-stand_all[0])
kost_diff_all = Kosten(dates_numbers_all[0],dates_numbers_all[len(dates_numbers_all)-1],veranschlagt(dates_numbers_all[0],dates_numbers_all[len(dates_numbers_all)-1])) - kost_all

print("Bisherige Kosten:", round(kost,2), "EUR")
print("Kostendifferenz:", round(kost_diff,2), "EUR")
print()
print("Gesamt", dates_list_all[0].strftime("%d.%m.%Y"), "bis", dates_list_all[len(dates_list_all)-1].strftime("%d.%m.%Y"), ":")
print("Bisheriger Verbrauch", stand_all[len(stand_all)-1]-stand_all[0], "kWh")
print("Bisherige Kosten:", round(kost_all,2), "EUR")
print("Kostendifferenz:", round(kost_diff_all,2), "EUR")

# Ticks einstellen
formatter = dates.DateFormatter('%d.%m')
years = dates.YearLocator()   # every year
months = dates.MonthLocator()  # every month
days = dates.DayLocator()
monthsFmt = dates.DateFormatter('%B')

# Daten plotten
fig, ax = plt.subplots()
ax.plot(dates_list_all, stand_all, marker=".", markersize=7, ls="-.", lw=0.5, label="Gemessen")
ax.plot(dates.num2date(xfit_all), linfit(xfit_all), lw=0.5, label="Durchschnitt der Auswahl")
ax.plot(dates.num2date(xfit_all), veranschlagt(dates_numbers_all[0],xfit_all)+stand_all[0], lw=1, label="Veranschlagt")
plt.ylabel("Zaehlerstand /kWh")
plt.grid()
plt.title("Gasverbrauch")
ax.set_ylim(stand_all[0])
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(days)
ax.legend()
plt.gcf().autofmt_xdate(rotation=25)

# Kosten plotten
fig2, ax2 = plt.subplots()
plt.ylabel("Kosten /EUR")
plt.title("Gaskosten")
plt.grid()
ax2.plot(dates_numbers_all, Kosten([dates_numbers_all[0]]*(len(dates_numbers_all)),dates_numbers_all,stand_all-stand_all[0]), marker=".", markersize=7, ls="-.", lw=0.5, label="Gemessen")
ax2.plot(xfit_all,Kosten([dates_numbers_all[0]]*(len(xfit_all)),xfit_all,veranschlagt([dates_numbers_all[0]]*(len(xfit_all)),xfit_all)), label="Kosten Voranschlag")
ax2.plot(xfit_all,Kosten([dates_numbers_all[0]]*(len(xfit_all)),xfit_all,linfit_all(xfit_all)-stand_all[0]),lw=0.5, label="Gesamtdurchschnitt")
ax2.plot(xfit_all,Kosten([dates_numbers_all[0]]*(len(xfit_all)),xfit_all,linfit(xfit_all)-stand_all[0]),lw=0.5, label="Durchschnitt der Auswahl")
ax2.set_ylim(0)
ax2.xaxis.set_major_locator(months)
ax2.xaxis.set_major_formatter(monthsFmt)
ax2.xaxis.set_minor_locator(days)
ax2.legend()
plt.gcf().autofmt_xdate(rotation=25)
plt.show()
