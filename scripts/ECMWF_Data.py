#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import winsound

duration = 1000  # millisecond
freq = 800  # Hz

server = ECMWFDataServer()
server.retrieve({
    "class": "ti",
    "dataset": "tigge",
    "date": "2014-09-08",
    "expver": "prod",
    "grid": "0.5/0.5",
    "levelist": "200/250/300/500/700/850/925/1000",
    "levtype": "pl",
    "number": "1/2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30/31/32/33/34/35/36/37/38/39/40/41/42/43/44/45/46/47/48/49/50",
    "origin": "ecmf",
    "param": "131/132",
    "step": "24/30/36",
    "time": "00:00:00",
    "type": "pf",
    "format": "netcdf",
    "target": "I:\Documents\Google Drive\Thesis 2018\BlueSky Git3\\Tigge_08_09_2014_00.nc",
})

winsound.Beep(freq, duration)