package com.rnmonitorapp;

import android.content.Intent;
import androidx.annotation.Nullable;

import com.facebook.react.HeadlessJsTaskService;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.jni.ReactNative;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.jni.HybridData;
import com.facebook.react.HeadlessJsTaskConfig;

import java.util.concurrent.TimeUnit;

public class PDFMonitorService extends HeadlessJsTaskService {
    private static final String TASK_NAME = "PDFMonitorTask";

    @Override
    protected @Nullable HeadlessJsTaskConfig getTaskConfig(Intent intent) {
        return new HeadlessJsTaskConfig(
            TASK_NAME,
            Arguments.createMap(),
            TimeUnit.DAYS.toMillis(1), // Keep running for 1 day
            true // Allow the task to run in foreground
        );
    }
}
