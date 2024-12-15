from kivy.utils import platform
from jnius import autoclass
import time
import os
import signal
import sys

# Android specific imports
if platform == 'android':
    Service = autoclass('org.kivy.android.PythonService').mService
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    NotificationManager = autoclass('android.app.NotificationManager')
    Builder = autoclass('android.app.Notification$Builder')
    R = autoclass('org.kivy.android.R')

class PDFMonitorService:
    def __init__(self):
        self.service = None
        self.notification_manager = None
        self.CHANNEL_ID = "pdf_monitor_channel"
        self.NOTIFICATION_ID = 1
        self.running = True

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, signum, frame):
        """Handle termination signals"""
        self.running = False
        if platform == 'android' and self.service:
            self.service.stopForeground(True)
        sys.exit(0)

    def create_notification_channel(self):
        """Create notification channel for Android 8.0+"""
        try:
            channel = NotificationChannel(
                self.CHANNEL_ID,
                "PDF Monitor Service",
                NotificationManager.IMPORTANCE_LOW
            )
            channel.setDescription("PDF监控服务通知")
            self.notification_manager.createNotificationChannel(channel)
        except Exception as e:
            print(f"Error creating notification channel: {e}")

    def create_foreground_notification(self):
        """Create a foreground notification for the service"""
        try:
            # Create notification channel for Android 8.0+
            if not self.notification_manager:
                self.notification_manager = self.service.getSystemService(
                    Context.NOTIFICATION_SERVICE
                )
                self.create_notification_channel()

            # Create pending intent for notification
            context = self.service.getApplicationContext()
            intent = Intent(context, context.getClass())
            intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
            pending_intent = PendingIntent.getActivity(
                context, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )

            # Build notification
            notification = Builder(context, self.CHANNEL_ID)\
                .setContentTitle("PDF监控服务")\
                .setContentText("正在监控PDF文件变化...")\
                .setSmallIcon(R.drawable.icon)\
                .setContentIntent(pending_intent)\
                .setOngoing(True)\
                .build()

            return notification
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None

    def start(self):
        """Start the service"""
        try:
            if platform == 'android':
                self.service = Service
                notification = self.create_foreground_notification()
                if notification:
                    self.service.startForeground(self.NOTIFICATION_ID, notification)

            while self.running:
                # Main service loop
                time.sleep(1)
        except Exception as e:
            print(f"Service error: {e}")
        finally:
            if platform == 'android' and self.service:
                try:
                    self.service.stopForeground(True)
                except:
                    pass

if __name__ == '__main__':
    service = PDFMonitorService()
    service.start()
