namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"

/*
V E R S I O N       2.0
------------------------------------------------
Date: 2020 May 8

- This file and other AFC Thrift files which on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
- Sensor types and their data structures are overhauled (compared to prev version 1.2). If you use those structs, make sure to update to this version

*/

enum SensorType
{
    grass,
    flow_meter,
    soil,
    environmental,
    asset_tracking,
    silage,
    collar,  
}

enum ObservationType
{
	air_humidity,
    air_pressure,
    air_temperature,
	altitude,
	battery,
	crude_protein,
	dry_matter,
	d_value,
	electrical_conductivity_bulk,
	electrical_conductivity_pores,
	fibre,
	latitude,
	longitude,
	protein,
	relative_dielectric_constant,
	soil_humidity,
	soil_matrix_potential,
	soil_temperature,
	solar_radiation,
	speed,
	temperature_teros12,
	temperature_teros21,
	volumetric_water_content_mineral_soil,
	water_consumption,	
}


struct SensorData {
    1: string                   sensorUid,
    2: SensorType               sensorType,
	3: ObservationType          obserType,
    4: string                   unit,
    5: double                   value,
    6: AFC_Types.Position       sensorPosition,
	7: i64                      lastUpdate,
}

struct CollarData {
    1: string                   collarUid,
	2: AFC_Types.Position       collarPosition,
	3: double                   temperature,
	4: bool                     resourceAlarm,
	5: bool                     locationAnomaly,
	6: bool                     temperatureAnomaly,
	7: bool                     distanceAnomaly,
	8: bool                     positionAnomaly,
	9: i64                      lastUpdate,
}
