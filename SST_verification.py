import math
import netCDF4
from netCDF4 import Dataset

import urllib
from bs4 import BeautifulSoup
import re

# define
long_time_forecast = False #True for long_time_forecast and false for short_time_forecast
LOCATION = [[130,30],[-130,-30]]#all the location  to be Verified
long_time = ['0802','0803','0804']   #seven consecutive days
short_time = ['0802','0803','0804']

day = 24
moment = [0,9,15,21] # the observation moment during a day
file_ = r'C:\Users\89320\Desktop\test'  # Where to store the downloaded files(The location where the current program is saved)
dict = {moment[0]:'AM_N',moment[1]:'AM_D',moment[2]:'PM_D',moment[3]:'PM_N'}
E_long = []
E_short = []

for location in LOCATION:
    longitude , latitude = location[0] , location[1]
    if  long_time_forecast:
        #Verification of the model's long-term forecasting capabilities
        for data in long_time:
            e = []
            time = long_time.index(data)*day
            for hours in moment:
                rawurl_forecast = 'https://www.ncei.noaa.gov/thredds-coastal/fileServer/hycom_sfc/2020'+ long_time[0] +'/hycom_glb_sfc_u_2020'+ long_time[0] +'00_t'+ str(time+hours).zfill(3) +'.nc'
                rawurl_observation = 'ftp://ftp.star.nesdis.noaa.gov/pub/socd2/coastwatch/sst/nrt/l3s/'+ dict[hours][:2].lower() +'/2020/214/2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc'

                file_name = file_ + '\\' + 'hycom_glb_sfc_u_2020'+ long_time[0] +'00_t' + str(time+hours).zfill(3) + '.nc'  # The name of the saved file
                urllib.request.urlretrieve(rawurl_forecast, file_name)  # download files via url
                forecast = Dataset('hycom_glb_sfc_u_2020'+ long_time[0] +'00_t'+ str(time+hours).zfill(3) +'.nc')

                file_name = file_ + '\\' + '2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc'  # The name of the saved file
                urllib.request.urlretrieve(rawurl_observation, file_name)  # download files via url
                observation = Dataset('2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc')

                sst = forecast.variables['water_temp']
                SST = observation.variables['sea_surface_temperature']

                # select the nearest result relative to the specified latitude and longitude from the HYCOM
                if longitude < 0:
                    n = longitude + 360
                else:
                    n = longitude
                n = n / 360 * 4500 + 1
                m = (latitude + 80) / 160 * 2000 + 1
                n = round(n)
                m = round(m)

                forecast_sst = sst[0, 0, m, n]

                # the real Latitude and longitude about the location of HYCOM
                n = (n - 1) / 4500 * 360
                if longitude < 0:
                    real_longitude = n - 360
                else:
                    real_longitude = n
                real_latitude = (m - 1) / 2000 * 160 - 80

                # calculate the corresponding result in the observation data via Interpolation
                y_down = math.floor((real_longitude + 180.01) * 50)
                y_up = math.ceil((real_longitude + 180.01) * 50)
                x_down = math.floor((real_latitude - 90.01) * (-50))
                x_up = math.ceil((real_latitude - 90.01) * (-50))

                observation_SST = (SST[0, x_down, y_down] + SST[0, x_down, y_up] + SST[0, x_up, y_down] + SST[0, x_up, y_up]) / 4 - 272.15

                Absolute_error = forecast_sst - observation_SST
                e.append(Absolute_error)
            E_long.append(e)
        E_long.append(location)
        f = open("E_long.txt", "w")
        f.write(str(E_long))
        f.close()
    else:
        #Verification of the model's short-term forecasting capabilities

        for data in short_time:
            e = []
            #time = (int(data[-1])-1)*day
            for hours in moment:
                rawurl_forecast = 'https://www.ncei.noaa.gov/thredds-coastal/fileServer/hycom_sfc/2020'+ data +'/hycom_glb_sfc_u_2020'+ data +'00_t'+ str(hours).zfill(3) +'.nc'
                rawurl_observation = 'ftp://ftp.star.nesdis.noaa.gov/pub/socd2/coastwatch/sst/nrt/l3s/'+ dict[hours][:2].lower() +'/2020/214/2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc'

                file_name = file_ + '\\' + 'hycom_glb_sfc_u_2020'+ data +'00_t' + str(hours).zfill(3) + '.nc'  # The name of the saved file
                urllib.request.urlretrieve(rawurl_forecast, file_name)  # download files via url
                forecast = Dataset('hycom_glb_sfc_u_2020'+ data+'00_t'+ str(hours).zfill(3) +'.nc')

                file_name = file_ + '\\' + '2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc'  # The name of the saved file
                urllib.request.urlretrieve(rawurl_observation, file_name)  # download files via url
                observation = Dataset('2020'+ data +'120000-STAR-L3S_GHRSST-SSTsubskin-LEO_'+ dict[hours] +'-ACSPO_V2.80B04-v02.0-fv01.0.nc')

                sst = forecast.variables['water_temp']
                SST = observation.variables['sea_surface_temperature']

                # select the nearest result relative to the specified latitude and longitude from the HYCOM
                if longitude < 0:
                    n = longitude + 360
                else:
                    n = longitude
                n = n / 360 * 4500 + 1
                m = (latitude + 80) / 160 * 2000 + 1
                n = round(n)
                m = round(m)

                forecast_sst = sst[0, 0, m, n]

                # the real Latitude and longitude about the location of HYCOM
                n = (n - 1) / 4500 * 360
                if longitude < 0:
                    real_longitude = n - 360
                else:
                    real_longitude = n
                real_latitude = (m - 1) / 2000 * 160 - 80

                # calculate the corresponding result in the observation data via Interpolation
                y_down = math.floor((real_longitude + 180.01) * 50)
                y_up = math.ceil((real_longitude + 180.01) * 50)
                x_down = math.floor((real_latitude - 90.01) * (-50))
                x_up = math.ceil((real_latitude - 90.01) * (-50))

                observation_SST = (SST[0, x_down, y_down] + SST[0, x_down, y_up] + SST[0, x_up, y_down] + SST[0, x_up, y_up]) / 4 - 272.15

                Absolute_error = forecast_sst - observation_SST
                e.append(Absolute_error)
            E_short.append(e)
        E_short.append(location)
        f = open("E_short.txt", "w")
        f.write(str(E_short))
        f.close()