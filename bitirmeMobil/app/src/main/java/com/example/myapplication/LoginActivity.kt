//LoginActivity.kt
package com.example.myapplication

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.view.animation.AlphaAnimation
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class LoginActivity : AppCompatActivity() {

    private lateinit var etUsername: EditText
    private lateinit var etPassword: EditText
    private lateinit var btnLogin: Button
    private lateinit var tvRegister: TextView
    private lateinit var tvError: TextView

    private lateinit var prefs: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        // SharedPreferences
        prefs = getSharedPreferences("UserData", MODE_PRIVATE)

        // View bağlama
        etUsername = findViewById(R.id.etUsername)
        etPassword = findViewById(R.id.etPassword)
        btnLogin = findViewById(R.id.btnLogin)
        tvRegister = findViewById(R.id.tvRegister)
        tvError = findViewById(R.id.tvError)

        tvError.text = ""

        // Giriş butonu
        btnLogin.setOnClickListener { loginUser() }

        // Kayıt ekranına git
        tvRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }
    }

    private fun loginUser() {
        val savedUser = prefs.getString("username", null)
        val savedPass = prefs.getString("password", null)

        val inputUser = etUsername.text.toString().trim()
        val inputPass = etPassword.text.toString().trim()

        // Giriş kontrolü
        if (inputUser == savedUser && inputPass == savedPass) {

            tvError.text = ""

            // 🔥 Başarılı giriş → MainActivity'e geçiş
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
            finish()

        } else {
            // Hatalı giriş
            tvError.text = "Bilgiler yanlış, tekrar deneyin!"
            flashFields()
        }
    }

    private fun flashFields() {
        val anim = AlphaAnimation(0.3f, 1f)
        anim.duration = 150
        anim.repeatCount = 3
        anim.repeatMode = AlphaAnimation.REVERSE

        etUsername.startAnimation(anim)
        etPassword.startAnimation(anim)
    }
}
