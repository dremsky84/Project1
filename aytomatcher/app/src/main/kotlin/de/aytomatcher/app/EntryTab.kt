package de.aytomatcher.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import de.aytomatcher.core.Advisor
import de.aytomatcher.core.BoxResult
import de.aytomatcher.core.Couple
import de.aytomatcher.core.Matchbox
import de.aytomatcher.core.Night

/** Auswahlfeld: Button, der beim Antippen eine Liste von Optionen (Index, Text) öffnet. */
@Composable
fun Picker(
    placeholder: String,
    options: List<Pair<Int, String>>,
    selected: Int?,
    onSelect: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    var open by remember { mutableStateOf(false) }
    Column(modifier) {
        OutlinedButton(onClick = { open = true }, modifier = Modifier.fillMaxWidth()) {
            Text(options.firstOrNull { it.first == selected }?.second ?: placeholder, maxLines = 1)
        }
        DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
            options.forEach { (value, label) ->
                DropdownMenuItem(text = { Text(label) }, onClick = {
                    onSelect(value)
                    open = false
                })
            }
        }
    }
}

@Composable
fun EntryTab(vm: GameViewModel) {
    var showNight by remember { mutableStateOf(false) }
    var showBox by remember { mutableStateOf(false) }
    val nights = vm.events.count { it is Night }
    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Neues Ereignis eintragen", style = MaterialTheme.typography.titleMedium)
        Button(onClick = { showNight = true }, modifier = Modifier.fillMaxWidth()) {
            Text("Matching Night eintragen (bisher $nights)")
        }
        Button(onClick = { showBox = true }, modifier = Modifier.fillMaxWidth()) {
            Text("Matchbox eintragen")
        }
        Text(
            "Trage die Ereignisse in der Reihenfolge ein, in der sie in der Show passiert sind. " +
                "Bereits bestätigte Paare werden in jeder Matching Night automatisch mitgezählt.",
            style = MaterialTheme.typography.bodySmall,
        )
    }
    if (showNight) NightDialog(vm) { showNight = false }
    if (showBox) BoxDialog(vm) { showBox = false }
}

@Composable
private fun NightDialog(vm: GameViewModel, onClose: () -> Unit) {
    val c = vm.constraints
    if (c == null) {
        onClose()
        return
    }
    val freeMen = c.freeMen
    val freeWomen = c.freeWomen
    val choice = remember { mutableStateListOf<Int?>().also { l -> repeat(freeMen.size) { l.add(null) } } }
    var lights by remember { mutableIntStateOf(c.confirmedLights) }
    val used = choice.filterNotNull()
    val complete = used.size == freeMen.size && used.toSet().size == used.size

    AlertDialog(
        onDismissRequest = onClose,
        title = { Text("Matching Night") },
        text = {
            Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                if (c.confirmedLights > 0) {
                    Text(
                        "Bestätigte Paare (${c.confirmedLights}) leuchten automatisch und sind in der Lichter-Zahl enthalten.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                freeMen.forEachIndexed { i, man ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(vm.men[man], modifier = Modifier.width(96.dp), maxLines = 1)
                        val options = freeWomen
                            .filter { it == choice[i] || it !in used }
                            .map { it to vm.women[it] }
                        Picker("Frau wählen", options, choice[i], { choice[i] = it }, Modifier.weight(1f))
                    }
                }
                if (freeWomen.size > freeMen.size) {
                    val left = freeWomen.filter { it !in used }
                    if (complete && left.size == 1) {
                        Text("Ohne Partner: ${vm.women[left[0]]}", style = MaterialTheme.typography.bodySmall)
                    }
                }
                TextButton(onClick = {
                    val tip = vm.result?.let { Advisor.bestNight(c, it) }
                    tip?.couples?.forEach { cp -> choice[freeMen.indexOf(cp.man)] = cp.woman }
                }) { Text("Besten Tipp übernehmen") }
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Lichter:")
                    OutlinedButton(onClick = { if (lights > 0) lights-- }) { Text("−") }
                    Text("$lights", style = MaterialTheme.typography.titleLarge)
                    OutlinedButton(onClick = { if (lights < NUM_MEN) lights++ }) { Text("+") }
                }
            }
        },
        confirmButton = {
            TextButton(enabled = complete, onClick = {
                val couples = freeMen.mapIndexed { i, man -> Couple(choice[i] ?: 0, man) }
                vm.addEvent(Night(couples, lights))
                onClose()
            }) { Text("Speichern") }
        },
        dismissButton = { TextButton(onClick = onClose) { Text("Abbrechen") } },
    )
}

@Composable
private fun BoxDialog(vm: GameViewModel, onClose: () -> Unit) {
    val c = vm.constraints
    if (c == null) {
        onClose()
        return
    }
    var woman by remember { mutableStateOf<Int?>(null) }
    var man by remember { mutableStateOf<Int?>(null) }
    var second by remember { mutableStateOf<Int?>(null) }
    var result by remember { mutableStateOf(BoxResult.NO) }
    val womenOptions = c.freeWomen.map { it to vm.women[it] }
    val menOptions = c.freeMen.map { it to vm.men[it] }
    val secondOptions = c.freeWomen.filter { it != woman }.map { it to vm.women[it] }
    val canSave = woman != null && man != null && (result != BoxResult.DOUBLE || second != null)

    AlertDialog(
        onDismissRequest = onClose,
        title = { Text("Matchbox") },
        text = {
            Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Picker("Frau wählen", womenOptions, woman, { woman = it; if (second == it) second = null })
                Picker("Mann wählen", menOptions, man, { man = it })
                listOf(
                    BoxResult.NO to "Kein Match",
                    BoxResult.YES to "Perfect Match",
                    BoxResult.DOUBLE to "Doppel-Match",
                ).forEach { (value, label) ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = result == value, onClick = { result = value })
                        Text(label)
                    }
                }
                if (result == BoxResult.DOUBLE) {
                    Text("Zweite Frau des Mannes:", style = MaterialTheme.typography.bodySmall)
                    Picker("Zweite Frau wählen", secondOptions, second, { second = it })
                }
            }
        },
        confirmButton = {
            TextButton(enabled = canSave, onClick = {
                vm.addEvent(Matchbox(woman ?: 0, man ?: 0, result, if (result == BoxResult.DOUBLE) second ?: -1 else -1))
                onClose()
            }) { Text("Speichern") }
        },
        dismissButton = { TextButton(onClick = onClose) { Text("Abbrechen") } },
    )
}
