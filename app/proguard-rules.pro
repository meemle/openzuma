# 添加项目特定的混淆规则
# 更多细节请参考: https://developer.android.com/studio/build/shrink-code

# 如果你使用Gradle 2.3或更高版本，你可以使用android.enableR8=true来启用R8

# 你的项目特定的混淆规则
# 只有在这里添加规则，才会应用于你的发布版本
# 默认情况下，R8为你的项目自动生成混淆规则（不需要修改此文件）
# 了解更多关于混淆的信息，请访问: https://developer.android.com/studio/build/shrink-code.html

# 添加项目特定的混淆规则
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable

# Retrofit使用注解
-keepattributes RuntimeVisibleAnnotations
-keepattributes RuntimeInvisibleAnnotations
-keepattributes RuntimeVisibleParameterAnnotations
-keepattributes RuntimeInvisibleParameterAnnotations

# Retrofit特定的规则
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepattributes Signature
-keepattributes Exceptions

-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# OkHttp
-keepattributes Signature
-keepattributes *Annotation*
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }
-dontwarn okhttp3.**

# Glide
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep public class * extends com.bumptech.glide.module.AppGlideModule
-keep public enum com.bumptech.glide.load.ImageHeaderParser$** {
  **[] $VALUES;
  public *;
}

# Gson
-keep class sun.misc.Unsafe { *; }
-keep class com.google.gson.stream.** { *; }
-keep class com.google.gson.examples.android.model.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase {
  *;
}

# ViewModel
-keep class * extends androidx.lifecycle.ViewModel {
  *;
}

# 保持数据类
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# 保持Parcelable实现
-keep class * implements android.os.Parcelable {
  public static final android.os.Parcelable$Creator *;
}

# 保持序列化
-keepnames class * implements java.io.Serializable

# 保持自定义视图
-keepclassmembers public class * extends android.view.View {
   public <init>(android.content.Context);
   public <init>(android.content.Context, android.util.AttributeSet);
   public <init>(android.content.Context, android.util.AttributeSet, int);
   public void set*(...);
}

# 保持枚举
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# 保持原生方法
-keepclasseswithmembernames class * {
    native <methods>;
}

# 保持所有Activity
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider
-keep public class * extends android.app.backup.BackupAgentHelper
-keep public class * extends android.preference.Preference

# 移除日志
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int i(...);
    public static int w(...);
    public static int d(...);
    public static int e(...);
}

# 保留资源
-keepclassmembers class **.R$* {
    public static <fields>;
}

# 保留自定义异常
-keep public class * extends java.lang.Exception

# WebView相关
-keepclassmembers class * extends android.webkit.WebViewClient {
    public void *(android.webkit.WebView, java.lang.String, android.graphics.Bitmap);
    public boolean *(android.webkit.WebView, java.lang.String);
}
-keepclassmembers class * extends android.webkit.WebViewClient {
    public void *(android.webkit.WebView, jav.lang.String);
}