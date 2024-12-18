package com.rnmonitorapp

import android.content.Intent
import android.net.Uri
import android.os.PowerManager
import android.provider.Settings
import android.content.Context

import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.bridge.Promise

class PowerManagerModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    override fun getName(): String {
        return "PowerManagerModule"
    }

    @ReactMethod
    fun requestIgnoreBatteryOptimizations(packageName: String, promise: Promise) {
        try {
            val pm = reactApplicationContext.getSystemService(Context.POWER_SERVICE) as PowerManager
            if (pm.isIgnoringBatteryOptimizations(packageName)) {
                promise.resolve(true)
                return
            }

            val intent = Intent().apply {
                action = Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
                data = Uri.parse("package:$packageName")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            reactApplicationContext.startActivity(intent)
            promise.resolve(true)
        } catch (e: Exception) {
            promise.reject("ERROR", e.message)
        }
    }

    @ReactMethod
    fun isIgnoringBatteryOptimizations(packageName: String, promise: Promise) {
        try {
            val pm = reactApplicationContext.getSystemService(Context.POWER_SERVICE) as PowerManager
            promise.resolve(pm.isIgnoringBatteryOptimizations(packageName))
        } catch (e: Exception) {
            promise.reject("ERROR", e.message)
        }
    }
}
