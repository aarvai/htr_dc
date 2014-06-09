import time
from matplotlib import pyplot as pp

from kadi import events

#from utilities import append_to_array, find_first_after, find_last_before, find_closest

def append_to_array(a, pos=-1, val=0):
    """Appends a zero (or user-defined value) to a given one-dimensional array, 
    either at the end (pos=-1) or beginning (pos=0).
    
    e.g. append_to_array(arange(5),pos=-1)
    returns array([0, 1, 2, 3, 4, 0])
    """
    val_a = np.array([val])
    if pos==0:
        out = np.concatenate([val_a, a])
    elif pos==-1:
        out = np.concatenate([a, val_a])
    return out
    
def find_last_before(a, b):
    """This function returns an array of length a with the indices of 
    array b that are closest without going over the values of array a.
    (Bob Barker rules.  Assumes b is sorted by magnitude.)
    """
    out = np.searchsorted(b,a,side='left') - 1
    out[out==-1] = 0
    return out    
     
def find_first_after(a, b):
    """This function returns an array of length a with the indices of 
    array b that are closest without being less than the values of array a.
    (Opposite of Bob Barker rules.  Assumes b is sorted by magnitude.)
    """
    out = np.searchsorted(b,a,side='right')
    return out  

def find_closest(a, b):
    """This function returns an array of length a with the indices of 
    array b that are closest to the values of array a.
    """
    idx = np.array([(np.abs(b-a_i)).argmin() for a_i in a])
    return idx

