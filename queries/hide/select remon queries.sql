SELECT * FROM ddr_1409_nest.flight where
-- ac_id = 'BER717E';
aobt BETWEEN '2014-09-12 00:00:00' AND '2014-09-12 23:59:59' 
AND ac_id in (	'ADH931', 'AEE929', 'AFL2352', 'AFR234H', 'AUA381', 
				'AUA522D', 'AUA601', 'AUI34L', 'AZA1572', 'BAW4TM',
                'BAW66Q', 'BEL724', 'BEL7PC', 'BER717E', 'BLX328',
                'CCA931', 'DLH08W', 'DLH156', 'DLH1HU', 'DLH8PK',
                'DTH3057', 'EIN111', 'EXS79G', 'EZY471', 'EZY92FN',
                'FPO551', 'GWI2807', 'KLM1395', 'KLM59Z', 'LBT7362',
                'MIBID', 'MON752A', 'NJE2FD', 'OHY2160', 'PGT424', 
                'PGT4629', 'PRI5403', 'QTR022', 'ROT608D', 'RYR5008',
                'SAS1042', 'SAS1842', 'SAS618', 'SHT2J', 'SWR779',
                'TAP1015', 'TAP803L', 'TAY011', 'TFL219', 'VLG2473', 
                'WZZ114')  
