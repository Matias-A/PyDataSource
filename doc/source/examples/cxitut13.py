import sys
import time

exp = 'cxitut13'

def DataSource(exp=exp, run=30, 
        save_config=True, publish=False, **kwargs):
    """Load event data source and configure for cxitut13 data.
    """
    import PyDataSource
    import numpy as np
    ds = PyDataSource.DataSource(exp=exp,run=run, **kwargs)
    evt = ds.events.next()
    
    if run in [10,11]:
        evt.DscCsPad.add.parameter(gain=1/23.)
        bins = np.arange(-20,150,1)*evt.DscCsPad.gain
        evt.DscCsPad.add.histogram('calib', bins=bins, gain=evt.DscCsPad.gain, 
                name='photon_hist', unit='photons', 
                doc='Front CsPad Gain corrected histogram', 
                publish=publish)
        evt.DscCsPad.add.count('calib', limits=(12,10000), 
                gain=evt.DscCsPad.gain, 
                name='photon_count', unit='photons', 
                doc='Front CsPad Photon Count')

    elif run == 20:
        evt.DsaCsPad.add.parameter(gain=1/27.7)
        bins = np.arange(-20,150,1)*evt.DsaCsPad.gain
        evt.DsaCsPad.add.histogram('calib', bins=bins, gain=evt.DsaCsPad.gain, 
                name='photon_hist', unit='photons', 
                doc='CsPad Gain corrected histogram', 
                publish=publish)
        evt.DsaCsPad.add.count('calib', limits=(12,10000), 
                gain=evt.DsaCsPad.gain, 
                name='photon_count', unit='photons', 
                doc='CsPad Photon Count')

    elif run == 30:
        evt.Sc2Imp.add.module('impbox')
        evt.Acqiris.add.module('acqiris')
    
    if save_config:
        ds.save_config()

    return ds

def to_xarray(ds, build_html='auto', **kwargs):
    """
    Make xarray object
    """
    x = ds.to_hdf5(build_html=build_html, **kwargs) 
    return x

def make_cuts(x, **kwargs):
    """
    Make experiment specific cuts
    """
    return x

def build_run(x, ioff=True, auto=False, **kwargs):
    """Make html web page from xarray summary dataset.
    """
    # do not perform interactive plotting
    import matplotlib.pyplot as plt
    from PyDataSource.build_html import Build_html
    if ioff:
        plt.ioff()

    x = make_cuts(x)
    run = int(x.run.values[0])

    b = Build_html(x, auto=auto, **kwargs)
    if not auto:   
        b.add_detstats()
        b.add_correlations()
        attrs = [a for a in x.keys() if (a.endswith('_count') or a.endswith('_sum')) 
                    and len(x[a].dims) == 1 and 'time' in x[a].dims]
        if 'PhotonEnergy' in x:
            attrs.append('PhotonEnergy')
        if 'Gasdet_post_atten' in x:
            attrs.append('Gasdet_post_atten')
        b.add_detector(attrs=attrs, catagory='Detector Count', confidence=0.1)
 
    if run in [10,11]:
        variables = ['DscCsPad_photon_hist']
        b.add_summary(variables)
        b.add_detector('DscCsPad')
        b.to_html()
    
    elif run == 20:
        variables = ['DsaCsPad_photon_hist']
        b.add_summary(variables)
        b.add_detector('DsaCsPad')
        b.add_stats('DsaCsPad_corr_stats')
        b.add_stats('Sc2Questar_corr_stats')
        b.to_html()

    else:
        if not auto:
            b.add_all(**kwargs)
            b.to_html()
    
    return b

def main():
    """Main script to create run summary.
    """
    from PyDataSource import initArgs
    time0 = time.time()
    print time0
    args = initArgs.initArgs()
    print args
    attr = args.attr
    exp = args.exp
    run = int(args.run.split('-')[0])
    print exp, run
    if attr in ['build']:
        from PyDataSource import h5write
        x = h5write.open_h5netcdf(exp=exp,run=run)
        print x
        b = build_run(x)
   
    else:
        ds = DataSource(exp=exp,run=run)
        if attr in ['batch']:
            from PyDataSource import write_hdf5
            if args.config:
                if args.config in ['auto', 'default']:
                    config = ds._get_config_file()
                    print 'Loading default config: {:}'.format(config)
                    ds.load_config()
                else:
                    print 'Loading config: {:}'.format(args.config)
                    ds.load_config(file_name=args.config)
            
            x = to_xarray(ds) 
            print x
            b = build_run(x)
        else:
            print ds.configData



if __name__ == "__main__":
    sys.exit(main())


