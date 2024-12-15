package com.pdfmonitorapp;

import android.os.FileObserver;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFRow;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.util.Arrays;

public class FileMonitorModule extends ReactContextBaseJavaModule {
    private static final String TAG = "FileMonitorModule";
    private FileObserver fileObserver;
    private final ReactApplicationContext reactContext;

    public FileMonitorModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
    }

    @NonNull
    @Override
    public String getName() {
        return "FileMonitorModule";
    }

    private void sendEvent(String eventName, @Nullable WritableMap params) {
        reactContext
                .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
                .emit(eventName, params);
    }

    @ReactMethod
    public void startMonitoring(String folderPath, Promise promise) {
        try {
            if (fileObserver != null) {
                fileObserver.stopWatching();
            }

            fileObserver = new FileObserver(folderPath, FileObserver.CREATE) {
                @Override
                public void onEvent(int event, @Nullable String path) {
                    if (path != null && path.toLowerCase().endsWith(".pdf")) {
                        String fullPath = folderPath + "/" + path;
                        WritableMap params = Arguments.createMap();
                        params.putString("filePath", fullPath);
                        sendEvent("onPdfFileCreated", params);
                    }
                }
            };

            fileObserver.startWatching();
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("ERROR", "Failed to start monitoring: " + e.getMessage());
        }
    }

    @ReactMethod
    public void stopMonitoring(Promise promise) {
        try {
            if (fileObserver != null) {
                fileObserver.stopWatching();
                fileObserver = null;
            }
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("ERROR", "Failed to stop monitoring: " + e.getMessage());
        }
    }

    @ReactMethod
    public void convertPdfToExcel(String pdfPath, Promise promise) {
        try {
            File pdfFile = new File(pdfPath);
            String excelPath = pdfPath.substring(0, pdfPath.lastIndexOf(".")) + ".xlsx";

            PDDocument document = PDDocument.load(pdfFile);
            PDFTextStripper stripper = new PDFTextStripper();
            String text = stripper.getText(document);

            XSSFWorkbook workbook = new XSSFWorkbook();
            XSSFSheet sheet = workbook.createSheet("PDF Content");

            String[] lines = text.split("\n");
            for (int i = 0; i < lines.length; i++) {
                XSSFRow row = sheet.createRow(i);
                row.createCell(0).setCellValue(lines[i]);
            }

            FileOutputStream outputStream = new FileOutputStream(excelPath);
            workbook.write(outputStream);
            outputStream.close();
            workbook.close();
            document.close();

            promise.resolve(excelPath);
        } catch (Exception e) {
            promise.reject("ERROR", "Failed to convert PDF to Excel: " + e.getMessage());
        }
    }

    @ReactMethod
    public void convertPdfToJson(String pdfPath, Promise promise) {
        try {
            File pdfFile = new File(pdfPath);
            String jsonPath = pdfPath.substring(0, pdfPath.lastIndexOf(".")) + ".json";

            PDDocument document = PDDocument.load(pdfFile);
            PDFTextStripper stripper = new PDFTextStripper();
            String text = stripper.getText(document);

            JSONObject jsonObject = new JSONObject();
            jsonObject.put("content", text);
            jsonObject.put("pages", document.getNumberOfPages());
            jsonObject.put("filename", pdfFile.getName());


            FileWriter writer = new FileWriter(jsonPath);
            writer.write(jsonObject.toString(2));
            writer.close();
            document.close();

            promise.resolve(jsonPath);
        } catch (Exception e) {
            promise.reject("ERROR", "Failed to convert PDF to JSON: " + e.getMessage());
        }
    }
}
