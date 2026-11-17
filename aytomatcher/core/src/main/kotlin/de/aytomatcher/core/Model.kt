package de.aytomatcher.core

/** Ein Paar aus Frau und Mann, jeweils als Index (Frauen 0..M, Männer 0..M-1). */
data class Couple(val woman: Int, val man: Int)

/** Ergebnis einer Matchbox. */
enum class BoxResult {
    /** Kein Perfect Match. */
    NO,

    /** Perfect Match, der Mann hat nur diese eine Frau. */
    YES,

    /** Doppel-Match: Der Mann hat zwei Perfect Matches (Frau + zweite Frau). */
    DOUBLE,
}

/** Ein Ereignis aus der Sendung, in der Reihenfolge, in der es passiert ist. */
sealed interface Event

/**
 * Matching Night. [couples] sind die gebildeten Paare der noch im Haus lebenden Personen,
 * [lights] ist die in der Show angezeigte Lichter-Anzahl (inklusive bereits bestätigter Paare).
 */
data class Night(val couples: List<Couple>, val lights: Int) : Event

/** Matchbox für das Paar [woman]/[man]. Bei [BoxResult.DOUBLE] ist [secondWoman] die zweite Frau. */
data class Matchbox(
    val woman: Int,
    val man: Int,
    val result: BoxResult,
    val secondWoman: Int = -1,
) : Event
