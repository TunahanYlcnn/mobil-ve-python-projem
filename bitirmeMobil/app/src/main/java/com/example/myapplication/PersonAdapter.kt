// PersonAdapter.kt
package com.example.myapplication

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.CheckBox
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import android.util.SparseBooleanArray

// Callback (Geri Çağırma) arayüzü eklendi, böylece Adapter, MainActivity'ye haber verebilir.
class PersonAdapter(
    private val list: MutableList<PersonData>,
    private val listener: SelectionListener // Yeni listener eklendi
) : RecyclerView.Adapter<PersonAdapter.ViewHolder>() {

    // Seçim modunda olup olmadığımızı belirler
    var isSelectionMode = false

    interface SelectionListener {
        fun onSelectionChanged(selectedCount: Int)
        fun onLongClickStarted()
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textName: TextView = itemView.findViewById(R.id.textName)
        val textAccuracy: TextView = itemView.findViewById(R.id.textAccuracy)
        val textDateTime: TextView = itemView.findViewById(R.id.textDateTime)
        // CheckBox eklendi
        val itemCheckbox: CheckBox = itemView.findViewById(R.id.itemCheckbox)
        val itemContainer: View = itemView.findViewById(R.id.itemContainer)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_person, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = list.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = list[position]

        // Veri bağlama
        holder.textName.text = item.name
        holder.textAccuracy.text = "${(item.accuracy * 100).toInt()}%"
        holder.textDateTime.text = item.dateTime

        // 1. Seçim Modunu Yönetme (Görünürlük)
        if (isSelectionMode) {
            holder.itemCheckbox.visibility = View.VISIBLE
            holder.itemCheckbox.isChecked = item.isSelected
            holder.itemContainer.setBackgroundColor(if (item.isSelected) Color.parseColor("#E0E0E0") else Color.TRANSPARENT)
        } else {
            holder.itemCheckbox.visibility = View.GONE
            holder.itemCheckbox.isChecked = false // Moddan çıkınca seçimi sıfırla
            holder.itemContainer.setBackgroundColor(Color.TRANSPARENT)
        }

        // 2. Tıklama Olayları
        holder.itemView.setOnClickListener {
            if (isSelectionMode) {
                toggleSelection(position) // Eğer seçim modundaysak, seçimi değiştir
            }
        }

        // 3. Uzun Basma Olayı
        holder.itemView.setOnLongClickListener {
            if (!isSelectionMode) {
                isSelectionMode = true
                listener.onLongClickStarted() // MainActivity'ye bildir
                toggleSelection(position) // Basılı tutulanı seç
                true // Olayı tükettik
            } else {
                false
            }
        }
    }

    private fun toggleSelection(position: Int) {
        list[position].isSelected = !list[position].isSelected // Seçim durumunu tersine çevir
        notifyItemChanged(position)
        listener.onSelectionChanged(list.count { it.isSelected }) // MainActivity'ye seçili sayısını bildir
    }

    // Silinmesi gereken öğeleri döndürür
    fun getSelectedItems(): List<PersonData> {
        return list.filter { it.isSelected }
    }

    // Seçili öğeleri listeden siler
    fun removeSelectedItems() {
        val selectedItems = getSelectedItems()
        list.removeAll(selectedItems)
        // Seçim modundan çık
        isSelectionMode = false
        notifyDataSetChanged()
        listener.onSelectionChanged(0) // Seçili sayısını sıfırla
    }

    // Tüm öğelerin seçimini kaldırır
    fun clearSelections() {
        isSelectionMode = false
        list.forEach { it.isSelected = false }
        notifyDataSetChanged()
        listener.onSelectionChanged(0)
    }

    fun addNewItem(item: PersonData) {
        // Yeni veri en üste (0. pozisyona) eklensin
        list.add(0, item)
        notifyItemInserted(0)
    }
}