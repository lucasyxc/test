package com.rnmonitorapp;

import android.content.Intent;
import android.os.Bundle;
import androidx.annotation.Nullable;

import com.facebook.react.HeadlessJsTaskService;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.jstasks.HeadlessJsTaskConfig;

import java.util.concurrent.TimeUnit;

public class PDFMonitorService extends HeadlessJsTaskService {
    private static final String TASK_NAME = "PDFMonitorTask";
    private static final long TIMEOUT = TimeUnit.DAYS.toMillis(1); // 1 day timeout

    @Override
    protected @Nullable HeadlessJsTaskConfig getTaskConfig(Intent intent) {
        Bundle extras = intent.getExtras();
        WritableMap data = extras != null ? Arguments.fromBundle(extras) : Arguments.createMap();

        return new HeadlessJsTaskConfig(
            TASK_NAME,
            data,
            TIMEOUT,
            true // Allow the task to run in foreground
        );
    }
}
