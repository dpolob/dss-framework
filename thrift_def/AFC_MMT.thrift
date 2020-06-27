namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"
include "AFC_Sensors.thrift"
include "AFC_DSS_Types.thrift"


/*
V E R S I O N       2.0
------------------------------------------------

Date: 2020 June 23

- Functions for receiving the results back from DSS are revised. New ones are added


Date: 2020 June 10

- This file and other AFC Thrift files which on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
*/

/*
T O D O
------------------------------------------------

 - The Error codes for the sendError function need to be defined. 
*/

//Service for MMT
//----------------------------------------------
service MmtService
{
    //  REQUESTID:
    //- All of the functions that contain a "requestId" field, must return the same value back to MMT when calling MMT Service back in response to a function call from MMT or if they want to call sendError on MMT.
    //- If the function call is not in response to a previous request by MMT, set the "requestId" to any negative value.

	oneway void stateVectorUpdate               (1: i32 requestId, 2: AFC_Types.StateVector stateVector)                                            //Called by MissionManager or SQ to update the state vector for a vehicle

    //NoteToSelf: I guess this is not needed anymore now that we are remvoing oneway functions from SQ, but maybe MM might want to use it? We keep it for now.
    oneway void sensorDataUpdate                (1: i32 requestId, 2: list<AFC_Sensors.SensorData> sensorData)                                      //Called by SQ to update the sensor readings.

    oneway void sendPlan                        (1: i32 requestId, 2: AFC_Types.Mission plan),							                            //Called by Planners in response to a computePlan. Sends the plan to Mmt
	oneway void sendError                       (1: i32 requestId, 2: i32 errorId,   3: string errorMessage),	                                    //Called by all in case something goes wrong. 
	oneway void sendAlarm						(1: i32 requestId, 2: i32 missionId, 3: AFC_Types.Alarm alarm),                                     //Called by the MM whenever there is a new alarm.
    oneway void sendMessage                     (1: i32 requestId, 2: i32 senderId,  3: string message),                                            //Celled by anyone when they need to send text messages to MMT
    oneway void sendMissionStatusReport         (1: i32 requestId, 2: i32 missionId, 3: AFC_Types.TaskCommandStatus status),				        //Called by MM whenever there is a new update for a mission.
    oneway void sendTaskStatusReport            (1: i32 requestId, 2: i32 missionId, 3: i32 taskId,    4: AFC_Types.TaskCommandStatus status),	    //Called by MM whenever there is a new update for a task in a mission.
    oneway void sendCommandStatusReport         (1: i32 requestId, 2: i32 missionId, 3: i32 commandId, 4: AFC_Types.TaskCommandStatus status),      //Called by MM whenever there is a new update for a command in a mission.

    //Functions used by DSS to send back results to MMT    
    oneway void sendDssResultNumber	            (1:i32 requestId, 2:i32 algorithmId, 3:list<AFC_DSS_Types.ResponseNumber> result),	                        // We send a list in case someone need to send more than one
	oneway void sendDssResultBoolean	        (1:i32 requestId, 2:i32 algorithmId, 3:list<AFC_DSS_Types.ResponseBoolean> result),
	oneway void sendDssResultString	            (1:i32 requestId, 2:i32 algorithmId, 3:list<AFC_DSS_Types.ResponseString> result),
	oneway void sendDssResultPosition           (1:i32 requestId, 2:i32 algorithmId, 3:list<AFC_DSS_Types.ResponsePosition> result),

    //No Pingy, No Party!
    string ping(),
}
