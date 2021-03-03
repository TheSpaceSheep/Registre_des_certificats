package com.example.registredescertificats

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.MenuItem
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import getJsonDataFromCloud
import kotlinx.android.synthetic.main.activity_change_school.*
import java.io.File
import com.google.gson.GsonBuilder
import com.google.gson.reflect.TypeToken

val api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
val schoolListId = "2da280f42766"
val schoolIdsId = "f53b6f4631d6"


class ChangeSchoolActivity : AppCompatActivity() {
    var ok = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_change_school)
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.setDisplayHomeAsUpEnabled(true);

        val url = "https://json.extendsclass.com/bin/$schoolListId"
        val queue = Volley.newRequestQueue(applicationContext)
        val stringRequest = StringRequest(Request.Method.GET, url,
                Response.Listener<String> { response ->
                    val gson = GsonBuilder().setPrettyPrinting().create()
                    val jsonSchoolListType = object : TypeToken<JSONSchoolList>() {}.type
                    val jsonSchoolList: JSONSchoolList = gson.fromJson(response, jsonSchoolListType)
                    val listeEcoles = jsonSchoolList.school_list
                    val ecoleArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listeEcoles)
                    ecole_actv.setAdapter(ecoleArrayAdapter)
                },
                Response.ErrorListener {println("That Didn't Work")})
        queue.add(stringRequest)
        queue.cache.clear()

    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        val id = item.itemId
        return if(id == android.R.id.home){
            finish()
            true
        } else{
            super.onOptionsItemSelected(item)
        }
    }

    fun validerCallback(v: View){
        val name = ecole_actv.text.toString()
        val pwd = pwd_edittext.text.toString()
        val queue = Volley.newRequestQueue(applicationContext)
        val url_1 = "https://json.extendsclass.com/bin/$schoolIdsId"

        val fetchSchoolIds = StringRequest(Request.Method.GET, url_1,
                Response.Listener<String> { response ->
                    val gson = GsonBuilder().setPrettyPrinting().create()
                    val schoolIdsType = object: TypeToken<Map<String, String>>() {}.type
                    val schoolIds: Map<String, String> = gson.fromJson(response, schoolIdsType)
                    val schoolId = schoolIds[name] ?: ""
                    if(schoolId == ""){
                       println("Error fetching school id")
                    }

                    val loadSchool = object: StringRequest(Request.Method.GET, "https://json.extendsclass.com/bin/$schoolId",
                            Response.Listener<String> { response2 ->
                                val regFile = File(applicationContext.filesDir, "registre_certificats.json")
                                regFile.writeText(response2)

                                val idFile = File(applicationContext.filesDir, "school_id.txt")
                                idFile.writeText(schoolId)

                                val pFile = File(applicationContext.filesDir, "p.rc")
                                pFile.writeText(pwd)

                                val nameFile = File(applicationContext.filesDir, "school_name.txt")
                                nameFile.writeText(name)

                                println(response2)

                                intent.putExtra("schoolName", name)
                                setResult(Activity.RESULT_OK, intent)
                                ok = true
                                finish()
                            },
                            Response.ErrorListener {response2 -> println(response2)})
                            {
                                override fun getHeaders(): MutableMap<String, String> {
                                    val headers = HashMap<String, String>()
                                    headers["Security-key"] = pwd
                                    return headers
                                }
                            }

                    println(response)
                    queue.add(loadSchool)
                },
                Response.ErrorListener {response -> println(response)})
        queue.add(fetchSchoolIds)
        queue.cache.clear()
    }

    override fun onDestroy(){
        if(!ok){
            intent.putExtra("schoolName", "")
            setResult(Activity.RESULT_OK, intent)
        }
        super.onDestroy()
    }
}

class JSONSchoolList(val school_list: List<String>)
