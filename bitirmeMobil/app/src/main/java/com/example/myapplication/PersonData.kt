// PersonData.kt (Güncel Hali)
package com.example.myapplication

data class PersonData(
    // Benzersiz Key'i buraya ekledik
    var key: String,
    val name: String,
    val accuracy: Double,
    val dateTime: String,
    var isSelected: Boolean = false,
    val note: String? = null
)