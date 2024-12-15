[app]
title = PDF处理器
package.name = pdfprocessor
package.domain = com.yourcompany
source.dir = .
source.include_exts = py,png,jpg,ttf,ttc
source.include_patterns = assets/*
version = 1.0

requirements = python3,kivy==2.2.1,pdfplumber==0.10.3,pandas==1.0.1,watchdog==3.0.0,plyer==2.1.0,android

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE,POST_NOTIFICATIONS
android.api = 31
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a

[buildozer]
log_level = 2
