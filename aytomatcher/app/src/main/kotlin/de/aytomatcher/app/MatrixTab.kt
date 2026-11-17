package de.aytomatcher.app

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import de.aytomatcher.core.BoxResult
import de.aytomatcher.core.Matchbox
import kotlin.math.roundToInt

private val LABEL_WIDTH = 78.dp
private val CELL_SIZE = 36.dp

@Composable
fun MatrixTab(vm: GameViewModel) {
    val r = vm.result
    val c = vm.constraints
    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        InfoCard(vm)
        if (r == null || c == null) {
            Text(if (vm.computing) "Berechne …" else "Noch keine Daten.")
            return@Column
        }
        if (r.total > 0) {
            Text("Wahrscheinlichkeit je Paar in Prozent", style = MaterialTheme.typography.titleSmall)
            Column(Modifier.horizontalScroll(rememberScrollState())) {
                Row {
                    Box(Modifier.width(LABEL_WIDTH))
                    for (m in 0 until NUM_MEN) {
                        Text(
                            vm.men[m].take(3),
                            fontSize = 11.sp,
                            textAlign = TextAlign.Center,
                            modifier = Modifier
                                .width(CELL_SIZE)
                                .padding(bottom = 4.dp),
                            maxLines = 1,
                        )
                    }
                }
                for (w in 0 until NUM_WOMEN) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            vm.women[w].take(10),
                            fontSize = 12.sp,
                            maxLines = 1,
                            modifier = Modifier.width(LABEL_WIDTH),
                        )
                        for (m in 0 until NUM_MEN) {
                            Cell(r.probability(w, m), confirmed = c.confirmedWomen[w] && r.marginals[w][m] == r.total)
                        }
                    }
                }
            }
            Text("Spaltenköpfe sind die ersten Buchstaben der Männer-Namen. Grün: bestätigt.", style = MaterialTheme.typography.bodySmall)
            DoubleCard(vm)
        }
    }
}

@Composable
private fun InfoCard(vm: GameViewModel) {
    val r = vm.result
    val c = vm.constraints
    val nights = vm.events.count { it is de.aytomatcher.core.Night }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        when {
            vm.failure != null -> Text(vm.failure ?: "", color = MaterialTheme.colorScheme.error)
            r == null -> Text("Berechne …")
            r.contradiction != null -> {
                Text("Widerspruch in den Eingaben", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.titleMedium)
                Text(r.contradiction ?: "")
                Text("Lösche im Tab Verlauf das letzte Ereignis und prüfe die Eingabe.")
            }

            r.total == 0L -> {
                Text("Keine Lösung mehr möglich", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.titleMedium)
                Text("Die Eingaben widersprechen sich. Lösche im Tab Verlauf das letzte Ereignis und prüfe die Eingabe.")
            }

            else -> {
                Text("Mögliche Lösungen", style = MaterialTheme.typography.labelMedium)
                Text(formatCount(r.total), style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
                if (r.total == 1L) Text("Alle Perfect Matches sind eindeutig bestimmt!", color = Green)
            }
        }
        if (c != null) {
            Text(
                "Matching Nights: $nights von 10 · Bestätigte Lichter: ${c.confirmedLights}",
                style = MaterialTheme.typography.bodySmall,
            )
        }
        if (vm.computing) Text("Berechne …", style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun Cell(p: Double, confirmed: Boolean) {
    val bg = when {
        confirmed -> Green
        p <= 0.0 -> CellEmpty
        else -> lerp(Color(0xFF3A2A4A), Pink, p.toFloat().coerceIn(0f, 1f))
    }
    val text = when {
        confirmed -> "✓"
        p <= 0.0 -> "·"
        p >= 0.995 -> "100"
        p < 0.005 -> "<1"
        else -> (p * 100).roundToInt().coerceAtLeast(1).toString()
    }
    Box(
        Modifier
            .padding(1.dp)
            .size(CELL_SIZE - 2.dp)
            .clip(RoundedCornerShape(4.dp))
            .background(bg),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, fontSize = 11.sp, color = if (confirmed) Color.Black else Color.White)
    }
}

@Composable
private fun DoubleCard(vm: GameViewModel) {
    val r = vm.result ?: return
    val c = vm.constraints ?: return
    val doubleConfirmed = vm.events.any { it is Matchbox && it.result == BoxResult.DOUBLE }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text("Wer hat das Doppel-Match?", style = MaterialTheme.typography.titleSmall)
        if (doubleConfirmed) {
            Text("Bereits bestätigt.", color = Green)
        } else {
            val rows = (0 until NUM_MEN).filter { !c.confirmedMen[it] }
                .map { it to r.doubleProbability(it) }
                .sortedByDescending { it.second }
            rows.forEach { (m, p) ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(vm.men[m], modifier = Modifier.width(110.dp), maxLines = 1)
                    Box(
                        Modifier
                            .height(10.dp)
                            .width((150 * p.coerceIn(0.0, 1.0)).dp.coerceAtLeast(2.dp))
                            .clip(RoundedCornerShape(5.dp))
                            .background(Pink),
                    )
                    Text("  ${(p * 100).roundToInt()} %", fontSize = 12.sp)
                }
            }
        }
    }
}
