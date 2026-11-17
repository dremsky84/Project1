package de.aytomatcher.core

/** Ergebnis der Berechnung: Anzahl aller noch möglichen Lösungen und wie oft jedes Paar darin vorkommt. */
class SolveResult(
    val numMen: Int,
    val total: Long,
    /** marginals[frau][mann] = Anzahl der gültigen Lösungen, in denen dieses Paar ein Perfect Match ist. */
    val marginals: Array<LongArray>,
    val contradiction: String?,
) {
    /** Wahrscheinlichkeit (0..1), dass Frau [w] und Mann [m] ein Perfect Match sind. */
    fun probability(w: Int, m: Int): Double = if (total == 0L) 0.0 else marginals[w][m].toDouble() / total

    /** Wahrscheinlichkeit (0..1), dass Mann [m] das Doppel-Match hat. */
    fun doubleProbability(m: Int): Double {
        if (total == 0L) return 0.0
        var sum = 0.0
        for (w in marginals.indices) sum += marginals[w][m].toDouble()
        return sum / total - 1.0
    }
}

class StateLimitException(message: String) : RuntimeException(message)

/**
 * Zählt exakt alle Zuordnungen "jede Frau genau ein Mann, jeder Mann mindestens eine Frau", die zu allen
 * Matchbox-Ergebnissen und Lichter-Anzahlen passen.
 *
 * Verfahren: Dynamic Programming über die Frauen. Ein Zustand besteht aus der Menge der schon vergebenen Männer,
 * einem Merker "Doppel-Match schon vergeben" und den bisherigen Treffern je Matching Night. Gleiche Zustände
 * werden zusammengefasst, statt 200 Mio. Lösungen einzeln durchzugehen.
 */
object Solver {
    private const val MAX_NIGHTS = 12
    private const val DEFAULT_STATE_LIMIT = 20_000_000

    fun solve(numMen: Int, events: List<Event>, stateLimit: Int = DEFAULT_STATE_LIMIT): SolveResult =
        solve(derive(numMen, events), stateLimit)

