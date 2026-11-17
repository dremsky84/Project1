package de.aytomatcher.app

import android.content.Context
import de.aytomatcher.core.BoxResult
import de.aytomatcher.core.Couple
import de.aytomatcher.core.Event
import de.aytomatcher.core.Matchbox
import de.aytomatcher.core.Night
import org.json.JSONArray
import org.json.JSONObject

class Saved(
    val women: List<String>,
    val men: List<String>,
    val events: List<Event>,
    val setupDone: Boolean,
)

/** Speichert den Spielstand als JSON in den SharedPreferences. */
class Storage(context: Context) {
    private val prefs = context.getSharedPreferences("aytomatcher", Context.MODE_PRIVATE)

    fun save(s: Saved) {
        val root = JSONObject()
        root.put("women", JSONArray(s.women))
        root.put("men", JSONArray(s.men))
        root.put("setupDone", s.setupDone)
        val ev = JSONArray()
        for (e in s.events) {
            val o = JSONObject()
            when (e) {
                is Night -> {
                    o.put("t", "night")
                    o.put("lights", e.lights)
                    val c = JSONArray()
                    e.couples.forEach { c.put(JSONArray().put(it.woman).put(it.man)) }
                    o.put("c", c)
                }

                is Matchbox -> {
                    o.put("t", "box")
                    o.put("w", e.woman)
                    o.put("m", e.man)
                    o.put("r", e.result.name)
                    o.put("s", e.secondWoman)
                }
            }
            ev.put(o)
        }
        root.put("events", ev)
        prefs.edit().putString("state", root.toString()).apply()
    }

    fun load(): Saved? {
        val text = prefs.getString("state", null) ?: return null
        return try {
            val root = JSONObject(text)
            val women = root.getJSONArray("women").let { a -> List(a.length()) { a.getString(it) } }
            val men = root.getJSONArray("men").let { a -> List(a.length()) { a.getString(it) } }
            val ev = root.getJSONArray("events")
            val events = List(ev.length()) { i ->
                val o = ev.getJSONObject(i)
                if (o.getString("t") == "night") {
                    val c = o.getJSONArray("c")
                    Night(
                        List(c.length()) { j -> Couple(c.getJSONArray(j).getInt(0), c.getJSONArray(j).getInt(1)) },
                        o.getInt("lights"),
                    ) as Event
                } else {
                    Matchbox(o.getInt("w"), o.getInt("m"), BoxResult.valueOf(o.getString("r")), o.getInt("s")) as Event
                }
            }
            Saved(women, men, events, root.getBoolean("setupDone"))
        } catch (e: Exception) {
            null
        }
    }
}
