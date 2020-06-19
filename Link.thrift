/*
* Enums 
*/
enum StatusEnum {
    STARTED = 1,
    STOPPED = 2
}

enum ReplyEnum {
    OK = 1,
    ERROR = 2
}

/*
* Struct to send to MMT for getList 
*/
struct AlgorithmStruct {
    1: string algorithm_name,
    2: i32 id,
    3: string description,
    4: StatusEnum status,
    5: string url_api,
    6: string url_web
}

/*
* Service
*/
service mmtLink{
    string ping(),
    list<AlgorithmStruct> getList(),
    ReplyEnum start(1: i32 id),
}