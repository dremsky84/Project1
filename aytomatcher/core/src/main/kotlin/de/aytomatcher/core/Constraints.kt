package de.aytomatcher.core

/** Eine Matching Night als Bedingung: Genau [lights] der Paare in [partner] müssen stimmen. */
class NightConstraint(
    /** partner[frau] = Mann, mit dem diese Frau in der Night gepaart wurde, oder -1. */
    val partner: IntArray,
    /** Anzahl der Lichter ohne die bereits bestätigten Paare. */
    val lights: Int,
)

/**
 * Aus den Ereignissen abgeleiteter Wissensstand.
 * Es gibt [numMen] Männer und numMen + 1 Frauen; genau ein Mann hat zwei Perfect Matches.
 */
class Constraints(val numMen: Int) {
    val numWomen: Int = numMen + 1

    /** allowed[frau] = Bitmaske der Männer, die für diese Frau noch möglich sind. */
    val allowed = IntArray(numWomen) { (1 shl numMen) - 1 }

    /** Männer, die nur ein Match haben dürfen (per Matchbox als einzelnes Match bestätigt). */
    var noDouble = 0

    val nights = ArrayList<NightConstraint>()
    val confirmedWomen = BooleanArray(numWomen)
    val confirmedMen = BooleanArray(numMen)

    /** Dauerhaft leuchtende Lichter durch bestätigte Paare (ein Doppel-Match zählt als ein Licht). */
    var confirmedLights = 0

    /** Gesetzt, wenn die Eingaben sich offensichtlich widersprechen. */
    var contradiction: String? = null

    val freeWomen: List<Int> get() = (0 until numWomen).filter { !confirmedWomen[it] }
    val freeMen: List<Int> get() = (0 until numMen).filter { !confirmedMen[it] }

    fun markContradiction(text: String) {
        if (contradiction == null) contradiction = text
    }
}

/** Leitet aus der Ereignisliste die Bedingungen für den Solver ab. */
fun derive(numMen: Int, events: List<Event>): Constraints {
    val c = Constraints(numMen)
    var nightNo = 0
    var boxNo = 0
    for (e in events) {
        when (e) {
            is Night -> {
                nightNo++
                val free = e.couples.filter { !c.confirmedWomen[it.woman] && !c.confirmedMen[it.man] }
                val l = e.lights - c.confirmedLights
                if (l < 0 || l > free.size) {
                    c.markContradiction(
                        "Matching Night $nightNo: ${e.lights} Lichter passen nicht zu ${free.size} freien Paaren " +
                            "und ${c.confirmedLights} bestätigten Lichtern.",
                    )
                    continue
                }
                when {
                    l == 0 -> free.forEach { c.allowed[it.woman] = c.allowed[it.woman] and (1 shl it.man).inv() }
                    l == free.size -> free.forEach { c.allowed[it.woman] = c.allowed[it.woman] and (1 shl it.man) }
                    else -> {
                        val partner = IntArray(c.numWomen) { -1 }
                        free.forEach { partner[it.woman] = it.man }
                        c.nights += NightConstraint(partner, l)
                    }
                }
            }

            is Matchbox -> {
                boxNo++
                val bit = 1 shl e.man
                when (e.result) {
                    BoxResult.NO -> c.allowed[e.woman] = c.allowed[e.woman] and bit.inv()

                    BoxResult.YES -> {
                        for (w in 0 until c.numWomen) {
                            c.allowed[w] = if (w == e.woman) c.allowed[w] and bit else c.allowed[w] and bit.inv()
                        }
                        c.noDouble = c.noDouble or bit
                        c.confirmedWomen[e.woman] = true
                        c.confirmedMen[e.man] = true
                        c.confirmedLights++
                    }

                    BoxResult.DOUBLE -> {
                        if (e.secondWoman < 0 || e.secondWoman == e.woman) {
                            c.markContradiction("Matchbox $boxNo: Doppel-Match braucht eine zweite, andere Frau.")
                            continue
                        }
                        for (w in 0 until c.numWomen) {
                            c.allowed[w] =
                                if (w == e.woman || w == e.secondWoman) c.allowed[w] and bit else c.allowed[w] and bit.inv()
                        }
                        c.confirmedWomen[e.woman] = true
                        c.confirmedWomen[e.secondWoman] = true
                        c.confirmedMen[e.man] = true
                        c.confirmedLights++
                    }
                }
            }
        }
    }
    return c
}
