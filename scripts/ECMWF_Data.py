#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import winsound

duration = 1000  # millisecond
freq = 800  # Hz

server = ECMWFDataServer()
server.retrieve({
    "class": "ti",
    "dataset": "tigge",
    "date": "2018-05-01/to/2018-05-31",
    "expver": "prod",
    "grid": "0.5/0.5",
    "levelist": "300/700/1000",
    "levtype": "pl",
    "number": "1/2",
    "origin": "ecmf",
    "param": "131/132",
    "step": "6",
    "time": "00:00:00",
    "type": "pf",
    "format": "netcdf",
    "target": "output",
})

winsound.Beep(freq, duration)