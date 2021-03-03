val api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
val schoolListId = "2da280f42766"
val schoolIdsId = "f53b6f4631d6"




fun getSchoolListFromCloud(): List<String>{
    // Request a string response from the provided URL.
    return listOf("Ecole Creactive", "Ecole Test")
}

fun getJsonDataFromCloud(schoolName: String, pwd: String): String{
    return "{}"
}

suspend fun uploadInThread(){
}

class JSONSchoolList(val school_list: List<String>)