namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"

/*
V E R S I O N       2.0
------------------------------------------------
Date: 2020 June 10

- This file and other AFC Thrift files which on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
- This is a new addition to the Thrift definitions in AFC

*/



//Service for Mobile MMT
//----------------------------------------------
service MobileMmtService
{
    //  REQUESTID:
    //- All of the functions that contain a "requestId" field, must return the same value back to MMT when calling MMT Service back in response to a function call from MMT or if they want to call sendError on MMT.
    //- If the function call is not in response to a previous request by MMT, set the "requestId" to any negative value.

    oneway void sendMission                     (1: i32 requestId, 2: AFC_Types.Mission currentMission),            //Called by MainMMT or MissionManager to send the mission to the Mobile Device(s)
	oneway void sendMessage                     (1: i32 requestId, 2: i32 senderId,  3: string message),            //Called by anyone when they need to send text messages to MobileMMT


    //Ping, Ping, Ping! You are dead now
    string ping(),
}
