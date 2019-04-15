#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import winsound

duration = 1000  # millisecond
freq = 800  # Hz

server = ECMWFDataServer()
server.retrieve({
    "class": "ti",
    "dataset": "tigge",
    "date": "2014-06-10/to/2014-06-14",
    "expver": "prod",
    "grid": "0.5/0.5",
    "levelist": "250/700/1000",
    "levtype": "pl",
    "number": "1/2/3",
    "origin": "ecmf",
    "param": "131/132",
    "step": "6",
    "time": "00:00:00",
    "format": "netcdf",
    "target": "F:\Documents\ECMWF Data\\tigge10.nc",
})

# 3 pressure levels, 3 perturbations

winsound.Beep(freq, duration)