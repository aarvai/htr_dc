import time

from kadi import events
from utilities import append_to_array, find_first_after, find_last_before, find_closest

def htr_dc(temp, on_range, off_range, t_start='2000:001', t_stop=None, name=None, event=None, plot_cycles=False, dur_lim=None):
    
    close('all')
    t0 = time.time()    
    
    #fetch data
    x = fetch.Msid(temp, t_start, t_stop)
    v = fetch.Msid('ELBV', t_start, t_stop, stat='5min')
    
    #find htr on and off times
    t1 = time.time()
    dt = diff(x.vals)
    dt1_n0 = nonzero(dt)[0]
    dt1 = dt[dt!=0]
    local_min_i = nonzero((dt1[:-1] < 0.) & (dt1[1:] > 0.))[0]
    local_max_i = nonzero((dt1[:-1] > 0.) & (dt1[1:] < 0.))[0]
    local_min = zeros(len(x.vals), dtype='bool')
    local_max = zeros(len(x.vals), dtype='bool')
    local_min[dt1_n0[local_min_i+1]] = 1
    local_max[dt1_n0[local_max_i]+1] = 1
    
    htr_on_range = x.vals < on_range
    htr_off_range = x.vals > off_range
    
    htr_on = local_min & htr_on_range
    htr_off = local_max & htr_off_range
    
    #remove any incomplete heater cycles at end of timeframe
    t2 = time.time()
    last_off = nonzero(htr_off)[0][-1]
    htr_on[last_off:] = 0
    
    t_on = x.times[htr_on]
    t_off = x.times[htr_off]
    
    #find matching cycles
    match_i1 = find_first_after(t_on, t_off)
    t_off = unique(t_off[match_i1]) #removes duplicate "offs"
    
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
    on_dates_days = floor(DateTime(t_on).mjd)
    
    days = arange(floor(DateTime(t_on[0]).mjd), DateTime(t_on[-1]).mjd)
    days_dates = DateTime(days, format='mjd').iso
    days_mos = array([date[0:7] for date in days_dates])
    mos = unique(days_mos)
    
    t_days = DateTime(days, format='mjd').secs
    t_mos = DateTime([mo + '-01 00:00:00.00' for mo in mos]).secs
    
    #compute stats
    t5 = time.time()
    on_freq = array([sum(on_dates_days == day) for day in days])
    on_freq_mo_mean = array([mean(on_freq[days_mos == mo]) for mo in mos])
    
    on_time = array([sum(dur_each[on_dates_days == day]) for day in days])
    on_time_mo_mean = array([mean(on_time[days_mos == mo]) for mo in mos])
    
    dur = array([mean(dur_each[on_dates_days == day]) for day in days])
    dur_mo_mean = array([mean(dur[days_mos == mo]) for mo in mos])
    
    acc_pwr = array([sum(pwr[on_dates_days == day]) for day in days])
    acc_pwr_mo_mean = array([mean(acc_pwr[days_mos == mo]) for mo in mos])
    
    per_each = diff(t_on)
    per = array([mean(per_each[on_dates_days[:-1] == day]) for day in days])
    per_mo_mean = array([mean(per[days_mos == mo]) for mo in mos])
    
    dc_each = dur_each[:-1] / per_each * 100
    dc = on_time / (3600*24) * 100
    dc_mo_mean = array([mean(dc[days_mos == mo]) for mo in mos])
    
    #plots
    t6 = time.time()
    
    t_event = array([DateTime(event).secs, DateTime(event).secs])
    
    if plot_cycles == True:
        figure(1, figsize=(8,2.2)) #- only plot for short timeframes when troubleshooting
        plot_cxctime(x.times, x.vals, mew=0)
        plot_cxctime(x.times, x.vals, 'b*',mew=0)
        plot_cxctime(x.times[htr_on], x.vals[htr_on], 'c*',mew=0, label='Heater On')
        plot_cxctime(x.times[htr_off], x.vals[htr_off], 'r*',mew=0, label='Heater Off')
        plot_cxctime(t_event, ylim(),'r:')
        ylabel('deg F')
        #legend(loc=0)
        title(name + ' Heater Cycling per ' + temp)
        tight_layout()
        savefig('htr_' + temp + '_sample_cycles.png')
    
    figure(2)
    hist(dur_each/60, bins=100)
    ylabel('instances')
    xlabel('min')
    title(name + ' Heater On-Time Durations')
    savefig('htr_' + temp + '_on_time_hist.png')
    
    figure(3)
    plot_cxctime(t_on, dur_each/60, 'r', alpha=.2, label='Range')
    plot_cxctime(t_days[:-1], dur[:-1]/60, 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], dur_mo_mean[:-1]/60, 'k', label='Monthly Mean')
    plot_cxctime(t_event, ylim(),'r:')
    title(name + ' Heater On-Time')
    ylabel('min')
    legend(loc=0)
    savefig('htr_' + temp + '_on_time.png')
    
    figure(4)
    plot_cxctime(t_on[:-1], per_each/60, 'r', alpha=.2, label='Range')
    plot_cxctime(t_days[:-1], per[:-1]/60, 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], per_mo_mean[:-1]/60, 'k', label='Monthly Mean')
    plot_cxctime(t_event, ylim(),'r:')
    title(name + ' Heater Period')
    ylabel('min')
    legend(loc=0)
    savefig('htr_' + temp + '_period.png')
    
    figure(5, figsize=(8,4))
    dc_each_step = append_to_array(dc_each, pos=0, val=dc_each[0])
    step(t_on, dc_each_step, 'r')
    title(name + ' Heater Duty Cycle')
    ylabel('%')
    savefig('htr_' + temp + '_duty_cycle_step.png')

    figure(6, figsize=(8,4))
    plot_cxctime(t_on[:-1], dc_each, 'r', label='Range')
    #plot_cxctime(t_days[:-1], dc[:-1], 'b', alpha=.5, label='Daily Mean')
    #omit last month in this case due to small sample size
    #plot_cxctime(t_mos[:-1], dc_mo_mean[:-1], 'k', label='Monthly Mean') 
    plot_cxctime(t_event, ylim(),'r:')
    title(name + ' Heater Duty Cycle')
    ylabel('%')
    #legend(loc=0)
    savefig('htr_' + temp + '_duty_cycle.png')
    
    figure(7)
    plot_cxctime(t_days[:-1], on_freq[:-1], 'b', alpha=.3, label='Range')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], on_freq_mo_mean[:-1], 'k', label='Monthly Mean')
    plot_cxctime(t_event, ylim(),'r:')
    title(name + ' Heater Cycles Per Day')
    legend(loc=0)
    savefig('htr_' + temp + '_on_freq.png')
    
    figure(8)
    plot_cxctime(t_days[:-1], on_time[:-1]/3600, 'b', alpha=.3, label='Range')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], on_time_mo_mean[:-1]/3600, 'k', label='Monthly Mean')
    plot_cxctime(t_event, ylim(),'r:')
    title('Accumulated ' + name + ' Heater On-Time Per Day')
    ylabel('hrs')
    legend(loc=0)
    savefig('htr_' + temp + '_acc_on_time.png')
    
    figure(9)
    plot_cxctime(t_days[:-1], acc_pwr[:-1], 'b', alpha=.3, label='Range')
    #omit last month in this case due to small sample size
    plot_cxctime(t_mos[:-1], acc_pwr_mo_mean[:-1], 'k', label='Monthly Mean')
    plot_cxctime(t_event, ylim(),'r:')
    title('Accumulated ' + name + ' Heater Power Per Day')
    ylabel('W-hrs')
    legend(loc=0)
    savefig('htr_' + temp + '_acc_pwr.png')
    
    print('Processing times:')
    print(str(t1 - t0) + ' - fetching data')
    print(str(t2 - t1) + ' - find htr on and off times')
    print(str(t3 - t2) + ' - find matching cycles')
    print(str(t4 - t3) + ' - compute dur_each and power')
    print(str(t5 - t4) + ' - calendar bookkeeping')
    print(str(t6 - t5) + ' - compute stats')
    print(str(time.time() - t6) + ' - plots')



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    