import android.app.AlertDialog
import android.content.Context
import android.view.View
import java.io.IOException
import java.io.File

fun getJsonDataFromFile(context: Context, fileName: String): String? {
    val jsonString: String
    try {
        jsonString = File(context.filesDir, fileName).bufferedReader().use { it.readText() }
    } catch (ioException: IOException) {
        ioException.printStackTrace()
        return null
    }
    return jsonString
}

fun copyJsonDataFromAssetToFilesDir(context: Context, fileName: String): String? {
    val jsonString: String
    try {
        jsonString = context.assets.open(fileName).bufferedReader().use {it.readText()}
        File(context.filesDir, fileName).writeText(jsonString)
    } catch (ioException: IOException) {
        ioException.printStackTrace()
        return null
    }
    return jsonString
}


fun createConfirmDialog(view: View, msg: String): AlertDialog.Builder{
    val builder = AlertDialog.Builder(view.context)
    builder.setTitle("Confirmer")
    builder.setMessage(msg)
    builder.setNegativeButton("Annuler"){_, _ -> Unit}
    return builder
}

fun createInfoDialog(view: View, msg: String): AlertDialog.Builder{
    val builder = AlertDialog.Builder(view.context)
    builder.setTitle("Information")
    builder.setMessage(msg)
    builder.setPositiveButton("Ok"){_, _ -> Unit}
    return builder
}

fun createErrorDialog(view: View, msg: String): AlertDialog.Builder{
    val builder = AlertDialog.Builder(view.context)
    builder.setTitle("Erreur")
    builder.setMessage(msg)
    builder.setPositiveButton("Ok"){_, _ -> Unit}
    return builder
}
