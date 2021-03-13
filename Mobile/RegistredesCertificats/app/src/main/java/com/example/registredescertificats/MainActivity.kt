@file:Suppress("SpellCheckingInspection")

package com.example.registredescertificats

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.util.AttributeSet
import android.view.View
import android.view.inputmethod.InputMethodManager
import android.widget.ArrayAdapter
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import createConfirmDialog
import createInfoDialog
import kotlinx.android.synthetic.main.activity_main.*
import loadDummyRegistre
import java.io.File
import java.io.UnsupportedEncodingException


const val EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE"

//val api_key = "51c63f31-4635-11eb-bff2-0242ac110002"
//val schoolListId = "2da280f42766"
//val schoolIdsId = "f53b6f4631d6"


class MainActivity : AppCompatActivity() {
    private val CHANGE_SCHOOL_REQUEST = 1
    private val registre: Registre = Registre()
    var schoolName = ""
    var isEmpty = true  // no user input yet
    var noFocus = true  // no widget has focus yet
    var registreUpdatedFlag = false

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val schoolNameFile = File(filesDir, "school_name.txt")
        if (!schoolNameFile.exists()){
            schoolNameFile.createNewFile()
        }
        val name = schoolNameFile.readText()
        if(name != "") schoolName = name

        setContentView(R.layout.activity_main)


        decerner.visibility = View.GONE
        retirer.visibility = View.GONE
        rendre_certificateur.visibility = View.GONE

        registre.filesDir = applicationContext.filesDir.toString()

