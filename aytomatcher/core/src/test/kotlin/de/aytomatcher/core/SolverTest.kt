package de.aytomatcher.core

import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class SolverTest {
    /** Verdeckte "Wahrheit": truth[frau] = Mann. */
    private fun randomTruth(m: Int, rnd: Random): IntArray {
        val w = m + 1
        val men = (0 until m).shuffled(rnd)
        val truth = IntArray(w)
        val women = (0 until w).shuffled(rnd)
        for (i in 0 until m) truth[women[i]] = men[i]
        truth[women[m]] = rnd.nextInt(m)
        return truth
    }

    /** Spielt eine Staffel anhand der Wahrheit durch und erzeugt die Ereignisse, die die Show zeigen würde. */
    private fun simulate(m: Int, truth: IntArray, nights: Int, boxes: Int, rnd: Random): List<Event> {
        val w = m + 1
        val events = ArrayList<Event>()
        val cw = BooleanArray(w)
        val cm = BooleanArray(m)
        var confirmedLights = 0
        val order = (List(nights) { 'N' } + List(boxes) { 'B' }).shuffled(rnd)
        for (kind in order) {
            val fw = (0 until w).filter { !cw[it] }
            val fm = (0 until m).filter { !cm[it] }
            if (fm.isEmpty()) break
            if (kind == 'N') {
                val shuffledW = fw.shuffled(rnd)
                val couples = fm.mapIndexed { i, man -> Couple(shuffledW[i], man) }
                val hits = couples.count { truth[it.woman] == it.man }
                events += Night(couples, confirmedLights + hits)
            } else {
                val wo = fw.random(rnd)
                val ma = fm.random(rnd)
                if (truth[wo] != ma) {
                    events += Matchbox(wo, ma, BoxResult.NO)
                } else {
                    val others = (0 until w).filter { it != wo && truth[it] == ma }
                    if (others.isEmpty()) {
                        events += Matchbox(wo, ma, BoxResult.YES)
                        cw[wo] = true
                        cm[ma] = true
                    } else {
                        events += Matchbox(wo, ma, BoxResult.DOUBLE, others[0])
                        cw[wo] = true
                        cw[others[0]] = true
                        cm[ma] = true
                    }
                    confirmedLights++
                }
            }
        }
        return events
    }

    /** Ground truth by brute force: alle Zuordnungen durchprobieren und die Ereignisse direkt prüfen. */
    private fun bruteForce(m: Int, events: List<Event>): Pair<Long, Array<LongArray>> {
        val w = m + 1
        val f = IntArray(w)
        var total = 0L
        val marg = Array(w) { LongArray(m) }

        fun consistent(): Boolean {
            val counts = IntArray(m)
            f.forEach { counts[it]++ }
            if (counts.any { it == 0 } || counts.count { it == 2 } != 1) return false
            val cw = BooleanArray(w)
            val cm = BooleanArray(m)
            var cl = 0
            for (e in events) {
                when (e) {
                    is Night -> {
                        val free = e.couples.filter { !cw[it.woman] && !cm[it.man] }
                        if (cl + free.count { f[it.woman] == it.man } != e.lights) return false
                    }

                    is Matchbox -> {
                        val match = f[e.woman] == e.man
                        when (e.result) {
                            BoxResult.NO -> if (match) return false
                            BoxResult.YES -> {
                                if (!match || counts[e.man] != 1) return false
                                cw[e.woman] = true; cm[e.man] = true; cl++
                            }
                            BoxResult.DOUBLE -> {
                                if (!match || counts[e.man] != 2 || f[e.secondWoman] != e.man) return false
                                cw[e.woman] = true; cw[e.secondWoman] = true; cm[e.man] = true; cl++
                            }
                        }
                    }
                }
            }
            return true
        }

        fun rec(i: Int) {
            if (i == w) {
                if (consistent()) {
                    total++
                    for (x in 0 until w) marg[x][f[x]]++
                }
                return
            }
            for (man in 0 until m) {
                f[i] = man
                rec(i + 1)
            }
        }
        rec(0)
        return total to marg
    }

    @Test
    fun unconstrainedCountMatchesFormula() {
        val r = Solver.solve(10, emptyList())
        assertEquals(199_584_000L, r.total)
        // gleichverteilt: jedes Paar in total/10 Lösungen
        for (wo in 0 until 11) for (ma in 0 until 10) assertEquals(r.total / 10, r.marginals[wo][ma])
    }

    @Test
    fun matchesBruteForceOnSmallGames() {
        val rnd = Random(1234)
        var checked = 0
        repeat(300) { iter ->
            val m = if (iter % 2 == 0) 4 else 5
            val truth = randomTruth(m, rnd)
            val events = simulate(m, truth, rnd.nextInt(0, 5), rnd.nextInt(0, 6), rnd)
            val (bt, bm) = bruteForce(m, events)
            val r = Solver.solve(m, events)
            assertTrue(bt > 0, "Wahrheit muss konsistent sein")
            assertEquals(bt, r.total, "Gesamtzahl bei Seed-Iteration $iter: $events")
            for (wo in 0..m) for (ma in 0 until m) {
                assertEquals(bm[wo][ma], r.marginals[wo][ma], "Paar $wo/$ma bei Iteration $iter")
            }
            checked++
        }
        println("Brute-Force-Vergleiche bestanden: $checked")
    }

    @Test
    fun contradictionGivesZero() {
        // Night mit 5 Lichtern, aber nur 4 Paare möglich nach Bestätigung -> Widerspruch
        val events = listOf(
            Matchbox(0, 0, BoxResult.YES),
            Night(listOf(Couple(1, 1), Couple(2, 2)), 0),
        )
        val r = Solver.solve(3, events)
        assertEquals(0L, r.total)
        assertNotNull(r.contradiction)
    }

    @Test
    fun doubleMatchConfirmedLeavesNineByNine() {
        val r = Solver.solve(10, listOf(Matchbox(0, 0, BoxResult.DOUBLE, 1)))
        assertEquals(362_880L, r.total)
    }

    @Test
    fun realisticSeasonIsFastAndKeepsTruth() {
        val rnd = Random(99)
        repeat(5) {
            val truth = randomTruth(10, rnd)
            val events = simulate(10, truth, 6, 4, rnd)
            val t0 = System.nanoTime()
            val r = Solver.solve(10, events)
            val ms = (System.nanoTime() - t0) / 1_000_000
            println("Realistische Staffel: ${events.size} Ereignisse, ${r.total} Lösungen, $ms ms")
            assertTrue(r.total > 0)
            for (wo in 0 until 11) assertTrue(r.marginals[wo][truth[wo]] > 0)
        }
    }

    @Test
    fun worstCaseManyNightsWithMidLights() {
        // Ungünstig: viele Nights mit mittleren Lichter-Zahlen
        val rnd = Random(7)
        val truth = randomTruth(10, rnd)
        val events = simulate(10, truth, 10, 0, rnd)
        val t0 = System.nanoTime()
        val r = Solver.solve(10, events)
        val ms = (System.nanoTime() - t0) / 1_000_000
        println("10 Nights ohne Matchbox: ${r.total} Lösungen, $ms ms")
        assertTrue(r.total > 0)
    }

    @Test
    fun advisorReturnsValidSuggestions() {
        val rnd = Random(5)
        val truth = randomTruth(10, rnd)
        val events = simulate(10, truth, 3, 2, rnd)
        val c = derive(10, events)
        val r = Solver.solve(c)
        val tip = Advisor.bestNight(c, r)
        assertNotNull(tip)
        assertEquals(c.freeMen.size, tip.couples.size)
        assertEquals(tip.couples.map { it.woman }.toSet().size, tip.couples.size)
        assertTrue(Advisor.matchboxTips(c, r).isNotEmpty())
    }
}
