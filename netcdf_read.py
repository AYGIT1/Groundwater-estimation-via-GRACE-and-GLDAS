import netCDF4
import os
import datetime
import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np


# Enter coordinates
# IMPORTANT! Check your order of coord. and time params, it might be (lat, lon) or (lon, lat) something else!!
# You should check this from variable shape
in_lat = 30.5
in_lon = 38.5

## File locations
# GRACE-2002_2017
directory_grac = "../db/grace-2002-2017" # Directory of GRACE Data (.nc4)
suffix_grac = "GRAC_GFZOP_BA01_0600_LND_v03" # GRACE file suffix
var_name_grac = "lwe_thickness" #Name of the desired data in GRACE files

# GRACE-2018_2020 (GRFO)
directory_grfo = "../db/grace-2018-2020" # Directory of GRFO Data (.nc4)
suffix_grfo = "GRFO_GFZOP_BA01_0600_LND_v03" # GRFO file suffix
var_name_grfo = "lwe_thickness" #Name of the desired data in GRFO files

# GLDAS
directory_gldas = "../db/gldas"
suffix_gldas = "GLDAS-NOAH_1deg_tws_anomaly_monthly"
var_name_gldas = "TWS_monthly"

# GPM-IMERG
directory_imerg = "../db/gpm-imerg"
suffix_imerg = "3B-MO.MS.MRG.3IMERG"
var_name_imerg = "precipitation"


def geo_idx(dd, dd_array):
    """
    search for nearest decimal degree in an array of decimal degrees and return the index.
    np.argmin returns the indices of minium value along an axis.
    so subtract dd from all values in dd_array, take absolute value and find index of minium.
    Copied from Eric Bridger @ stackoverflow
    """
    geo_idx = (np.abs(dd_array - dd)).argmin()
    return geo_idx


def import_nc4(directory, suffix, var_name):
    """Imports the required data from nc4 file to a python dictionary with date as keys and data as values"""
    # directory: Directory of the netCDF files
    # suffix: Partial name of the netCDF files that will be imported
    # var_name: Name of the netCDF4 variable that will be imported from file
    file_list = sorted(os.listdir(directory))
    run_once = False
    temp_dict = {}
    lat_idx = 1
    lon_idx = 1
    for file in file_list:
        if suffix in file and file.endswith(".nc"):
            f = netCDF4.Dataset(directory + "/" + file)
            if not run_once: # Run the indented rows once
                # Import  latitude and longitude data from file to corresponding lists.
                lats = f.variables['lat'][:]
                lons = f.variables['lon'][:]

                # Find nearest coordinates to the input coordinates.
                lat_idx = geo_idx(in_lat, lats)
                lon_idx = geo_idx(in_lon, lons)
                # Debug stuff
                # print("lats:", lats,"*****", "lons:", lons)
                # print(len(lats), len(lons))
                # print(f.variables['lat'][lat_idx])
                # print(f.variables['lon'][lon_idx])
                # print(lat_idx, lon_idx)

                run_once = True

            # Import date from file and convert to python datetime format
            nc_time = f.time_coverage_end
            # Quick fix for conversion to datetime object
            nc_time = nc_time.replace("Z", "")
            node_datetime = datetime.datetime.fromisoformat(nc_time) #.strftime("%m/%Y")
            var = f.variables[var_name]
            # print(var)

            node_data = round(float(var[0, lat_idx, lon_idx]), 8)
            # print(node_data)

            # Add data to dictionary: date as keys, data as values
            temp_dict[node_datetime] = node_data
    return temp_dict


def import_hdf5(directory, suffix, var_name):
    group_name = "Grid" # HDF5 file group name
    file_list = sorted(os.listdir(directory))
    run_once = False
    temp_dict = {}
    lat_idx = 1
    lon_idx = 1
    for file in file_list:
        if suffix in file and file.endswith(".HDF5"):
            f = netCDF4.Dataset(directory + "/" + file)
            group = f.groups[group_name]
            var = group.variables[var_name]
            if not run_once:  # Run the indented rows once
                # Import  latitude and longitude data from file to corresponding lists.
                lats = group.variables['lat'][:]
                lons = group.variables['lon'][:]

                # Find nearest coordinates to the input coordinates.
                lat_idx = geo_idx(in_lat, lats)
                lon_idx = geo_idx(in_lon, lons)
                # print(var)
                run_once = True

            # Python type conversion
            node_data = float(var[0, lon_idx, lat_idx])
            print(node_data)


