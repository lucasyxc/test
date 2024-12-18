package com.rnmonitorapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.util.Log;
import android.content.pm.PackageManager;
import android.Manifest;
import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import com.facebook.react.HeadlessJsTaskService;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.jstasks.HeadlessJsTaskConfig;

import java.util.concurrent.TimeUnit;

public class PDFMonitorService extends HeadlessJsTaskService {
    private static final String TAG = "PDFMonitorService";
    private static final String TASK_NAME = "PDFMonitorTask";
    private static final long TIMEOUT = TimeUnit.DAYS.toMillis(1); // 1 day timeout
    private static final String CHANNEL_ID = "pdf_monitor_service";
    private static final int NOTIFICATION_ID = 1;
    private PowerManager.WakeLock wakeLock;

    @Override
    public void onCreate() {
        super.onCreate();
        try {
            if (!checkPermissions()) {
                Log.e(TAG, "Required permissions not granted. Stopping service.");
                stopSelf();
                return;
            }
            createNotificationChannel();
            startForeground(NOTIFICATION_ID, buildNotification());
            acquireWakeLock();
            Log.i(TAG, "PDF Monitor Service started successfully");
        } catch (Exception e) {
            Log.e(TAG, "Error starting service", e);
            stopSelf();
        }
    }

    private boolean checkPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Notification permission not granted");
                return false;
            }
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.MANAGE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Storage permission not granted");
                return false;
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
                Log.e(TAG, "Storage permission not granted");
                return false;
            }
        }
        return true;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "PDF Monitor Service",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Used to keep the PDF monitoring service running");
            NotificationManager notificationManager = getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);
        }
    }

    private Notification buildNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
            this,
            0,
            notificationIntent,
            PendingIntent.FLAG_IMMUTABLE
        );

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("PDF监控服务")
            .setContentText("正在监控下载文件夹中的PDF文件")
            .setSmallIcon(android.R.drawable.ic_menu_view)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pendingIntent)
            .setOngoing(true);

        return builder.build();
    }

    @Override
    protected @Nullable HeadlessJsTaskConfig getTaskConfig(Intent intent) {
        try {
            Bundle extras = intent.getExtras();
            WritableMap data = extras != null ? Arguments.fromBundle(extras) : Arguments.createMap();
            return new HeadlessJsTaskConfig(
                TASK_NAME,
                data,
                TIMEOUT,
                true // Allow the task to run in foreground
            );
        } catch (Exception e) {
            Log.e(TAG, "Error creating task config", e);
            return null;
        }
    }

    private void acquireWakeLock() {
        try {
            PowerManager powerManager = (PowerManager) getSystemService(POWER_SERVICE);
            if (powerManager != null) {
                wakeLock = powerManager.newWakeLock(
                    PowerManager.PARTIAL_WAKE_LOCK,
                    "PDFMonitorService::WakeLock"
                );
                wakeLock.setReferenceCounted(false);
                wakeLock.acquire(TIMEOUT);
                Log.i(TAG, "Wake lock acquired successfully");
            } else {
                Log.e(TAG, "PowerManager service not available");
            }
        } catch (Exception e) {
            Log.e(TAG, "Error acquiring wake lock", e);
        }
    }

    @Override
    public void onDestroy() {
        try {
            if (wakeLock != null && wakeLock.isHeld()) {
                wakeLock.release();
                Log.i(TAG, "Wake lock released");
            }
        } catch (Exception e) {
            Log.e(TAG, "Error releasing wake lock", e);
        } finally {
            super.onDestroy();
        }
    }
}
