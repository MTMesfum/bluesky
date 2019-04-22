#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import winsound

duration = 1000  # millisecond
freq = 800  # Hz

server = ECMWFDataServer()
server.retrieve({
    "class": "ti",
    "dataset": "tigge",
    "date": "2014-06-25/to/2014-06-26",
    "expver": "prod",
    "grid": "0.5/0.5",
    "levelist": "200/250/300/500/700/850/925/1000",
    "levtype": "pl",
    "number": "1/2/3",
    "origin": "ecmf",
    "param": "131/132",
    "step": "6",
    "time": "00:00:00",
    "format": "netcdf",
    "target": "C:\Documents\Git\\24_06_2014.nc",
})

# 3 pressure levels, 3 perturbations

winsound.Beep(freq, duration)