def plot_grac(dict_file):
    """plotting options for GRAC data"""
    dates = matplotlib.dates.date2num(list(dict_file.keys()))
    # Convert from meters to mm
    new_lwe = [i * 1000 for i in list(dict_file.values())]
    plt.plot_date(dates, new_lwe, ".", linestyle='solid')
    # Create trendline
    coef = np.polyfit(dates, new_lwe, 1)
    trendline = np.poly1d(coef)
    xx = np.linspace(dates.min(), dates.max(), len(dates))
    plt.plot(xx, trendline(xx))
    print("GRACE trendline coeffs:", trendline)
    print("Yearly variation:", coef[0] * 360, "mm")

    plt.title("GRAC")
    plt.ylabel("Eşdeğer Su Yüksekliği (mm)")
    plt.xlabel("Tarih")
    plt.xticks(rotation=45)
    plt.legend(["Grace"], loc='upper left',)


def plot_gldas(dict_file):
    """plotting options for GLDAS data"""
    dates = matplotlib.dates.date2num(list(dict_file.keys()))
    vals = list(dict_file.values())
    plt.plot_date(dates, vals, ".", linestyle='solid')

    plt.title("GLDAS")
    plt.ylabel("Eşdeğer Su Yüksekliği (mm)")
    plt.xlabel("Tarih")
    plt.xticks(rotation=45)
    plt.legend(["GLDAS"], loc='upper left')
    # Create trendline
    coef = np.polyfit(dates, vals, 1)
    trendline = np.poly1d(coef)
    xx = np.linspace(dates.min(), dates.max(), len(dates))
    plt.plot(xx, trendline(xx))
    print("GLDAS trendline coeffs:", trendline)
    print("Yearly variation:", coef[0] * 360, "mm")


def plot_imerg(dict_file):
    """plotting options for GPM-IMERG data"""
    dates = matplotlib.dates.date2num(list(dict_file.keys()))
    vals = list(dict_file.values())
    plt.plot_date(dates, vals, ".", linestyle='solid')

    plt.title("IMERG")
    plt.ylabel("Ortalama Yağış (mm/hr)")
    plt.xlabel("Tarih")
    plt.xticks(rotation=45)
    plt.legend(["IMERG"], loc='upper left')
    # Create trendline
    # coef = np.polyfit(dates, vals, 1)
    # trendline = np.poly1d(coef)
    # xx = np.linspace(dates.min(), dates.max(), len(dates))
    # plt.plot(xx, trendline(xx))
    # print("IMERG trendline coeffs:", trendline)
    # # Print yearly variation
    # print(coef[0]*360)


def plot_overwrite():
    """Overwrite plotting options"""

    plt.grid(True, which="both")
    plt.title("Nokta: #, Koordinatlar: " + str(in_lat) + "K, " + str(in_lon) + "D")
    plt.ylabel("Eşdeğer Su Yüksekliği (mm)")
    plt.xlabel("Tarih")
    plt.xticks(rotation=45)
    plt.legend(["GRACE","GRACE Trendline", "GLDAS", "GLDAS Trendline", "IMERG"], loc='best')
    plt.subplots_adjust(bottom=0.15, right=0.95, top=0.95, left=0.1)


dict_grac = import_nc4(directory_grac, suffix_grac, var_name_grac)
dict_grfo = import_nc4(directory_grfo, suffix_grfo, var_name_grfo)
# join GRACE dictionaries
dict_grac.update(dict_grfo)

dict_gldas = import_nc4(directory_gldas, suffix_gldas, var_name_gldas)

# dict_imerg = import_hdf5(directory_imerg, suffix_imerg, var_name_imerg)

# Font size
plt.rcParams.update({'font.size': 14})

plot_grac(dict_grac)
plot_gldas(dict_gldas)
# plot_imerg(dict_imerg)
plot_overwrite()
plt.show()


