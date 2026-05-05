package com.example.myapplication

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.database.FirebaseDatabase

class DetailActivity : AppCompatActivity() {

    private lateinit var etNote: EditText
    private lateinit var btnSaveNote: Button
    private lateinit var btnBackDetail: ImageButton
    private lateinit var detailName: TextView
    private lateinit var detailDateTime: TextView
    private var personData: PersonData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detail)

        // UI Bileşenlerini Bağlama
        detailName = findViewById(R.id.detailName)
        detailDateTime = findViewById(R.id.detailDateTime)
        etNote = findViewById(R.id.etNote)
        btnSaveNote = findViewById(R.id.btnSaveNote)
        btnBackDetail = findViewById(R.id.btnBackDetail)

        // Intent ile gelen nesneyi alıyoruz
        personData = intent.getSerializableExtra("person_data") as? PersonData

        personData?.let {
            detailName.text = it.name
            detailDateTime.text = it.dateTime
            // Daha önce kaydedilen notu EditText'e yazdırıyoruz
            etNote.setText(it.note ?: "")
        }

        // Geri tuşu tıklama olayı (shadowing kaldırıldı)
        btnBackDetail.setOnClickListener {
            onBackPressedDispatcher.onBackPressed() // Modern geri gitme yöntemi
        }

        btnSaveNote.setOnClickListener {
            saveNoteToFirebase()
        }
    }

    private fun saveNoteToFirebase() {
        val newNote = etNote.text.toString()
        val key = personData?.key ?: return

        val ref = FirebaseDatabase.getInstance().getReference("test_write5").child(key)

        ref.child("note").setValue(newNote).addOnSuccessListener {
            Toast.makeText(this, "Not başarıyla güncellendi!", Toast.LENGTH_SHORT).show()
            finish()
        }.addOnFailureListener {
            Toast.makeText(this, "Hata: ${it.message}", Toast.LENGTH_SHORT).show()
        }
    }

    // Hem Toolbar hem de donanımsal geri tuşu için
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}