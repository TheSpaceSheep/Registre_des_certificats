package com.example.registredescertificats

import android.content.Context
import java.lang.NullPointerException

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.annotations.SerializedName
import com.google.gson.reflect.TypeToken
import copyJsonDataFromAssetToFilesDir
import getJsonDataFromFile
import java.io.File

class Membre(var prenom: String, var nom: String, var id:String)
class Certificat(var nom: String, var categorie: String)

class Registre{
    companion object Flags{
        val Certifie = 1
        val NonCertifie = 0
        val Certificateur = -1
        val CertificatPerdu = -2
    }

    var membres = mutableListOf<Membre>() // liste des membres de l'école
    var certificats = mutableListOf<Certificat>() // liste de tous les certificats
    var registre = mutableMapOf<Pair<Membre, Certificat>, Int>() // (membre, certificat) -> statut de certification
    var categories = mutableMapOf<String, MutableList<Certificat>>() // categorie -> liste des certificats de cette catégorie
    var filesDir = ""

    fun ajouterMembre(prenom: String, nom: String, id: String){
        for(m in membres){if(m.id == id){return}}
        membres.add(Membre(prenom, nom, id))
    }

    fun ajouterCertificat(nom: String, categorie: String){
        for(c in certificats){if(c.nom==nom && c.categorie==categorie){return}}
        val c = Certificat(nom, categorie)
        certificats.add(c)
        if(categorie !in categories){
            categories[categorie] = mutableListOf()
        }
        categories[categorie]?.add(c)

        for(m in membres){
            registre[Pair(m, c)] = Registre.NonCertifie
        }
    }

    fun decernerCertificat(membre: Membre, certificat: Certificat, niveau: Int){
        registre[Pair(membre, certificat)] = niveau
    }

    fun aLeCertificat(membre: Membre, certificat: Certificat): Pair<Int, String>{
        val r = registre[Pair(membre, certificat)] ?: NonCertifie
        return if (r >= Certifie) {
            Pair(r, "${membre.id} a le certificat ${certificat.nom}")
        } else if (r == NonCertifie) {
            Pair(NonCertifie, "${membre.id} n'a pas le certificat ${certificat.nom}")
        } else if (r == Certificateur) {
            Pair(Certificateur, "${membre.id} est certificateur\u00b7ice pour le certificat ${certificat.nom}")
        } else if (r == CertificatPerdu) {
            Pair(CertificatPerdu, "${membre.id} n'a plus le certificat ${certificat.nom}")
        } else
            Pair(NonCertifie, "${membre.id} n'a pas le certificat ${certificat.nom}")
    }

    fun findMembreById(identification: String): Membre?{
        for(m in membres){
            if(m.id == identification){
                return m
            }
        }
        return null
    }

        fun findMembreByName(prenom: String, nom: String): Membre? {
            for (m in membres) {
                if (m.prenom == prenom && m.nom == nom) {
                    return m
                }
            }
            return null
        }

    fun findCertificatByName(nom: String): Certificat? {
        for (c in certificats) {
            if (c.nom == nom) {
                return c
            }
        }
        return null
    }
    fun getCertificats(categorie: String): List<Certificat> {
        //renvoie une liste des certificats pour une catégorie
        val l = mutableListOf<Certificat>()
        for(c in certificats) {
            if(c.categorie == categorie) {
                l += c
            }
        }
        return l
    }

    fun charger(appctx: Context, file: String = "registre_certificats.json", merge: Boolean = false){
        val jsonFileString = File(filesDir, file).readText()
        val gson = GsonBuilder().create()
        val jsonRegistreType = object : TypeToken<JSONRegistre>() {}.type
        val jsonRegistre: JSONRegistre = gson.fromJson(jsonFileString, jsonRegistreType)

        if(!merge) clear()

        for(m in jsonRegistre.membres){
            ajouterMembre(m[0], m[1], m[2])
        }

        for(c in jsonRegistre.certificats){
            ajouterCertificat(c[0], c[1])
        }

        for(m_id in jsonRegistre.registre.keys){
            val m = findMembreById(m_id) ?: break
            for(entry in jsonRegistre.registre[m_id] ?: error("invalid json file")){
                val c = findCertificatByName(entry[0]) ?: break
                decernerCertificat(m, c, entry[1].toInt())
            }
        }
    }

    fun enregistrer(file: String = "registre_certificats.json"){
        val jsonable: JSONRegistre
        val jcertificats = mutableListOf<List<String>>()
        val jmembres = mutableListOf<List<String>>()
        val jregistre = mutableMapOf<String, MutableList<List<String>>>()
        for(c in certificats){
            jcertificats.add(listOf(c.nom, c.categorie))
        }
        for(m in membres){
            jmembres.add(listOf(m.prenom, m.nom, m.id))
        }

        for(m in membres){
            jregistre[m.id] = mutableListOf<List<String>>()
            for(c in certificats){
                jregistre[m.id]!!.add(listOf(c.nom, registre[Pair(m, c)].toString()))
            }
        }

        jsonable = JSONRegistre(jcertificats, jmembres, jregistre)

        val gson = GsonBuilder().create()
        val jsonString: String = gson.toJson(jsonable)
        val myfile = File(filesDir, file)

        myfile.writeText(jsonString)
    }

    private fun clear(){
        membres = mutableListOf() // liste des membres de l'école
        certificats = mutableListOf() // liste de tous les certificats
        registre = mutableMapOf() // (membre, certificat) -> statut de certification
        categories = mutableMapOf() // categorie -> liste des certificats de cette catégorie
    }
}

class JSONRegistre(
        @SerializedName("certificats")
        val certificats:List<List<String>>,
        @SerializedName("membres")
        val membres:List<List<String>>,
        @SerializedName("registre")
        val registre:Map<String, List<List<String>>>)
