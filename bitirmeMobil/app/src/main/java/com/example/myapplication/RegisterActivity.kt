// RegisterActivity.kt
package com.example.myapplication

import android.content.SharedPreferences
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.myapplication.databinding.ActivityRegisterBinding

class RegisterActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRegisterBinding
    private lateinit var prefs: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = getSharedPreferences("UserData", MODE_PRIVATE)

        binding.tvMatchStatus.text = ""
        disableRegister()

        val watcher = object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                checkAllFields()
            }
            override fun afterTextChanged(s: Editable?) {}
        }

        binding.etName.addTextChangedListener(watcher)
        binding.etSurname.addTextChangedListener(watcher)
        binding.etUsername.addTextChangedListener(watcher)
        binding.etPassword.addTextChangedListener(watcher)
        binding.etPasswordRepeat.addTextChangedListener(watcher)

        binding.btnRegister.setOnClickListener { saveUser() }
        binding.btnBack.setOnClickListener { finish() }
    }

    private fun disableRegister() {
        binding.btnRegister.isEnabled = false
        binding.btnRegister.alpha = 0.4f
    }

    private fun checkAllFields() {
        val name = binding.etName.text.toString().trim()
        val surname = binding.etSurname.text.toString().trim()
        val username = binding.etUsername.text.toString().trim()
        val pass = binding.etPassword.text.toString()
        val repeat = binding.etPasswordRepeat.text.toString()

        if (pass.isNotEmpty() && repeat.isNotEmpty()) {
            if (pass == repeat) {
                binding.tvMatchStatus.text = "Eşleşti"
                binding.tvMatchStatus.setTextColor(0xFF2E7D32.toInt())
            } else {
                binding.tvMatchStatus.text = "Eşleşmiyor"
                binding.tvMatchStatus.setTextColor(0xFFFF0000.toInt())
            }
        } else {
            binding.tvMatchStatus.text = ""
        }

        val allFilled = name.isNotEmpty() &&
                surname.isNotEmpty() &&
                username.isNotEmpty() &&
                pass.isNotEmpty() &&
                repeat.isNotEmpty() &&
                pass == repeat

        if (allFilled) {
            binding.btnRegister.isEnabled = true
            binding.btnRegister.alpha = 1f
        } else {
            disableRegister()
        }
    }

    private fun saveUser() {
        val username = binding.etUsername.text.toString().trim()
        val password = binding.etPassword.text.toString()

        prefs.edit().apply {
            putString("name", binding.etName.text.toString().trim())
            putString("surname", binding.etSurname.text.toString().trim())
            putString("username", username)
            putString("password", password)
            apply()
        }

        Toast.makeText(this, "Kayıt başarılı!", Toast.LENGTH_SHORT).show()
        finish()
    }
}
