package de.aytomatcher.core

/** Vorschlag für die nächste Matching Night. */
class NightTip(val couples: List<Couple>, val expectedLights: Double)

/** Vorschlag für die nächste Matchbox: Paar mit seiner Wahrscheinlichkeit. */
class BoxTip(val couple: Couple, val probability: Double)

object Advisor {
    /**
     * Paarung der noch freien Männer mit je einer eigenen freien Frau, die die Summe der Wahrscheinlichkeiten
     * (= erwartete Lichter ohne bestätigte Paare) maximiert.
     */
    fun bestNight(c: Constraints, r: SolveResult): NightTip? {
        if (r.total == 0L) return null
        val men = c.freeMen
        val women = c.freeWomen
        if (men.isEmpty() || women.size < men.size) return null
        val nw = women.size
        val size = 1 shl nw
        val neg = Double.NEGATIVE_INFINITY
        // best[mannIndex][frauenMaske]
        val best = Array(men.size + 1) { DoubleArray(size) { neg } }
        val choice = Array(men.size + 1) { IntArray(size) { -1 } }
        best[0][0] = 0.0
        for (mi in men.indices) {
            for (mask in 0 until size) {
                val cur = best[mi][mask]
                if (cur == neg) continue
                for (wi in 0 until nw) {
                    if (mask and (1 shl wi) != 0) continue
                    val nm = mask or (1 shl wi)
                    val v = cur + r.probability(women[wi], men[mi])
                    if (v > best[mi + 1][nm]) {
                        best[mi + 1][nm] = v
                        choice[mi + 1][nm] = wi
                    }
                }
            }
        }
        var bestMask = -1
        var bestVal = neg
        for (mask in 0 until size) {
            if (best[men.size][mask] > bestVal) {
                bestVal = best[men.size][mask]
                bestMask = mask
            }
        }
        if (bestMask < 0) return null
        val couples = ArrayList<Couple>()
        var mask = bestMask
        for (mi in men.size downTo 1) {
            val wi = choice[mi][mask]
            couples += Couple(women[wi], men[mi - 1])
            mask = mask and (1 shl wi).inv()
        }
        couples.sortBy { it.man }
        return NightTip(couples, bestVal)
    }

    /** Die [count] Paare, deren Wahrscheinlichkeit am nächsten bei 50 % liegt (bringt die meiste Information). */
    fun matchboxTips(c: Constraints, r: SolveResult, count: Int = 3): List<BoxTip> {
        if (r.total == 0L) return emptyList()
        val tips = ArrayList<BoxTip>()
        for (w in c.freeWomen) {
            for (m in c.freeMen) {
                val p = r.probability(w, m)
                if (p > 0.0 && p < 1.0) tips += BoxTip(Couple(w, m), p)
            }
        }
        return tips.sortedBy { kotlin.math.abs(it.probability - 0.5) }.take(count)
    }
}
