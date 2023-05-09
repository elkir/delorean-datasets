

#%%  Import all the packages needed to explore grib data
import re
import xarray as xr
import numpy as np
import argparse


from pathlib  import Path



# insert path to src folder no matter from where the notebook is run
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Check where we are, and what we have access to
print("Cwd: ",Path.cwd())
print("Path: ",sys.path)


from src.data_loading.load_ens import (load_ens_data_ED)



# =======================================
#%% Flags and directories
## Flags and directories
# =========================================
load_full_D = True
drop_wind_components = True
calculate_diffs = True


#%%

def calculate_variance(ds, vars=["t2m","d2m","stl4","ssrd","strd","w10","w100"],start_time=None):
    ds_var = ds[vars].resample(step="1D").mean().var(dim=["number"]
                        ).mean(["latitude","longitude"])
    if start_time==None:
        start_time=ds_var.time
    ds_var = ds_var.assign_coords(valid_time=ds_var.step+start_time)
    return ds_var
    
#ED only
def extract_var(filenameE, start_time=None):
    fn2_E = filenameE
    fn2_D = re.sub(r'v(\d\d)e', r'v\1d', filenameE)
    ds, dsD = load_ens_data_ED(fn2_E, fn2_D,
                            load_full_D=True,
                            drop_wind_components=True,
                            temperature_in_C=True,
                            calculate_diffs=True
                            )

    #calculate variance over number latitude and longitude
    ds_var = calculate_variance(ds.isel(step=slice(None,269-121)
                            ), start_time=start_time)
    dsD_var = calculate_variance(dsD,start_time=start_time)
    del ds, dsD
    return ds_var, dsD_var



def main():
    parser = argparse.ArgumentParser(description='Process GRIB files and compute variance')
    parser.add_argument('export_filename', type=str, help='Base name for the output NetCDF files')
    parser.add_argument('grib_files', nargs='+', type=str, help='GRIB files to process')
    args = parser.parse_args()

    export_filename = args.export_filename
    grib_files = args.grib_files

    all_ds_var_E = []
    all_ds_var_D = []

    for file in grib_files:
        ds_var_E, ds_var_D = extract_var(file)
        all_ds_var_E.append(ds_var_E)
        all_ds_var_D.append(ds_var_D)

    combined_ds_var_E = xr.concat(all_ds_var_E, dim="time")
    combined_ds_var_D = xr.concat(all_ds_var_D, dim="time")

    combined_ds_var_E.to_netcdf(f"{export_filename}_E.nc")
    combined_ds_var_D.to_netcdf(f"{export_filename}_D.nc")

if __name__ == "__main__":
    main()

