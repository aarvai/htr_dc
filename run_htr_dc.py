execfile('htr_dc.py')

# MUPS Valve Heaters
#htr_dc('PM3THV1T', on_range=[58, 63], off_range=[92, 110], name='MUPS-3 Valve')
#htr_dc('PM4THV1T', on_range=[55, 60], off_range=[94, 110], name='MUPS-4 Valve')

# RCS Valve Heaters
#htr_dc('PR1TV02T', on_range=[46, 50], off_range=[86, 95], dur_lim=60*60, name='RCS-1 Valve') #use B because A therm has dropouts
#htr_dc('PR2TV01T', on_range=[46, 52], off_range=[75, 85], dur_lim=60*60, name='RCS-2 Valve')
htr_dc('PR3TV01T', on_range=[40, 60], off_range=[70, 90], dur_lim=60*60, name='RCS-3 Valve')
#htr_dc('PR3TV01T', t_start='2013:101', t_stop='2013:200', on_range=[40, 60], off_range=[70, 90], dur_lim=60*60, name='RCS-3 Valve', plot_cycles=True)

# LAE Valve Heaters