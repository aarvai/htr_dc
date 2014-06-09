import glob
import shutil
import numpy as np

import matplotlib.pyplot as plt
import asciitable
import Ska.engarchive.fetch_eng as fetch
from Chandra.Time import DateTime
from Ska.Matplotlib import plot_cxctime, cxctime2plotdate
from kadi import events
from astropy.table import Table

execfile('htr_dc.py')

# ----------------------------------------------------------------------------------------------------
# First round:  short timeframes to generate zoomed-in plots with time histories
# ----------------------------------------------------------------------------------------------------

f = open('htr_dc_log.txt', 'a')
f.write('\n')
f.write('\n')
f.write('\n')
f.write('------------------------------------------------------------------------------------------------- \n')
f.write('Starting Processing for Round 1 (past 90 days) at ' + DateTime().date + ' \n')
f.write('------------------------------------------------------------------------------------------------- \n')
f.close()
shutil.copy('/home/aarvai/python/htr_dc/htr_dc_log.txt', '/share/FOT/engineering/prop/Heater_Trending')

t2 = DateTime().mjd
t1 = DateTime(t2-90, format='mjd').date
t2 = DateTime(t2, format='mjd').date

# MUPS Valve Heaters
# MUPS-1 and MUPS-2 heaters don't cycle
htr_dc('PM3THV1T', t_start=t1, t_stop=t2, on_range=[58, 63], off_range=[92, 110], dur_lim=30*60, name='MUPS-3 Valve', plot_cycles=True)
htr_dc('PM4THV1T', t_start=t1, t_stop=t2, on_range=[55, 60], off_range=[94, 110], name='MUPS-4 Valve', plot_cycles=True)

# RCS Valve Heaters
htr_dc('PR1TV02T', t_start=t1, t_stop=t2, on_range=[46, 50], off_range=[86, 95], dur_lim=60*60, name='RCS-1 Valve', plot_cycles=True) #use B because A therm has dropouts
htr_dc('PR2TV01T', t_start=t1, t_stop=t2, on_range=[46, 52], off_range=[75, 85], dur_lim=60*60, name='RCS-2 Valve', plot_cycles=True)
htr_dc('PR3TV01T', t_start=t1, t_stop=t2, on_range=[40, 60], off_range=[70, 90], dur_lim=60*60, name='RCS-3 Valve', plot_cycles=True)
htr_dc('PR4TV01T', t_start=t1, t_stop=t2, on_range=[40, 60], off_range=[75, 95], dur_lim=60*60, name='RCS-4 Valve', plot_cycles=True)

# LAE Valve Heaters
htr_dc('PLAEV1AT', t_start=t1, t_stop=t2, on_range=[50, 57], off_range=[64, 70], dur_lim=30*60, name='LAE-1 Valve', plot_cycles=True)
# LAE-2A and 2B thermistors have too many dropouts for accurate trending
htr_dc('PLAEV3AT', t_start=t1, t_stop=t2, on_range=[50, 57], off_range=[65, 70], dur_lim=120*60, name='LAE-3 Valve', plot_cycles=True)
htr_dc('PLAEV2AT', t_start=t1, t_stop=t2, on_range=[55, 65], off_range=[72, 85], dur_lim=60*60, name='LAE-4 Valve', plot_cycles=True) #PLAE2AT and 4AT are switched in the database

# ----------------------------------------------------------------------------------------------------
# Second round:  mission plots
# ----------------------------------------------------------------------------------------------------

f = open('htr_dc_log.txt', 'a')                                            
f.write('---------------------------------------------------------------------------------- \n')
f.write('Starting Processing for Round 2 (mission plots) at ' + DateTime().date + ' \n')
f.write('---------------------------------------------------------------------------------- \n')
f.close()
shutil.copy('/home/aarvai/python/htr_dc/htr_dc_log.txt', '/share/FOT/engineering/prop/Heater_Trending')

# MUPS Valve Heaters
# MUPS-1 and MUPS-2 heaters don't cycle
htr_dc('PM3THV1T', on_range=[58, 63], off_range=[92, 110], name='MUPS-3 Valve')
htr_dc('PM4THV1T', on_range=[55, 60], off_range=[94, 110], name='MUPS-4 Valve')

# RCS Valve Heaters
htr_dc('PR1TV02T', on_range=[46, 50], off_range=[86, 95], dur_lim=60*60, name='RCS-1 Valve') #use B because A therm has dropouts
htr_dc('PR2TV01T', on_range=[46, 52], off_range=[75, 85], dur_lim=60*60, name='RCS-2 Valve')
htr_dc('PR3TV01T', on_range=[40, 60], off_range=[70, 90], dur_lim=60*60, name='RCS-3 Valve')
htr_dc('PR4TV01T', on_range=[40, 60], off_range=[75, 95], dur_lim=60*60, name='RCS-4 Valve')

# LAE Valve Heaters
htr_dc('PLAEV1AT', on_range=[50, 57], off_range=[64, 70], dur_lim=30*60, name='LAE-1 Valve')
# LAE-2A and 2B thermistors have too many dropouts for accurate trending
htr_dc('PLAEV3AT', on_range=[50, 57], off_range=[65, 70], dur_lim=120*60, name='LAE-3 Valve')
htr_dc('PLAEV2AT', on_range=[55, 65], off_range=[72, 85], dur_lim=60*60, name='LAE-4 Valve') #PLAE2AT and 4AT are switched in the database

# Copy all PNGs and log file into web-accessible folder
for file in glob.glob(r'/home/aarvai/python/htr_dc/*.png'):
    shutil.copy(file, '/share/FOT/engineering/prop/Heater_Trending/plots')
shutil.copy('/home/aarvai/python/htr_dc/updated_thru.html', '/share/FOT/engineering/prop/Heater_Trending/plots')
f = open('htr_dc_log.txt', 'a')                                            
f.write('---------------------------------------------------------------------------------- \n')
f.write('Website Updated at ' + DateTime().date + ' \n')
f.write('---------------------------------------------------------------------------------- \n')
f.close()
shutil.copy('/home/aarvai/python/htr_dc/htr_dc_log.txt', '/share/FOT/engineering/prop/Heater_Trending')