def htr_dc(temp, t_start='2008:001', t_stop=None, on_range=None, off_range=None, name=None, event=None, dur_lim=None, plot_cycles=False, logfile='htr_dc_log.txt'):
    """This function generates heater cycling metrics based on a nearby  
    temperature.  Output plots include:
       - On-time durations
       - Period
       - Duty cycle
       - Cycles per day
       - Accumulated on-time per day
       - Accumulated power per day
       - Time history (optional)
    
    Inputs:
       temp         Thermistor near heater, preferably close to thermostat
       t_start      Start of timeframe to analyze (default is 2008:001)
       t_stop       End of timeframe to analyze (default is current time)
       on_range     Temperature range to constrain identified heater "on" instances 
       off_range    Temperature range to constrain identified heater "off" instances
       name         Identifying name of heater
       event        Significant time for which it is desired to highlight via vertical line
       dur_lim      Maximum duration for single heater "on" instance
       plot_cycles  Option to plot time-history, highlighting htr on and off points 
                    (default is False)
    
    Figures will be saved to local directory as 'htr_' + msid + '*.png'
    """
    
    pp.close('all')
    t0 = time.time()    
    
    #fetch data
    x = fetch.Msid(temp, t_start, t_stop)
    v = fetch.Msid('ELBV', t_start, t_stop, stat='5min')
    
    #find htr on and off times
    t1 = time.time()
    dt = np.diff(x.vals)
    dt1_n0 = np.nonzero(dt)[0]
    dt1 = dt[dt!=0]
    local_min_i = np.nonzero((dt1[:-1] < 0.) & (dt1[1:] > 0.))[0]
    local_max_i = np.nonzero((dt1[:-1] > 0.) & (dt1[1:] < 0.))[0]
    local_min = np.zeros(len(x.vals), dtype='bool')
    local_max = np.zeros(len(x.vals), dtype='bool')
    local_min[dt1_n0[local_min_i+1]] = 1
    local_max[dt1_n0[local_max_i]+1] = 1
    
    if on_range != None:
        htr_on_range = (x.vals > on_range[0]) & (x.vals < on_range[1])
        htr_on = local_min & htr_on_range
    else:    
        htr_on = local_min 

    if off_range != None:
        htr_off_range = (x.vals > off_range[0]) & (x.vals < off_range[1])      
        htr_off = local_max & htr_off_range
    else:
        htr_off = local_max
    
    #remove any incomplete heater cycles at end of timeframe
    t2 = time.time()
    last_off = np.nonzero(htr_off)[0][-1]
    htr_on[last_off:] = 0
    
    t_on = x.times[htr_on]
    t_off = x.times[htr_off]
    
    #find matching cycles
    match_i1 = find_first_after(t_on, t_off)
    t_off = np.unique(t_off[match_i1]) #removes duplicate "offs"
    
    match_i2 = find_last_before(t_off, t_on)
    t_on = t_on[match_i2] #removes duplicate "ons"
    
    if plot_cycles == True:    #time-intensive, not used if not plotting
        htr_on = find_closest(t_on, x.times) 
        htr_off = find_closest(t_off, x.times)
    
    #compute duration and power
    t3 = time.time()
    dur_each = t_off - t_on
    
    if dur_lim != None:
        too_long = dur_each > dur_lim
        t_on = t_on[~too_long]
        t_off = t_off[~too_long]
        htr_on = htr_on[~too_long]
        htr_off = htr_off[~too_long]
        dur_each = dur_each[~too_long]
    
    voltage_i = find_first_after(t_on, v.times)
    voltage = v.vals[voltage_i]
    pwr = voltage**2/40 * dur_each/3600 #W-hrs
    
    #calendar bookkeeping
    t4 = time.time()
    on_dates = DateTime(t_on).iso
    on_dates_days = np.floor(DateTime(t_on).mjd)
    on_dates_mos = np.array([date[0:7] for date in on_dates])
    
    days = np.arange(np.floor(DateTime(t_start).mjd), DateTime(t_stop).mjd)
    days_dates = DateTime(days, format='mjd').iso
    days_mos = np.array([date[0:7] for date in days_dates])
    mos = np.unique(days_mos)
    
    t_days = DateTime(days, format='mjd').secs
    t_mos = DateTime([mo + '-01 00:00:00.00' for mo in mos]).secs
    
    #compute stats
    t5 = time.time()
    on_freq = np.array([np.sum(on_dates_days == day) for day in days])
    on_freq[np.isnan(on_freq)] = 0
    on_freq_mo_mean = np.array([np.mean(on_freq[days_mos == mo]) for mo in mos])

    on_time = np.array([np.sum(dur_each[on_dates_days == day]) for day in days])
    on_time[np.isnan(on_time)] = 0
    on_time_mo_mean = np.array([np.mean(on_time[days_mos == mo]) for mo in mos])
    
    dur = np.array([np.mean(dur_each[on_dates_days == day]) for day in days])
    dur_mo_mean = np.array([np.mean(dur_each[on_dates_mos == mo]) for mo in mos])
    
    acc_pwr = np.array([np.sum(pwr[on_dates_days == day]) for day in days])
    acc_pwr[np.isnan(acc_pwr)] = 0
    acc_pwr_mo_mean = np.array([np.mean(acc_pwr[days_mos == mo]) for mo in mos])
    
    per_each = np.diff(t_on)
    per = np.array([np.mean(per_each[on_dates_days[:-1] == day]) for day in days])
    per_mo_mean = np.array([np.mean(per_each[on_dates_mos[:-1] == mo]) for mo in mos])
    
    dc_each = dur_each[:-1] / per_each * 100
    dc = on_time / (3600*24) * 100
    dc_mo_mean = np.array([np.mean(dc[days_mos == mo]) for mo in mos])
 
    #plots
    t6 = time.time()
    
    t_event = np.array([DateTime(event).secs, DateTime(event).secs])
    
    if plot_cycles == True:
        pp.figure(1, figsize=(6,3)) #- only plot for short timeframes when troubleshooting
        plot_cxctime(x.times, x.vals, mew=0)
        plot_cxctime(x.times, x.vals, 'b*',mew=0)
        plot_cxctime(x.times[htr_on], x.vals[htr_on], 'c*',mew=0, label='Heater On')
        plot_cxctime(x.times[htr_off], x.vals[htr_off], 'r*',mew=0, label='Heater Off')
        if event != None:
            plot_cxctime(t_event, ylim(),'r:')
        pp.ylabel('deg F')
        pp.legend(loc=0)
        pp.title(name + ' Heater Cycling per ' + temp)
        #pp.tight_layout()
        pp.savefig('htr_' + temp + '_sample_cycles.png')
    
    pp.figure(2, figsize=(6,3))
    pp.hist(dur_each/60, bins=100)
    pp.ylabel('instances')
    pp.xlabel('min')
    pp.title(name + ' Heater On-Time Durations')
    pp.savefig('htr_' + temp + '_on_time_hist.png')
    
    pp.figure(3, figsize=(6,3))
    plot_cxctime(t_on, dur_each/60, 'r', alpha=.2, label='Each Cycle')
    plot_cxctime(t_days[:-1], dur[:-1]/60, 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], dur_mo_mean[:-1]/60, 'k', label='Monthly Mean')
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title(name + ' Heater On-Time')
    pp.ylabel('min')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_on_time.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title(name + ' Heater On-Time (ZOOM)')
    pp.legend(loc=0)
    #pp.tight_layout()
    pp.savefig('htr_' + temp + '_on_time_zoom.png')
    
    pp.figure(4, figsize=(6,3))
    plot_cxctime(t_on[:-1], per_each/60, 'r', alpha=.2, label='Each Cycle')
    plot_cxctime(t_days[:-1], per[:-1]/60, 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], per_mo_mean[:-1]/60, 'k', label='Monthly Mean')
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title(name + ' Heater Period')
    pp.ylabel('min')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_period.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title(name + ' Heater Period (ZOOM)')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_period_zoom.png')
        
    #figure(5, figsize=(6,3))
    #as a first-order hold, this plotting is more accurate than fig 6
    #(holds values til the next), but isn't necessary if there's a long
    #timespan.  Disadvantage is the unhelpful x-axis.
    #dc_each_step = append_to_array(dc_each, pos=0, val=dc_each[0])
    #step(t_on, dc_each_step, 'r')
    #title(name + ' Heater Duty Cycle')
    #ylabel('%')
    #savefig('htr_' + temp + '_duty_cycle_step.png')

    pp.figure(6, figsize=(6,3))
    plot_cxctime(t_on[:-1], dc_each, 'r', alpha=.2, label='Each Cycle')
    plot_cxctime(t_days[:-1], dc[:-1], 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], dc_mo_mean[:-1], 'k', label='Monthly Mean') 
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title(name + ' Heater Duty Cycle')
    pp.ylabel('%')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_duty_cycle.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title(name + ' Heater Duty Cycle(ZOOM)')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_duty_cycle_zoom.png')
    
    pp.figure(7, figsize=(6,3))
    plot_cxctime(t_days[:-1], on_freq[:-1], 'b', alpha=.3, label='Cycles Per Day')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], on_freq_mo_mean[:-1], 'k', label='Monthly Mean')
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title(name + ' Heater Cycles Per Day')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_on_freq.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title(name + ' Heater Cycles Per Day (ZOOM)')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_on_freq_zoom.png')
    
    pp.figure(8, figsize=(6,3))
    plot_cxctime(t_days[:-1], on_time[:-1]/3600, 'b', alpha=.3, label='On-Time Per Day')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], on_time_mo_mean[:-1]/3600, 'k', label='Monthly Mean')
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title('Accumulated ' + name + ' Heater On-Time Per Day')
    pp.ylabel('hrs')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_acc_on_time.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title('Accumulated ' + name + ' Heater On-Time Per Day (ZOOM)')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_acc_on_time_zoom.png')
    
    pp.figure(9, figsize=(6,3))
    plot_cxctime(t_days[:-1], acc_pwr[:-1], 'b', alpha=.3, label='Power Per Day')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], acc_pwr_mo_mean[:-1], 'k', label='Monthly Mean')
    if event != None:    
        plot_cxctime(t_event, ylim(),'r:')
    pp.title('Accumulated ' + name + ' Heater Power Per Day')
    pp.ylabel('W-hrs')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_acc_pwr.png')
    pp.xlim([DateTime(pp.xlim()[1]-90, format='plotdate').plotdate, pp.xlim()[1]])
    pp.title('Accumulated ' + name + ' Heater Power Per Day (ZOOM)')
    pp.legend(loc=0)
    pp.savefig('htr_' + temp + '_acc_pwr_zoom.png')
    
    print('Processing times for ' + temp + ':')
    print(str(t1 - t0) + ' - fetching data')
    print(str(t2 - t1) + ' - find htr on and off times')
    print(str(t3 - t2) + ' - find matching cycles')
    print(str(t4 - t3) + ' - compute dur_each and power')
    print(str(t5 - t4) + ' - calendar bookkeeping')
    print(str(t6 - t5) + ' - compute stats')
    print(str(time.time() - t6) + ' - plots')
    print('Updated through:  ' + DateTime(x.times[-1]).date)
    print('Processing completed at:  ' + DateTime().date)
    print(' ')
    
    if logfile != None:
        f = open(logfile, 'a')
        f.write(temp + ' updated through ' + DateTime(x.times[-1]).date + ', completed at ' + DateTime().date + '\n')
        f.close()
        f2 = open('updated_thru.html', 'w')
        f2.write('<font face="sans-serif" size=4> \n')
        f2.write(DateTime(x.times[-1]).date)
        f2.close()
        shutil.copy('/home/aarvai/python/htr_dc/htr_dc_log.txt', '/share/FOT/engineering/prop/Heater_Trending')




    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    