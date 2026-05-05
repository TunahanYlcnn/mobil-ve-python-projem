//MainActivity.kt
package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.view.ActionMode
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.google.firebase.database.*
import android.app.NotificationChannel
import android.app.NotificationManager
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import android.os.Build
import android.content.Context
import android.graphics.Color


// PersonAdapter'dan gelen olayları işlemek için SelectionListener uygulandı
class MainActivity : AppCompatActivity(), PersonAdapter.SelectionListener {

    // --- GEREKLİ OLAN TANIMLAMALAR ---
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: PersonAdapter
    private val list = mutableListOf<PersonData>()

    private lateinit var database: FirebaseDatabase
    private lateinit var ref: DatabaseReference // Kişi verileri için Firebase Referansı (test_write5)

    // !!! BURASI TEKİL STATE İÇİN AYARLANDI !!!
    private lateinit var doorRef: DatabaseReference // Kapı durumu tekil düğümü (test_write6)

    private lateinit var textDoorStatus: TextView // Kapı Durumu için TextView
    private lateinit var textPersonName: TextView
    private lateinit var loadingOverlay: View
    private lateinit var loadingLayout: View
    private lateinit var cardResult: MaterialCardView
    private lateinit var progressAccuracy: ProgressBar
    private lateinit var textAccuracyPercent: TextView
    private lateinit var textDateTime: TextView
    private var firstDataLoaded = false

