@file:Suppress("SpellCheckingInspection")

package com.example.registredescertificats

import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.view.View
import android.text.Editable
import android.text.TextWatcher
import android.util.AttributeSet
import android.view.inputmethod.InputMethodManager
import android.widget.*
import androidx.fragment.app.Fragment
import kotlinx.android.synthetic.main.activity_main.*
import android.content.Intent
import createConfirmDialog
import createInfoDialog


const val EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE"

//TODO: cloud support
//TODO: prompt school name and pwd

class MainActivity : AppCompatActivity() {

    private val CHANGE_SCHOOL_REQUEST = 1
    val registre: Registre = Registre()

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val intent = Intent(this, ChangeSchoolActivity::class.java)
        startActivityForResult(intent, CHANGE_SCHOOL_REQUEST)

        setContentView(R.layout.activity_main)

        decerner.visibility = View.GONE
        retirer.visibility = View.GONE
        rendre_certificateur.visibility = View.GONE
        clearButton.visibility = View.GONE

        registre.filesDir = this.filesDir.toString()
        registre.charger(applicationContext, "registre_certificats.json")

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

        val m = registre.findMembreById("Christelle A.") ?: error("membre not found")
        val c = registre.findCertificatByName("Guitare") ?: error("certificat not found")
        registre.decernerCertificat(m, c, Registre.Certifie)

        registre.enregistrer(applicationContext)

    }

    fun update(){
        status.text = ""
        status.visibility = View.GONE
        if(membre_actv.text.toString()!="" ||
           categorie_actv.text.toString()!=""||
           certificat_actv.text.toString()!="") {
            clearButton.visibility = View.VISIBLE
        }
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

    fun clear(){
        status.text = ""
        status.visibility = View.GONE
        membre_actv.text.clear()
        categorie_actv.text.clear()
        certificat_actv.text.clear()
        decerner.visibility = View.GONE
        rendre_certificateur.visibility = View.GONE
        retirer.visibility = View.GONE
        clearButton.visibility = View.INVISIBLE
        currentFocus?.clearFocus()
    }

    fun decernerCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Décerner le certificat ${c.nom} à ${m.id} ?")
        //TODO: update registre in thread

        builder.setPositiveButton("Ok"){_, _ ->
            registre.decernerCertificat(m, c, Registre.Certifie)
            createInfoDialog(v, "${m.id} a maintenant le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun retirerCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Retirer le certificat ${c.nom} à ${m.id} ?")
        //TODO: update registre in thread
        builder.setPositiveButton("Ok"){_, _ ->
            registre.decernerCertificat(m, c, Registre.CertificatPerdu)
            createInfoDialog(v, "${m.id} a perdu le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun rendreCertificateurCallback(v: View){
        val m = registre.findMembreById(membre_actv.text.toString()) ?: return
        val c = registre.findCertificatByName(certificat_actv.text.toString()) ?: return
        val builder = createConfirmDialog(v, "Rendre ${m.id} certificateur\u00b7ice pour le certificat ${c.nom} ?")
        //TODO: update registre in thread
        builder.setPositiveButton("Ok"){_, _ ->
            registre.decernerCertificat(m, c, Registre.Certificateur)
            createInfoDialog(v, "${m.id} peut maintenant décerner le certificat ${c.nom}.").show()
            clear()}
        builder.show()
    }

    fun clearButtonCallback(v: View){
        clear()
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
