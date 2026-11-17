package de.aytomatcher.app

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun SetupScreen(vm: GameViewModel) {
    val women = remember { mutableStateListOf<String>().also { it.addAll(vm.women) } }
    val men = remember { mutableStateListOf<String>().also { it.addAll(vm.men) } }
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        item {
            Column(Modifier.padding(top = 16.dp)) {
                Text("AytO Matcher", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.primary)
                Text(
                    "Trage die Namen der 11 Frauen und 10 Männer ein. Leere Felder bekommen einen Standardnamen.",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(top = 8.dp),
                )
                Text("Frauen", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
            }
        }
        itemsIndexed(women) { i, name ->
            OutlinedTextField(
                value = name,
                onValueChange = { women[i] = it },
                label = { Text("Frau ${i + 1}") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item { Text("Männer", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp)) }
        itemsIndexed(men) { i, name ->
            OutlinedTextField(
                value = name,
                onValueChange = { men[i] = it },
                label = { Text("Mann ${i + 1}") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Button(
                onClick = { vm.saveSetup(women.toList(), men.toList()) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
            ) { Text("Los geht's") }
        }
    }
}