    private var actionMode: ActionMode? = null
    private var initialLoadComplete = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
        }

        // Loading View'ları bağlama
        loadingOverlay = findViewById(R.id.loadingOverlay)
        loadingLayout = findViewById(R.id.loadingLayout)

        // Kapı Durumu TextView'ı bağlama
        textDoorStatus = findViewById(R.id.textDoorStatus)

        // Kapı Durumu TextView'e Tıklama Olayı Ekle (Toggle için)
        textDoorStatus.setOnClickListener {
            sendManualDoorToggle()
        }

        // Card elemanları
        cardResult = findViewById(R.id.cardResult)
        textPersonName = findViewById(R.id.textPersonName)
        progressAccuracy = findViewById(R.id.progressAccuracy)
        textAccuracyPercent = findViewById(R.id.textAccuracyPercent)
        textDateTime = findViewById(R.id.textDateTime)

        // Başlangıçta kart gizli
        cardResult.visibility = View.GONE

        // RecyclerView Başlatma
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = PersonAdapter(list, this)
        recyclerView.adapter = adapter

        // Firebase Başlatma
        database = FirebaseDatabase.getInstance()
        ref = database.getReference("test_write5") // Kişi verileri

        // !!! doorRef'i tekil state düğümüne ayarlama !!!
        doorRef = database.getReference("test_write6")

        // Kapı Durumu Listener'ını başlat
        setupDoorStatusListener()

        // Firebase Listener (Kişi verileri) - Tüm veriyi çeker, sadece yeni veriye bildirim verir
        ref.addChildEventListener(object : ChildEventListener {
            override fun onChildAdded(snapshot: DataSnapshot, previousChildName: String?) {

                val key = snapshot.key!!
                val name = snapshot.child("person").getValue(String::class.java) ?: "Bilinmiyor"
                val accuracy = snapshot.child("accuracy").getValue(Double::class.java) ?: 0.0
                val dateTime = snapshot.child("date_time").getValue(String::class.java) ?: "Yok"

                val newItem = PersonData(key, name, accuracy, dateTime)

                runOnUiThread {
                    adapter.addNewItem(newItem)

                    // KONTROL: Sadece ilk yükleme tamamlandıktan sonra bildirim gönder
                    if (initialLoadComplete) {
                        showNotification(name)
                    }

                    if (!firstDataLoaded) {
                        loadingOverlay.visibility = View.GONE
                        loadingLayout.visibility = View.GONE
                        updateCardWithData(name, accuracy, dateTime)
                        cardResult.visibility = View.VISIBLE
                        firstDataLoaded = true
                    } else if (initialLoadComplete) { // Sadece yeni veriler için kartı güncelle
                        updateCardWithData(name, accuracy, dateTime)
                    }
                }
            }

            override fun onChildChanged(snapshot: DataSnapshot, previousChildName: String?) {}

            override fun onChildRemoved(snapshot: DataSnapshot) {
                val key = snapshot.key!!
                val itemToRemove = list.find { it.key == key }

                if (itemToRemove != null) {
                    list.remove(itemToRemove)
                    adapter.notifyDataSetChanged()
                }
            }

            override fun onChildMoved(snapshot: DataSnapshot, previousChildName: String?) {}

            override fun onCancelled(error: DatabaseError) {
                initialLoadComplete = true
            }
        })

        // EKLEME: Tüm veriler yüklendikten sonra bildirimi açmak için tek seferlik Listener.
        ref.addListenerForSingleValueEvent(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                // Tüm geçmiş veriler listeye eklendiğinde bu metot bir kez tetiklenir.
                initialLoadComplete = true
            }

            override fun onCancelled(error: DatabaseError) {
                initialLoadComplete = true
            }
        })
    }

    // --- KAPININ MANUEL KONTROL METODU (TEKİL STATE GÜNCELLEME) ---
    /**
     * Mevcut UI durumuna göre Kapı durumunu tersine çevirir ve sonucu test_write6 yoluna doğrudan yazar (setValue).
     */
    private fun sendManualDoorToggle() {
        val currentState = textDoorStatus.text.toString()

        val newState: String

        // UI'daki metne bakılarak yeni durum belirlenir
        if (currentState == "KAPI KAPALI") {
            // Kapalı ise Açık yap
            newState = "door opened"
        } else {
            // Açık ise Kapalı yap
            newState = "door closed"
        }

        // !!! DÜZELTME: push() yerine setValue() kullanılarak mevcut düğümün değeri güncellenir.
        doorRef.setValue(newState)

    }


    // --- Kapı Durumu Listener Metotları (TEKİL STATE OKUMA) ---
    private fun setupDoorStatusListener() {
        // !!! DÜZELTME: Artık limitToLast(1) kullanılmıyor. Doğrudan tekil düğümü dinliyoruz.
        doorRef.addValueEventListener(object : ValueEventListener {

            override fun onDataChange(snapshot: DataSnapshot) {
                // Veriyi doğrudan String olarak okuyoruz (test_write6 -> "door closed" veya "door opened")
                val doorState = snapshot.getValue(String::class.java)

                runOnUiThread {
                    updateDoorStatusUI(doorState)
                }
            }

            override fun onCancelled(error: DatabaseError) {
                Toast.makeText(this@MainActivity, "Kapı durumu okuma hatası: ${error.message}", Toast.LENGTH_LONG).show()
                updateDoorStatusUI("Hata")
            }
        })
    }

    // Kapı durumu metni ve rengini güncelleyen yardımcı metot
    private fun updateDoorStatusUI(state: String?) {

        when (state?.toLowerCase()) {
            "door opened", "kapı açık" -> {
                textDoorStatus.text = "KAPI AÇIK"
                textDoorStatus.setBackgroundColor(Color.RED)
            }
            "door closed", "kapı kapalı" -> {
                textDoorStatus.text = "KAPI KAPALI"
                textDoorStatus.setBackgroundColor(Color.GREEN)
            }
            else -> {
                textDoorStatus.text = "Bilinmeyen Durum: ${state ?: "Veri Yok"}"
                textDoorStatus.setBackgroundColor(Color.GRAY)
            }
        }
    }

    // --- Silme Mantığı ---
    private fun deleteSelectedItems() {
        val selectedItems = adapter.getSelectedItems()

        if (selectedItems.isEmpty()) {
            Toast.makeText(this, "Lütfen silmek için öğe seçin.", Toast.LENGTH_SHORT).show()
            return
        }

        for (item in selectedItems) {
            val firebaseKey = item.key

            if (firebaseKey.isNotEmpty()) {
                ref.child(firebaseKey).removeValue()
                    .addOnSuccessListener {
                        Toast.makeText(this, "Öğe(ler) siliniyor...", Toast.LENGTH_SHORT).show()
                    }
                    .addOnFailureListener {
                        Toast.makeText(this, "Silme başarısız oldu: ${it.message}", Toast.LENGTH_SHORT).show()
                    }
            }
        }

        actionMode?.finish()
    }

    // --- SelectionListener Metotları ---
    override fun onSelectionChanged(selectedCount: Int) {
        if (actionMode != null) {
            actionMode?.title = "$selectedCount Seçili"
        }
        if (selectedCount == 0 && adapter.isSelectionMode) {
            actionMode?.finish()
        }
    }

    override fun onLongClickStarted() {
        if (actionMode == null) {
            actionMode = startSupportActionMode(actionModeCallback)
        }
    }

    private val actionModeCallback = object : ActionMode.Callback {
        override fun onCreateActionMode(mode: ActionMode, menu: Menu): Boolean {
            mode.menuInflater.inflate(R.menu.menu_selection, menu)
            return true
        }

        override fun onPrepareActionMode(mode: ActionMode, menu: Menu): Boolean {
            return false
        }

        override fun onActionItemClicked(mode: ActionMode, item: MenuItem): Boolean {
            return when (item.itemId) {
                R.id.action_delete -> {
                    deleteSelectedItems()
                    true
                }
                else -> false
            }
        }

        override fun onDestroyActionMode(mode: ActionMode) {
            adapter.clearSelections()
            actionMode = null
        }
    }

    // --- Diğer Metotlar ---

    private fun updateCardWithData(name: String, accuracy: Double, dateTime: String) {

        textPersonName.text = "Kişi: $name"

        val percent = if (accuracy <= 1.0) {
            (accuracy * 100).toInt()
        } else {
            accuracy.toInt()
        }

        progressAccuracy.progress = percent
        textAccuracyPercent.text = "$percent%"
        textDateTime.text = "Tarih & Saat: $dateTime"
    }

    private fun showNotification(personName: String) {
        val channelId = "new_person_channel"

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Yeni Kişi Bildirimi",
                NotificationManager.IMPORTANCE_HIGH
            )
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Yeni kişi geldi")
            .setContentText("Kişi: $personName")
            .setSmallIcon(R.mipmap.ic_launcher)
            .setAutoCancel(true)
            .build()

        val manager = NotificationManagerCompat.from(this)
        manager.notify(System.currentTimeMillis().toInt(), notification)
    }

}