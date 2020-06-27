namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"
include "AFC_Sensors.thrift"

/*
V E R S I O N       2.0
------------------------------------------------
Date: 2020 June 25

- New data types for algorithm results are added


Date: 2020 June 9

- This file and other AFC Thrift files which on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
- Sensor types and their data structures are overhauled (compared to prev version 1.2). If you use those structs, make sure to update to this version
- This is a new addition to the Thrift system in AFC. Is used only for MMT and DSS Services. If you are involved in something else, this is not the droid you are looking for.
*/

enum AlgorithmStatus
{
    Available,                              //The Algorithm Service is up and running
    NotAvailable,                           //The Algorithm Service is down / not-accessible
    Busy,                                   //The Algorithm Service is up but is not available at the moment, check back later please!
}

struct DssAlgorithm
{
    1: i32               Id,                //Do I really need to explain what an ID is?
    2: string            Name,              //It is the name of course
    3: string            Description,       //Please make sure that the algorithms have this field correctly filled. Think of the poor operator who might need to know what an Algorithm actually does.
    4: AlgorithmStatus   Status,            //Check the Enum above
    5: string            WebInterfaceUrl,   //The URL to the web interface that allows modifying the algorithm settings. This is NOT the Algorithm's API URL
}

// Here are the structs for sending the algorithm results, more will be added later

struct ResponseNumber
{
	1: i64  			            Timestamp,			//Time of recomendation
	2: AFC_Sensors.ObservationType	Observation,		//Description of what recomendation is sent (water, temperature, etc)
	3: string			            Units,				//Units of measure according to http://qudt.org/vocab/unit/,
	4: double			            Result,				//Recommendation 
}

struct ResponseBoolean
{
	1: i64  			            Timestamp,			//Time of recomendation
	2: AFC_Sensors.ObservationType	Observation,		//Description of what recomendation is sent (water, temperature, etc)
	3: string			            Units,				//Units of measure according to http://qudt.org/vocab/unit/,
	4: bool				            Result,				//Recommendation (true or false)
}

struct ResponseString
{
	1: i64   			            Timestamp,			//Time of recomendation
	2: AFC_Sensors.ObservationType	Observation,		//Description of what recomendation is sent (water, temperature, etc)
	3: string			            Units,				//Units of measure according to http://qudt.org/vocab/unit/,
	4: string			            Result,				//Recommendation (text or URL for images)
}

struct ResponsePosition
{
	1: i64  			            Timestamp,		//Time of recomendation
	2: AFC_Sensors.ObservationType	Observation,	//Description of what recomendation is sent (water, temperature, etc)
	3: string			            Units,			//Units of measure according to http://qudt.org/vocab/unit/,
	4: AFC_Types.Position           Result,			//The location in lng,lat,alt
}