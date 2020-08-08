namespace java com.afarcloud.thrift
namespace csharp AFarCloudGUI.Comm.Thrift
namespace cpp afarcloud

include "AFC_DSS_Types.thrift"

/*
V E R S I O N       2.0
------------------------------------------------
Date: 2020 June 8

- This file and other AFC Thrift files which are on versions 2.x are the versions used for the 2nd year demos
- The main change is the separation of different definitions and services into different files
- This file is a new addition to the Thrift system in AFC. Is used only for MMT and DSS Services. If you are involved in something else, this is not the droid you are looking for.
- All of the functions that contain a "requestId" field, must return the same value back to MMT when calling MMT Service back in response to a function call from MMT or if they want to call sendError on MMT.
*/

//Service for DSS
//----------------------------------------------
service DssService
{
    list<AFC_DSS_Types.DssAlgorithm>      getAlgorithmList(),                                       //Gets a list of all available Algorithms from the DSS Manager (@Diego: Is this the correct name?)

    oneway void                           startAlgorithm    (1:i32 requestId, 2:i32 algorithmId),   //Asks the DSS Manager to start an algorithm. "requestId" is explained in the top comments. "algorithmId" is the Id of the algorithm to start
    AFC_DSS_Types.AlgorithmStatus         getAlgorithmStatus(1:i32 requestId, 2:i32 algorithmId),   //Asks the DSS Manager about the current status of an algorithm service. 

    oneway void                           sendIpAddress     (1: string ip),                             
    
    //Bow to the Ping!
    string ping(),
}
