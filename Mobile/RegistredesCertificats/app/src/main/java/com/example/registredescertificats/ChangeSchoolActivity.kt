package com.example.registredescertificats

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.snackbar.Snackbar
import androidx.appcompat.app.AppCompatActivity
import createErrorDialog
import getJsonDataFromCloud
import getSchoolListFromCloud
import kotlinx.android.synthetic.main.activity_change_school.*
import java.io.File

class ChangeSchoolActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_change_school)
        setSupportActionBar(findViewById(R.id.toolbar))

        val listeEcoles = getSchoolListFromCloud()

        val ecoleArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listeEcoles)
        ecole_actv.setAdapter(ecoleArrayAdapter)


    }

    fun validerCallback(v: View){
        val name = ecole_actv.text.toString()
        val pwd = pwd_edittext.text.toString()

        try {
            val data: String = getJsonDataFromCloud(name, pwd)
            val myfile = File(applicationContext.filesDir, "registre_des_certificats.json")
            myfile.writeText(data)
            println(data)
        }
        finally{}

    }
}