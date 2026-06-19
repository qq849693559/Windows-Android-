# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in the SDK tools.

# Keep Python native library interfaces
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep MainActivity
-keep class com.example.musicplayer.MainActivity { *; }

# Keep PyQt related classes
-keep class org.qtproject.** { *; }
-dontwarn org.qtproject.**

# General Android rules
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
