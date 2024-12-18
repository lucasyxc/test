package com.rnmonitorapp

import android.content.Intent
import android.os.Build
import android.Manifest
import android.content.pm.PackageManager
import android.os.Environment
import android.util.Log
import androidx.core.content.ContextCompat
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.bridge.Promise

class PDFMonitorModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    private val TAG = "PDFMonitorModule"

    override fun getName() = "PDFMonitorService"

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
    fun startService(promise: Promise) {
        try {
            if (!checkPermissions()) {
                promise.reject("ERROR", "Required permissions not granted")
                return
            }

            val intent = Intent(reactApplicationContext, PDFMonitorService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                reactApplicationContext.startForegroundService(intent)
            } else {
                reactApplicationContext.startService(intent)
            }
            Log.i(TAG, "PDF Monitor Service started successfully")
            promise.resolve(null)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start PDFMonitorService", e)
            promise.reject("ERROR", "Failed to start PDFMonitorService: ${e.message}")
        }
    }

    @ReactMethod
    fun stopService(promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, PDFMonitorService::class.java)
            reactApplicationContext.stopService(intent)
            Log.i(TAG, "PDF Monitor Service stopped successfully")
            promise.resolve(null)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop PDFMonitorService", e)
            promise.reject("ERROR", "Failed to stop PDFMonitorService: ${e.message}")
        }
    }
}
