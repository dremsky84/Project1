package de.aytomatcher.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import de.aytomatcher.core.Advisor
import kotlin.math.roundToInt

@Composable
fun TipsTab(vm: GameViewModel) {
    val c = vm.constraints
    val r = vm.result
    val nightTip = remember(c, r) { if (c != null && r != null) Advisor.bestNight(c, r) else null }
    val boxTips = remember(c, r) { if (c != null && r != null) Advisor.matchboxTips(c, r) else emptyList() }
    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (c == null || r == null || r.total == 0L) {
            Text("Noch keine Empfehlung möglich. Prüfe die Eingaben im Tab Matrix.")
            return@Column
        }
        Text("Nächste Matching Night", style = MaterialTheme.typography.titleMedium)
        if (nightTip == null) {
            Text("Kein Vorschlag verfügbar.")
        } else {
            Text(
                "Dieses Paarungs-Set hat die höchste erwartete Lichter-Zahl: " +
                    String.format(java.util.Locale.GERMANY, "%.2f", nightTip.expectedLights + c.confirmedLights) +
                    " (inklusive ${c.confirmedLights} bestätigter).",
                style = MaterialTheme.typography.bodySmall,
            )
            nightTip.couples.forEach {
                Text("${vm.men[it.man]} + ${vm.women[it.woman]}  (${(r.probability(it.woman, it.man) * 100).roundToInt()} %)")
            }
        }
        Text("Nächste Matchbox", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
        Text(
            "Paare mit einer Wahrscheinlichkeit nahe 50 % bringen die meiste Information.",
            style = MaterialTheme.typography.bodySmall,
        )
        if (boxTips.isEmpty()) Text("Kein Vorschlag verfügbar.")
        boxTips.forEach {
            Text("${vm.men[it.couple.man]} + ${vm.women[it.couple.woman]}  (${(it.probability * 100).roundToInt()} %)")
        }
    }
}