        if(schoolName != ""){
            loadRegistreInUI()
            titleButton.text = schoolName
            registre.charger(applicationContext, "registre_certificats.json")
        }
        else titleButton.text = "Appuyez ici pour commencer"
    }

    private fun loadRegistreInUI(){
        // setting values in actvs
        val listeMembres = mutableListOf<String>()
        for(m in registre.membres){listeMembres.add(m.id)}
        val listeCategories = mutableListOf<String>()
        for(cat in registre.categories.keys){listeCategories.add(cat)}

        val membreArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listeMembres)
        membre_actv.setAdapter(membreArrayAdapter)

        val categorieArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, listeCategories)
        categorie_actv.setAdapter(categorieArrayAdapter)

        val certificatArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, mutableListOf<String>())
        certificat_actv.setAdapter(certificatArrayAdapter)

        val textWatcher: TextWatcher = object: TextWatcher{
            override fun afterTextChanged(s: Editable?) {
            }

            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
            }

            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                update()
            }
        }

        membre_actv.addTextChangedListener(textWatcher)
        categorie_actv.addTextChangedListener(textWatcher)
        certificat_actv.addTextChangedListener(textWatcher)

    }

    override fun onBackPressed() {
        update()
        if(isEmpty && noFocus){
            super.onBackPressed()
        }
        else{
            clear()
        }
    }

    private fun uploadRegistre(){
        val schoolIdFile = File(filesDir, "school_id.txt")
        val schoolId = schoolIdFile.readText()

        val pFile = File(filesDir, "p.rc")
        val pwd = pFile.readText()

        val registreFile = File(filesDir, "registre_certificats.json")
        val registreString = registreFile.readText()
        println("data sent to http : ")
        println(registreString)

        val queue = Volley.newRequestQueue(applicationContext)
        queue.cache.clear()
        val uploadRegistre = object: StringRequest(Method.PUT, "https://json.extendsclass.com/bin/$schoolId",
                Response.Listener<String> {response ->
                    println(response)
                },
                Response.ErrorListener {response -> println(response)})
        {
            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["Security-key"] = pwd
                return headers
            }

            override fun getBody(): ByteArray {
                return registreString.toByteArray()
            }

        }
        queue.add(uploadRegistre)
        println("uploading registre")
        registreUpdatedFlag = false

    }

    fun update(){
        isEmpty = membre_actv.text.toString()=="" &&
                categorie_actv.text.toString()==""&&
                certificat_actv.text.toString()==""

        noFocus = !(membre_actv.hasFocus() ||
                categorie_actv.hasFocus() ||
                certificat_actv.hasFocus())

        if(schoolName != "") titleButton.text = schoolName
        else{
            titleButton.text = "Appuyez ici pour commencer"
            return
        }

        if(registreUpdatedFlag){
            uploadRegistre()
        }
        else{
            val schoolIdFile = File(filesDir, "school_id.txt")
            val schoolId = schoolIdFile.readText()
            val pFile = File(filesDir, "p.rc")
            val pwd = pFile.readText()
            val queue = Volley.newRequestQueue(applicationContext)
            queue.cache.clear()

            val reloadRegistre = object: StringRequest(Request.Method.GET, "https://json.extendsclass.com/bin/$schoolId",
                    Response.Listener<String> { response ->
                        println("checking if online register was modified")
                        val regFile = File(filesDir, "registre_certificats.json")
                        if(regFile.readText() != response){
                            println(regFile.readText())
                            println(response)
                            println("The online registre has changed !!!!")
                            regFile.writeText(response)
                            registre.charger(applicationContext)
                            loadRegistreInUI()
                            println(registre.membres)
                        }
                    },
                    Response.ErrorListener {response -> println(response)})
            {
                override fun getHeaders(): MutableMap<String, String> {
                    val headers = HashMap<String, String>()
                    headers["Security-key"] = pwd
                    return headers
                }
            }
            queue.add(reloadRegistre)
        }

        // update status text
        status.text = ""
        status.visibility = View.GONE
        val certificats = registre.getCertificats(categorie_actv.text.toString())
        if(certificats.count() > 0){
            val certificatArrayAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, mutableListOf<String>())
            for(c in certificats) certificatArrayAdapter.insert(c.nom, 0)
            certificat_actv.setAdapter(certificatArrayAdapter)
        }
        val m = registre.findMembreById(membre_actv.text.toString()) ?: Membre("", "", id="")
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: Certificat("", "")
        val (ok, msg) = registre.aLeCertificat(m, c)
        if(m.prenom == "" || c.nom == ""){
            decerner.visibility = View.GONE
            rendre_certificateur.visibility = View.GONE
            retirer.visibility = View.GONE
            return
        }
        this.hideKeyboard()
        if(ok == Registre.Certifie){
            decerner.visibility = View.GONE
            rendre_certificateur.visibility = View.VISIBLE
            retirer.visibility = View.VISIBLE}
        else if(ok == Registre.NonCertifie || ok == Registre.CertificatPerdu) {
            decerner.visibility = View.VISIBLE
            rendre_certificateur.visibility = View.GONE
            retirer.visibility = View.GONE}
        else if(ok == Registre.Certificateur){
            decerner.visibility = View.GONE
            rendre_certificateur.visibility = View.GONE
            retirer.visibility = View.VISIBLE
        }
        status.visibility = View.VISIBLE
        status.text = msg
    }

    private fun clear(){
        status.text = ""
        status.visibility = View.GONE
        membre_actv.text.clear()
        categorie_actv.text.clear()
        certificat_actv.text.clear()
        decerner.visibility = View.GONE
        rendre_certificateur.visibility = View.GONE
        retirer.visibility = View.GONE
        // clearButton.visibility = View.INVISIBLE
        currentFocus?.clearFocus()
    }

    fun decernerCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Décerner le certificat ${c.nom} à ${m.id} ?")
        builder.setPositiveButton("Ok"){_, _ ->
            registreUpdatedFlag = true
            registre.decernerCertificat(m, c, Registre.Certifie)
            registre.enregistrer()
            createInfoDialog(v, "${m.id} a maintenant le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun retirerCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Retirer le certificat ${c.nom} à ${m.id} ?")
        builder.setPositiveButton("Ok"){_, _ ->
            registreUpdatedFlag = true
            registre.decernerCertificat(m, c, Registre.CertificatPerdu)
            registre.enregistrer()
            createInfoDialog(v, "${m.id} a perdu le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun rendreCertificateurCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Rendre ${m.id} certificateur\u00b7ice pour le certificat ${c.nom} ?")
        //uploadInThread()
        builder.setPositiveButton("Ok"){_, _ ->
            registreUpdatedFlag = true
            registre.decernerCertificat(m, c, Registre.Certificateur)
            registre.enregistrer()
            createInfoDialog(v, "${m.id} peut maintenant décerner le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun titleCallback(v: View){
        val intent = Intent(this, ChangeSchoolActivity::class.java)
        startActivityForResult(intent, CHANGE_SCHOOL_REQUEST)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if(requestCode == CHANGE_SCHOOL_REQUEST){
            val result = data?.getStringExtra("schoolName") ?: ""
            if(result != ""){
                schoolName = result
                titleButton.text = result
            }

            registre.charger(applicationContext, "registre_certificats.json")
            loadRegistreInUI()
        }
    }

    fun actvCallback(v: View){
        update()
    }
}

class MyAutoCompleteTextView @JvmOverloads
    constructor(context : Context,
                attr: AttributeSet? = null,
                defStyleAttr: Int = 0) : androidx.appcompat.widget.AppCompatAutoCompleteTextView(context, attr, defStyleAttr)
{
    override fun enoughToFilter(): Boolean {
        return true
    }
    override fun performClick(): Boolean{
        showDropDown()
        return super.performClick()
    }
}

fun Fragment.hideKeyboard() {
    view?.let { activity?.hideKeyboard(it) }
}

fun Activity.hideKeyboard() {
    hideKeyboard(currentFocus ?: View(this))
}

fun Context.hideKeyboard(view: View) {
    val inputMethodManager = getSystemService(Activity.INPUT_METHOD_SERVICE) as InputMethodManager
    inputMethodManager.hideSoftInputFromWindow(view.windowToken, 0)
}
