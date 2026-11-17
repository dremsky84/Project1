package de.aytomatcher.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import de.aytomatcher.core.BoxResult
import de.aytomatcher.core.Matchbox
import de.aytomatcher.core.Night

@Composable
fun HistoryTab(vm: GameViewModel) {
    var confirmReset by remember { mutableStateOf(false) }
    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (vm.events.isEmpty()) Text("Noch keine Ereignisse eingetragen.")
        var nightNo = 0
        var boxNo = 0
        vm.events.forEach { e ->
            when (e) {
                is Night -> {
                    nightNo++
                    Column {
                        Text("Matching Night $nightNo – ${e.lights} Lichter", style = MaterialTheme.typography.titleSmall)
                        Text(
                            e.couples.joinToString(", ") { "${vm.men[it.man]}+${vm.women[it.woman]}" },
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }

                is Matchbox -> {
                    boxNo++
                    val what = when (e.result) {
                        BoxResult.NO -> "kein Match"
                        BoxResult.YES -> "Perfect Match"
                        BoxResult.DOUBLE -> "Doppel-Match (zweite Frau: ${vm.women.getOrElse(e.secondWoman) { "?" }})"
                    }
                    Column {
                        Text("Matchbox $boxNo", style = MaterialTheme.typography.titleSmall)
                        Text("${vm.women[e.woman]} + ${vm.men[e.man]}: $what", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        if (vm.events.isNotEmpty()) {
            OutlinedButton(onClick = { vm.removeLast() }, modifier = Modifier.fillMaxWidth()) {
                Text("Letztes Ereignis löschen")
            }
        }
        Button(onClick = { vm.editNames() }, modifier = Modifier.fillMaxWidth()) { Text("Namen bearbeiten") }
        OutlinedButton(onClick = { confirmReset = true }, modifier = Modifier.fillMaxWidth()) {
            Text("Alle Ereignisse löschen")
        }
    }
    if (confirmReset) {
        AlertDialog(
            onDismissRequest = { confirmReset = false },
            title = { Text("Alle Ereignisse löschen?") },
            text = { Text("Die Namen bleiben erhalten.") },
            confirmButton = {
                TextButton(onClick = {
                    vm.resetAll()
                    confirmReset = false
                }) { Text("Löschen") }
            },
            dismissButton = { TextButton(onClick = { confirmReset = false }) { Text("Abbrechen") } },
        )
    }
}
