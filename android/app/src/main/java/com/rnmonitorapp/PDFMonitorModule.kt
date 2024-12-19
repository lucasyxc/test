package com.rnmonitorapp

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Environment
import android.util.Log
import androidx.core.content.ContextCompat
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.bridge.Promise
import com.facebook.react.modules.core.DeviceEventManagerModule

class PDFMonitorModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    private val TAG = "PDFMonitorModule"

    override fun getName() = "PDFMonitorModule"

    private fun checkPermissions(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(reactApplicationContext, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Notification permission not granted")
                return false
            }
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                Log.e(TAG, "Storage permission (MANAGE_EXTERNAL_STORAGE) not granted")
                return false
            }
        } else {
            val readPermission = ContextCompat.checkSelfPermission(
                reactApplicationContext,
                Manifest.permission.READ_EXTERNAL_STORAGE
            )
            val writePermission = ContextCompat.checkSelfPermission(
                reactApplicationContext,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
            if (readPermission != PackageManager.PERMISSION_GRANTED ||
                writePermission != PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Storage permissions not granted")
                return false
            }
        }
        return true
    }

    @ReactMethod
    fun checkPermissionsStatus(promise: Promise) {
        try {
            val hasPermissions = checkPermissions()
            promise.resolve(hasPermissions)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to check permissions: ${e.message}")
        }
    }

    @ReactMethod
    fun notifyNewPDF(filePath: String) {
        try {
            reactApplicationContext
                .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                .emit("onNewPDF", filePath)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to emit new PDF event", e)
        }
    }
}
