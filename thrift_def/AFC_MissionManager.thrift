namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_Types.thrift"

/*
V E R S I O N       2.0
------------------------------------------------
Date: 2020 May 8

- This file and other AFC Thrift files which are on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files

*/

//Service for Mission Manager
service MissionManagerService
{
    oneway void sendPlan                (1: i32 requestId, 2: AFC_Types.Mission plan),      //Used by MMT to send the plan to Mission Manager for execution
    
    string abortMissionPlan             (1: i32 requestId, 2: i32 missionId),               //Suspends a mission plan. All vehicles with pause
    string abortVehiclePlan             (1: i32 requestId, 2: i32 vehicleId),               //Suspends a vehicle plan. The rest of the vehicles will continue as they were.
    string abortMissionPlanHard         (1: i32 requestId, 2: i32 missionId),               //Completely aborts a mission. All vehicles head back home.
    string abortVehiclePlanHard         (1: i32 requestId, 2: i32 vehicleId),               //Completely aborta a vehicle's mission. The vehicle heads back home. The rest continue.

    //The King of the network functions, the PIIINNNGGGGG
    string ping(),
}

