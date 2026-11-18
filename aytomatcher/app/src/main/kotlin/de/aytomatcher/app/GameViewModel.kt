package de.aytomatcher.app

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import de.aytomatcher.core.Constraints
import de.aytomatcher.core.Event
import de.aytomatcher.core.SolveResult
import de.aytomatcher.core.Solver
import de.aytomatcher.core.StateLimitException
import de.aytomatcher.core.derive
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

const val NUM_MEN = 10
const val NUM_WOMEN = 11

class GameViewModel(application: Application) : AndroidViewModel(application) {
    private val storage = Storage(application)

    var women by mutableStateOf(List(NUM_WOMEN) { "Frau ${it + 1}" })
        private set
    var men by mutableStateOf(List(NUM_MEN) { "Mann ${it + 1}" })
        private set
    var events by mutableStateOf<List<Event>>(emptyList())
        private set
    var setupDone by mutableStateOf(false)
        private set
    var constraints by mutableStateOf<Constraints?>(null)
        private set
    var result by mutableStateOf<SolveResult?>(null)
        private set
    var computing by mutableStateOf(false)
        private set
    var failure by mutableStateOf<String?>(null)
        private set

    private var job: Job? = null

    init {
        storage.load()?.let {
            if (it.women.size == NUM_WOMEN && it.men.size == NUM_MEN) {
                women = it.women
                men = it.men
                events = it.events
                setupDone = it.setupDone
            }
        }
        recompute()
    }

    fun saveSetup(newWomen: List<String>, newMen: List<String>) {
        women = newWomen.mapIndexed { i, n -> n.trim().ifEmpty { "Frau ${i + 1}" } }
        men = newMen.mapIndexed { i, n -> n.trim().ifEmpty { "Mann ${i + 1}" } }
        setupDone = true
        persist()
    }

    /** Setzt alle Namen auf die Standardnamen zurück. Die Ereignisse bleiben erhalten. */
    fun resetNames() {
        women = List(NUM_WOMEN) { "Frau ${it + 1}" }
        men = List(NUM_MEN) { "Mann ${it + 1}" }
        persist()
    }

    fun editNames() {
        setupDone = false
    }

    fun addEvent(e: Event) {
        events = events + e
        persist()
        recompute()
    }

    fun removeLast() {
        if (events.isEmpty()) return
        events = events.dropLast(1)
        persist()
        recompute()
    }

    fun resetAll() {
        events = emptyList()
        persist()
        recompute()
    }

    private fun persist() = storage.save(Saved(women, men, events, setupDone))

    private fun recompute() {
        job?.cancel()
        val snapshot = events
        job = viewModelScope.launch {
            computing = true
            failure = null
            try {
                val pair = withContext(Dispatchers.Default) {
                    val c = derive(NUM_MEN, snapshot)
                    c to Solver.solve(c)
                }
                constraints = pair.first
                result = pair.second
            } catch (e: CancellationException) {
                throw e
            } catch (e: StateLimitException) {
                failure = "Die Berechnung ist zu groß für dieses Gerät."
            } catch (e: Exception) {
                failure = e.message ?: "Unbekannter Fehler bei der Berechnung."
            }
            computing = false
        }
    }
}
