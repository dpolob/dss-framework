namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"
include "AFC_Sensors.thrift"

/*
V E R S I O N       2.0     
------------------------------------------------
THIS IS A PRELIMINARY VERSION. SOME ISSUES ARE STILL UNRESOLVED. FIND AND RESOLVE ALL COMMENTS IN THE CODE MARKED WITH "//NOTE"
------------------------------------------------
Date: 2020 June 3

- This file and other AFC Thrift files which on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
- Sensor types and their data structures are overhauled (compared to prev version 1.2). If you use those structs, make sure to update to this version

Date: 2020 June 18
- The search region is defined as a circle with a centre (Position) and a radius.
- The times for historical functions are changed to 64-bit
*/



//Service for Semantic Queries.
//----------------------------------------------
// Notice that most functions in this service are blocking functions. There is no callback defined in the MmtService for sending the result. 
//----------------------------------------------
service SemanticQueryService
{
    //Mission Related Functions
	list<AFC_Types.Vehicle>       getAllVehicles          (1: i32 requestId),				              //Sends a list of all currently available vehicules. Called by MMT once at startup
    list<AFC_Types.MissionTag>    getAllMissions          (1: i32 requestId),                             //Send a list of all missions
    list<AFC_Types.MissionTag>    getOngoingMissions      (1: i32 requestId),                             //Send a list of all missions that contain unfinished tasks
    AFC_Types.Mission             getMissionById          (1: i32 requestId, 2: i32 missionId),               //Send a mission given the ID
    AFC_Types.Vehicle             getVehicle              (1: i32 requestId, 2: i32 vid),                 //Send information related to a vehicle based on the Id

        
    //Query Functions for sensors, collars and vehiclues for last values available in database
	list<AFC_Sensors.SensorData> querySensorLastData                    (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius),     //All last value observations from sensors measured in a region 
	list<AFC_Sensors.SensorData> querySensorLastDataBySensorUid         (1: i32 requestId, 2: string sensorUid),                                   //All last value observations of sensor with this Uid 
	list<AFC_Sensors.SensorData> querySensorLastDataBySensorType        (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: AFC_Sensors.SensorType sensorType),     //All last value observations of a given sensor type measured in a region 
	list<AFC_Sensors.SensorData> querySensorLastDataByObservationType   (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: AFC_Sensors.ObservationType obserType),  //All last value observations of a given type measured in a region 
	
	list<AFC_Sensors.CollarData> queryCollarLastData                    (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius),		//All last value data from collars in a region
	list<AFC_Sensors.CollarData> queryCollarLastDataByCollarUid         (1: i32 requestId, 2: string collarUid),		                            //Last value data from a given collar

    list<AFC_Types.StateVector> queryVehicleLastStateVector             (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius),   //All last value data of vehicles' state vectors in a region
	list<AFC_Types.StateVector> queryVehicleLastStateVectorByVehicleId  (1: i32 requestId, 2: i32 vehicleId ),                                      //All last value data of a vehicle's state vectors specified by a vehicleId

    //Historical Queries
    //Same as above functions, but instead of the last value, they return all data within a given timeframe. Times are UNIX time
	
	//NOTE: querySensorHistoricalData, querySensorHistoricalDataBySensorType and querySensorHistoricalDataByObservationType return a maximum of 100 data for pair {sensorUid, ObservationType}
	//NOTE: querySensorHistoricalDataBySensorUid returns a maximum of 500 data for ObservationType
    list<AFC_Sensors.SensorData> querySensorHistoricalData                    (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: i64 startTime, 5: i64 endTime),	
	list<AFC_Sensors.SensorData> querySensorHistoricalDataBySensorUid         (1: i32 requestId, 2: string sensorUid,        3: i64 startTime, 4: i64 endTime),	
	list<AFC_Sensors.SensorData> querySensorHistoricalDataBySensorType        (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: AFC_Sensors.SensorType sensorType,     5: i64 startTime, 6: i64 endTime),        
	list<AFC_Sensors.SensorData> querySensorHistoricalDataByObservationType   (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: AFC_Sensors.ObservationType obserType, 5: i64 startTime, 6: i64 endTime),    
	
	//NOTE: queryCollarHistoricalData returns a maximum of 100 data for collarUid
	//NOTE: queryCollarHistoricalDataByCollarUid returns a maximum of 500
	list<AFC_Sensors.CollarData> queryCollarHistoricalData                    (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: i64 startTime, 5: i64 endTime),			
	list<AFC_Sensors.CollarData> queryCollarHistoricalDataByCollarUid         (1: i32 requestId, 2: string collarUid,        3: i64 startTime, 4: i64 endTime),		        

	//NOTE: queryVehicleHistoricalStateVectors returns a maximum of 100 data for vehicleId
	//NOTE: queryVehicleHistoricalStateVectorByVehicleId returns a maximum of 500
    list<AFC_Types.StateVector> queryVehicleHistoricalStateVectors            (1: i32 requestId, 2: AFC_Types.Position regionCentre, 3: i32 radius, 4: i64 startTime, 5: i64 endTime),  
	list<AFC_Types.StateVector> queryVehicleHistoricalStateVectorByVehicleId  (1: i32 requestId, 2: i32 vehicleId,           3: i64 startTime, 4: i64 endTime),                        


    //Store Functions    
    oneway void storeEvent                      (1: i32 requestId, 2:i32 missionId, 3:i32 vehicleId, 4:i32 subtype, 5:string description, 6:i64 timeReference),  //If MMT detects or is requested to (abort, etc), the event is reported to MW with this function 

 
    //The Mighty Everlasting PINGGGGGGG
    string ping(),
}