    fun solve(c: Constraints, stateLimit: Int = DEFAULT_STATE_LIMIT): SolveResult {
        val m = c.numMen
        val w = c.numWomen
        val empty = Array(w) { LongArray(m) }
        if (c.contradiction != null) return SolveResult(m, 0, empty, c.contradiction)
        if (c.nights.size > MAX_NIGHTS) {
            return SolveResult(m, 0, empty, "Mehr als $MAX_NIGHTS Matching Nights werden nicht unterstützt.")
        }

        val nights = c.nights
        val nightCount = nights.size
        val full = (1 shl m) - 1
        val fullL = full.toLong()
        val hitsMask = -1L shl (m + 1)

        // hitInc[frau][mann]: Welche Nacht-Zähler erhöhen sich, wenn die Frau diesen Mann bekommt.
        val hitInc = Array(w) { LongArray(m) }
        val nightsOf = Array(w) { wi -> nights.indices.filter { nights[it].partner[wi] >= 0 }.toIntArray() }
        for (n in 0 until nightCount) {
            for (wi in 0 until w) {
                val p = nights[n].partner[wi]
                if (p >= 0) hitInc[wi][p] += 1L shl (m + 1 + 4 * n)
            }
        }
        // rem[n][wi] = Anzahl der Paare der Night n bei Frauen mit Index >= wi
        val rem = Array(nightCount) { n ->
            IntArray(w + 2).also { r ->
                for (wi in w - 1 downTo 0) r[wi] = r[wi + 1] + if (nights[n].partner[wi] >= 0) 1 else 0
            }
        }
        val lightsOf = IntArray(nightCount) { nights[it].lights }
        // Männer, die von Frauen mit Index >= wi überhaupt noch erreicht werden können.
        val unionSuffix = IntArray(w + 2)
        for (wi in w - 1 downTo 0) unionSuffix[wi] = unionSuffix[wi + 1] or c.allowed[wi]
        val noDouble = c.noDouble

        fun child(wi: Int, key: Long, man: Int): Long {
            val bit = 1 shl man
            val mask = (key and fullL).toInt()
            val d = ((key shr m) and 1L).toInt()
            val newMask: Int
            val nd: Int
            if (mask and bit == 0) {
                newMask = mask or bit
                nd = d
            } else {
                if (d == 1 || (noDouble and bit) != 0) return -1
                newMask = mask
                nd = 1
            }
            if ((full and newMask.inv()) and unionSuffix[wi + 1].inv() != 0) return -1
            val k = newMask.toLong() or (nd.toLong() shl m) or ((key and hitsMask) + hitInc[wi][man])
            for (n in nightsOf[wi]) {
                val h = ((k shr (m + 1 + 4 * n)) and 15L).toInt()
                if (h > lightsOf[n] || h + rem[n][wi + 1] < lightsOf[n]) return -1
            }
            return k
        }

        // Vorwärts: erreichbare Zustände je Frau mit der Anzahl der Wege dorthin.
        val layers = ArrayList<Layer>(w + 1)
        layers += Layer().also { it.add(0L, 1L) }
        for (wi in 0 until w) {
            val cur = layers[wi]
            val next = Layer()
            for (i in 0 until cur.size) {
                val key = cur.keys[i]
                val f = cur.vals[i]
                var am = c.allowed[wi]
                while (am != 0) {
                    val man = Integer.numberOfTrailingZeros(am)
                    am = am and (am - 1)
                    val k = child(wi, key, man)
                    if (k >= 0) next.add(k, f)
                }
            }
            if (next.size > stateLimit) throw StateLimitException("Zu viele Zustände (${next.size}).")
            layers += next
        }

        // Rückwärts: Anzahl der Vervollständigungen je Zustand; dabei die Paar-Häufigkeiten sammeln.
        val completions = Array(w + 1) { LongArray(layers[it].size) }
        val last = layers[w]
        for (i in 0 until last.size) {
            val key = last.keys[i]
            val ok = (key and fullL) == fullL && ((key shr m) and 1L) == 1L
            completions[w][i] = if (ok) 1L else 0L
        }
        val marginals = Array(w) { LongArray(m) }
        for (wi in w - 1 downTo 0) {
            val cur = layers[wi]
            val nextLayer = layers[wi + 1]
            val nextCompletions = completions[wi + 1]
            for (i in 0 until cur.size) {
                val key = cur.keys[i]
                val f = cur.vals[i]
                var sum = 0L
                var am = c.allowed[wi]
                while (am != 0) {
                    val man = Integer.numberOfTrailingZeros(am)
                    am = am and (am - 1)
                    val k = child(wi, key, man)
                    if (k < 0) continue
                    val n = nextCompletions[nextLayer.indexOf(k)]
                    if (n > 0) {
                        sum += n
                        marginals[wi][man] += f * n
                    }
                }
                completions[wi][i] = sum
            }
        }
        val total = completions[0][0]
        return SolveResult(m, total, if (total == 0L) empty else marginals, null)
    }

    /** Hash-Map von Zustand (Long) auf Wege-Anzahl, mit dichten Arrays zum schnellen Durchlaufen. */
    private class Layer {
        var keys = LongArray(64)
        var vals = LongArray(64)
        var size = 0
        private var table = IntArray(128) { -1 }
        private var shift = 64 - 7

        private fun slot(key: Long): Int = ((key * -7046029254386353131L) ushr shift).toInt()

        fun indexOf(key: Long): Int {
            val mask = table.size - 1
            var i = slot(key)
            while (true) {
                val idx = table[i]
                if (idx < 0) return -1
                if (keys[idx] == key) return idx
                i = (i + 1) and mask
            }
        }

        fun add(key: Long, v: Long) {
            val mask = table.size - 1
            var i = slot(key)
            while (true) {
                val idx = table[i]
                if (idx < 0) {
                    if (size == keys.size) {
                        keys = keys.copyOf(size * 2)
                        vals = vals.copyOf(size * 2)
                    }
                    keys[size] = key
                    vals[size] = v
                    table[i] = size
                    size++
                    if (size * 2 > table.size) rehash()
                    return
                }
                if (keys[idx] == key) {
                    vals[idx] += v
                    return
                }
                i = (i + 1) and mask
            }
        }

        private fun rehash() {
            table = IntArray(table.size * 2) { -1 }
            shift -= 1
            val mask = table.size - 1
            for (idx in 0 until size) {
                var i = slot(keys[idx])
                while (table[i] >= 0) i = (i + 1) and mask
                table[i] = idx
            }
        }
    }
}
