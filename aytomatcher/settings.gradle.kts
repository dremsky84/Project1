pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    // Versionen zentral; aufgelöst wird ein Plugin erst, wenn ein Modul es anwendet.
    plugins {
        id("com.android.application") version "8.7.3"
        id("org.jetbrains.kotlin.android") version "2.0.21"
        id("org.jetbrains.kotlin.jvm") version "2.0.21"
        id("org.jetbrains.kotlin.plugin.compose") version "2.0.21"
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "AytO-Matcher"

include(":core")
// Mit -PcoreOnly wird nur der Rechenkern gebaut (ohne Android-SDK, z. B. für Tests in der Cloud-Sandbox).
if (!providers.gradleProperty("coreOnly").isPresent) {
    include(":app")
}
