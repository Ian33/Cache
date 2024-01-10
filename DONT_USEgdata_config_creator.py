# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 08:06:05 2022

@author: IHiggins
"""

#import module
import configparser
 
#create configparser object
config_file = configparser.ConfigParser()
 
#define sections and their key and value pairs
config_file["sql_connection"]={
        "Driver": 'SQL Server',
        "Server": 'KCITSQLPRNRPX01',
        "Database": 'gData',
        "Trusted_Connection": 'yes'
        }

# Data is the raw data
# data = raw waterlevel for discharge
# for the purposes of the sql server data is raw data
# however there is 'pre-processing' ex: spec. conductivity and baro correction

# corrected_data is data with an offset, this could be offset data
# column is the column we are reading when pulling from sql

# corrected_data is the corrected data
# Corrected Data is stage for discharge

# Program used Discharge as discharge file
# Need to convert Discharge to D_Discharge for SQL

# Program uses utc_offset, defined for sql below
# Program uses est, defined for sql below

# Program uses lock, defined for sql below
# Program uses warning, defined for sql below
# Program uses auto_timestamp, defined for sql below
# Program uses provisional, defined for sql below

# site_sql_id is the "old g-id"

config_file['air_temperature']={
        "table" : 'tblAirTempGauging',
        "column" : 'A_Value',
        "datetime": 'A_TimeDate',
        "column": 'A_Value',
        "data": "A_Value",
        "corrected_data": "A_Value",
        "utc_offset": "A_UTCOffset",
        "est": "A_Est",
        "lock": "A_Lock",
        "warning": "A_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "A_Provisional",

        "daily_table": 'tblAirTempDaily',
        "daily_datetime": "A_Date",
        "daily_mean": "A_Mean",
        "daily_max": "A_Max",
        "daily_min": "A_Min",
        "daily_record_count": "A_RecCount",

        "daily_estimate": "A_Estimate",
        "daily_lock": "A_Lock",
        "daily_warning": "A_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "A_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 4,
        }

config_file['water_temperature']={
        "table" : 'tblWaterTempGauging',
        "column" : 'W_ValueCorrected',
        "datetime": 'W_TimeDate',
        "column": 'W_ValueCorrected',
        "data": "W_Value",
        "corrected_data": "W_ValueCorrected",
        "utc_offset": "W_UTCOffset",
        "est": "W_Est",
        #"lock": "W_Lock",
        "ice": "W_Ice",
        "depth": "W_Depth",
        #"warning": "A_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "W_Provisional",

        "daily_table": 'tblWaterTempDaily',
        "daily_datetime": "W_Date",
        "daily_mean": "W_Mean",
        "daily_max": "W_Max",
        "daily_min": "W_Min",
        "daily_record_count": "W_RecCount",

        "daily_estimate": "W_Estimate",
        "daily_lock": "W_Lock",
        "daily_ice": "W_Ice",
        "daily_depth": "W_Depth",
        "daily_warning": "W_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "W_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 3,
        }

config_file['barometer']={
        "table" : 'tblBarometerGauging',
        "column" : 'B_Value',
        "datetime": 'B_TimeDate',
        "column": 'B_Value',
        "data": "B_Value",
        "corrected_data": "B_Value",
        "utc_offset": "B_UTCOffset",
        "est": "B_Est",
        "lock": "B_Lock",
        "warning": "B_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "B_Provisional",

        "daily_table": 'tblBarometerDaily',
        "daily_datetime": "B_Date",
        "daily_mean": "B_Mean",
        "daily_max": "B_Max",
        "daily_min": "B_Min",
        "daily_record_count": "B_RecCount",

        "daily_estimate": "B_Estimate",
        "daily_lock": "B_Lock",
        "daily_warning": "B_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "B_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 12,

        }
config_file['Conductivity']={
        "table" : 'tblConductivityGauging',
        "column" : 'C_ValueCorrected',
        "datetime": 'C_TimeDate',
        "column": 'C_ValueCorrected',
        "data": "C_Value",
        "corrected_data": "C_ValueCorrected",
        "utc_offset": "C_UTCOffset",
        "est": "C_Est",
        "lock": "C_Lock",
        "warning": "C_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "C_Provisional",

        "daily_table": 'tblConductivityDaily',
        "daily_datetime": "C_Date",
        "daily_mean": "C_Mean",
        "daily_max": "C_Max",
        "daily_min": "C_Min",
        "daily_record_count": "C_RecCount",

        "daily_estimate": "C_Estimate",
        "daily_lock": "C_Lock",
        "daily_warning": "C_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "C_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 6,
        }
config_file['DO']={
        "table" : 'tblDOGauging',
        "datetime" : 'O_TimeDate',
        "column" : 'O_DO_Grams',
        }
config_file['FlowLevel']={
        "table": 'tblDischargeGauging',
        "daily_table": 'tblDischargeDaily',
        "datetime": 'D_TimeDate',
        "daily_datetime": "D_Date",
        "column": 'D_Stage',
        "data": "D_Value",
        "corrected_data": "D_Stage",
        "discharge": "D_Discharge",
        "utc_offset": "D_UTCOffset",
        "est" : "D_Est",
        "lock": "D_Lock",
        "warning": "D_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "D_Provisional",
        "observation_type": 2,

        "daily_mean": "D_MeanStage",
        "daily_max": "D_MaxStage",
        "daily_min": "D_MinStage",
        "daily_record_count": "D_RecCount",

        "discharge_mean": "D_MeanDis",
        "discharge_max": "D_MaxDis",
        "discharge_min": "D_MinDis",

        "discharge_mean": "D_MeanDis",
        "discharge_max": "D_MaxDis",
        "discharge_min": "D_MinDis",
        "daily_estimate": "D_Estimate",
        "daily_lock": "D_Lock",
        "daily_warning": "D_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "D_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",

        }
config_file['discharge']={
        "table": 'tblDischargeGauging',
        "daily_table": 'tblDischargeDaily',
        "datetime": 'D_TimeDate',
        "daily_datetime": "D_Date",
        "column": 'D_Stage',
        "data": "D_Value",
        "corrected_data": "D_Stage",
        "discharge": "D_Discharge",
        "utc_offset": "D_UTCOffset",
        "est": "D_Est",
        "lock": "D_Lock",
        "warning": "D_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "D_Provisional",

        "daily_mean": "D_MeanStage",
        "daily_max": "D_MaxStage",
        "daily_min": "D_MinStage",
        "daily_record_count": "D_RecCount",

        "discharge_mean": "D_MeanDis",
        "discharge_max": "D_MaxDis",
        "discharge_min": "D_MinDis",
        "daily_estimate": "D_Estimate",
        "daily_lock": "D_Lock",
        "daily_warning": "D_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "D_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 2,

}
config_file['Humidity'] = {
        "table" : 'tblRelativeHumidityGauging',
        "datetime" : 'H_TimeDate',
        "column" : 'H_Value',
        }
config_file['LakeLevel']={
        "table": 'tblLakeLevelGauging',
        "daily_table": 'tblLakeLevelDaily',
        "datetime": 'L_TimeDate',
        "daily_datetime": "L_Date",
        "column": 'L_Level',
        "data": "L_Value",
        "corrected_data": "L_Level",
        "utc_offset": "L_UTCOffset",
        "est": "L_Est",
        "lock": "L_Lock",
        "warning": "L_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "L_Provisional",

        "daily_mean": "L_MeanLevel",
        "daily_max": "L_MaxLevel",
        "daily_min": "L_MinLevel",
        "daily_record_count": "L_RecCount",

        "daily_estimate": "L_Estimate",
        "daily_lock": "L_Lock",
        "daily_warning": "L_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "L_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 41,
        }
config_file['water_level']={
        "table": 'tblLakeLevelGauging',
        "daily_table": 'tblLakeLevelDaily',
        "datetime": 'L_TimeDate',
        "daily_datetime": "L_Date",
        "column": 'L_Level',
        "data": "L_Value",
        "corrected_data": "L_Level",
        "utc_offset": "L_UTCOffset",
        "est": "L_Est",
        "lock": "L_Lock",
        "warning": "L_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "L_Provisional",

        "daily_mean": "L_MeanLevel",
        "daily_max": "L_MaxLevel",
        "daily_min": "L_MinLevel",
        "daily_record_count": "L_RecCount",

        "daily_estimate": "L_Estimate",
        "daily_lock": "L_Lock",
        "daily_warning": "L_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "L_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        "observation_type": 41,
        }
config_file['groundwater_level'] = {
        "table": 'tblPiezometerGauging',
        "daily_table": 'tblPiezometerDaily',
        "datetime": 'P_TimeDate',
        "daily_datetime": "P_Date",
        "column": 'P_Level',
        "data": "P_Value",
        "corrected_data": "P_Level",
        "utc_offset": "P_UTCOffset",
        "est": "P_Est",
        "lock": "P_Lock",
        "warning": "P_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "P_Provisional",
        "amount_pumped": "P_GallonsPumped",
        "pump_state": "P_Pump_On",
        "observation_type": 0,

        "daily_mean": "P_MeanLevel",
        "daily_max": "P_MaxLevel",
        "daily_min": "P_MinLevel",
        "daily_record_count": "P_RecCount",

        "daily_estimate": "P_Estimate",
        "daily_lock": "P_Lock",
        "daily_warning": "P_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "P_Provisional",
        "daily_amount_pumped": "P_GallonsPumped",
        "daily_pump_state": "P_Pummp_On",
        "daily_pump_hours": "P_PumpHours",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        }

config_file['pH']={
        "table" : 'tblpHGauging',
        "datetime" : 'pH_TimeDate',
        "column" : 'pH_ValueCorrected',
        }
config_file['Piezometer']={
        "table" : 'tblPiezometerGauging',
        "datetime" : 'P_TimeDate',
        "column" : 'P_Level',
        
        "data" : "P_Value",
        "corrected_data" : "P_Level",
        "utc_offset" : "P_UTCOffset",
        "est" : "P_Est",
        "lock" : "P_Lock",
        "warning" : "P_Warning",
        "auto_timestamp" : "AutoDTStamp",
        "provisional" : "P_Provisional",
        "gallons_pumped" : "P_GallonsPumped",
        "pump_on" : "P_Pump_On"
        }
config_file['rain']={
        "table": 'tblRainGauging',
        "daily_table": 'tblRainDaily',
        "datetime": 'R_TimeDate',
        "daily_datetime": "R_Date",
        "column": 'R_Value',
        "data": "R_Value",
        "corrected_data": "R_Value",
        "utc_offset": "R_UTCOffset",
        "est": "R_Est",
        "lock": "R_Lock",
        "warning": "R_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "Provisional",
        "snow": "R_Snow",
        "observation_type": 0,

        # Rain only has total rain, I added the mean/max/min for consistancy
        "daily_sum": "R_TotalRain",
        "daily_mean": "mean",
        "daily_max": "max",
        "daily_min": "min",

        "daily_record_count": "R_RecCount",

        "daily_estimate": "R_Estimate",
        "daily_lock": "R_Lock",
        "daily_snow": "R_Snow",
        "daily_warning": "R_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "R_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        }

config_file["rain_tips"] = {
        "table": 'tblRainGauging5minute',
        # "daily_table": 'tblRainDaily',
        "datetime": 'R_TimeDate',
        # "daily_datetime": "R_Date",
        "column": 'R_Value',
        "data": "R_Value",
        "corrected_data": "R_Value",
        "utc_offset": "R_UTCOffset",
        "est": "R_Est",
        "lock": "R_Lock",
        "warning": "R_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "Provisional",
        "snow": "R_Snow",
        "observation_type": 0,

        # Rain only has total rain, I added the mean/max/min for consistancy
        # "daily_sum": "R_TotalRain",
        # "daily_mean": "mean",
        # "daily_max": "max",
        # "daily_min": "min",

        # "daily_record_count": "R_RecCount",

        # "daily_estimate": "R_Estimate",
        # "daily_lock": "R_Lock",
        # "daily_snow": "R_Snow",
        # "daily_warning": "R_Warning",
        # "daily_auto_timestamp": "AutoDTStamp",
        # "daily_provisional": "R_Provisional",
        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name_EventData",
        }

config_file['SolarRad']={
        "table" : 'tblSolarRadiationGauging',
        "datetime" : 'S_TimeDate',
        "column" : 'S_Value',
        }
config_file['WaterTemp']={
        "table" : 'tblWaterTempGauging',
        "datetime" : 'W_TimeDate',
        "column" : 'W_ValueCorrected',
        }
config_file['turbidity']={
        "table": 'tblTurbidityGauging',
        "daily_table": 'tblTurbidityDaily',
        "datetime": 'T_TimeDate',
        "daily_datetime": "T_Date",
        "column": 'T_ValueCorrected',
        "data": "T_Value",
        "corrected_data": "T_ValueCorrected",
        "utc_offset": "T_UTCOffset",
        "est": "T_Est",
        "lock": "T_Lock",
        "warning": "T_Warning",
        "auto_timestamp": "AutoDTStamp",
        "provisional": "Provisional",
        "observation_type": 0,

        "daily_mean": "T_Mean",
        "daily_max": "T_Max",
        "daily_min": "T_Min",
        "daily_record_count": "T_RecCount",

        "daily_estimate": "T_Estimate",
        "daily_lock": "T_Lock",
        "daily_warning": "T_Warning",
        "daily_auto_timestamp": "AutoDTStamp",
        "daily_provisional": "Provisional",

        # this is to find the proper telemetry file column in GData autoloader
        "telemetry_file": "File_Name",
        }
config_file['Wind']={
        "table" : 'tblWindSpeedGauging',
        "datetime" : 'W_TimeDate',
        "column" : 'W_Value',
        }
# Site Identification
config_file['site_identification']={
    "site" : "SITE_CODE",
    "site_sql_id" : "G_ID",
    }

config_file['battery'] = {
    "table" : 'tblBatteryVoltages',
    "site_sql_id" : "G_ID",
    "datetime" : "Voltage_Date",
    "column": 'Voltage',
    "data": "Voltage",
    "corrected_data": "Voltage",
    # this is to find the proper telemetry file column in GData autoloader
    "telemetry_file": "File_Name",

    }

# Field Observations
# This gets confusing because in gData field observations are stored with metadata, an identifier "FieldVisitID" and stage in "TBLFIELDVISITINFO"
# in gData other parameters are stored in other table
# program calls observations "observation"
# in gData tblFieldVisitInfo stores waterlevel/stage as Stage_Feet

config_file['observation']={
    "observation_table" : "tblFieldVisitInfo",
    "observation_value_table" : "tblFieldData",
    "observation_id" : "FieldVisit_ID",
    "site_sql_id" : "G_ID",
    "datetime" : "Date_Time",
    "observation_number" : "Measurement_Number",
    "observation_stage" : "Stage_Feet",
    # these live in observation_values_table -> tblFieldData
    "observation_type" : "Parameter",
    "observation_value" : "Parameter_Value"
    }

# in gData tblFieldData stors other parameter values that are referenced by FieldVIsit_ID and parameter number
# FieldData_ID # this isnt really used by gData



config_file["Education"]={
        "College":"IIITA",
        "Branch" : "IT"
        }
config_file["Favorites"]={
        "Sports": "VolleyBall",
        "Books": "Historical Books"
        }

#SAVE CONFIG FILE
#SAVE CONFIG FILE

with open(r"C:\Users\ihiggins\Documents\Python\Cache gData\gdata_config.ini","w") as file_object:
    config_file.write(file_object)
print("Config file 'gdata_config.ini' created")

#SAVE CONFIG FILE
with open(r"C:\Users\ihiggins\Documents\Python\Autoloader\gdata_config.ini","w") as file_object:
    config_file.write(file_object)
print("Config file 'gdata_config.ini' created")





#print file content
read_file=open("gdata_config.ini","r")
content=read_file.read()
print("content of the config file is:")
print(content)
