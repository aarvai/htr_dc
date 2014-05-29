execfile('htr_dc.py')

#1.  FDM-2 
#htr_dc('PFDM202T', 57, 64, t_start='2010:075', t_stop='2010:110', name='FDM-2', plot_cycles=True, dur_lim=200*60) #troubleshooting
#htr_dc('PLINE08T', 58, 71, t_start='2001:001', t_stop='2014:100', name='5133 Line', event='2010:099:16:54:00.000', plot_cycles=False)
#htr_dc('PLINE01T', 59, 67.2, t_start='2001:001', t_stop='2014:100', name='5105 Line', event='2010:099:16:54:00.000', plot_cycles=False, dur_lim=70*60)

#2.  MUPS Valve Heaters
htr_dc('PFDM202T', 57, 64, t_start='2010:075', t_stop='2010:110', name='FDM-2', plot_cycles=True, dur_lim=200*60) #troubleshooting

#3.  RCS Valve Heaters


#4.  LAE Valve Heaters