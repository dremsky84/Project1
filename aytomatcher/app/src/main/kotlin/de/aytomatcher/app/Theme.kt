package de.aytomatcher.app

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import java.util.Locale

val Pink = Color(0xFFFF4D8D)
val Background = Color(0xFF12121A)
val SurfaceColor = Color(0xFF1E1E2A)
val CellEmpty = Color(0xFF262633)
val Green = Color(0xFF3DDC84)

private val Colors = darkColorScheme(
    primary = Pink,
    onPrimary = Color.White,
    background = Background,
    onBackground = Color(0xFFEDEDF5),
    surface = SurfaceColor,
    onSurface = Color(0xFFEDEDF5),
    surfaceVariant = Color(0xFF2A2A38),
    onSurfaceVariant = Color(0xFFB8B8C8),
    secondary = Color(0xFFB388FF),
)

@Composable
fun AytoTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = Colors, content = content)
}

/** Zahl mit deutschem Tausenderpunkt, z. B. 199.584.000. */
fun formatCount(n: Long): String = String.format(Locale.GERMANY, "%,d", n)
