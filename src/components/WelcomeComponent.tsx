import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  PermissionsAndroid,
  Linking,
  Platform,
} from 'react-native';
import RNFS from 'react-native-fs';
import { monitorPDFFiles } from '../tasks/PDFMonitorTask';

interface WelcomeComponentProps {
  organizationName: string;
  onLogout: () => Promise<void>;
}

interface FSEvent {
  path: string;
  type: string;
}

const WelcomeComponent: React.FC<WelcomeComponentProps> = ({ organizationName, onLogout }) => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const DOWNLOAD_PATH = '/storage/emulated/0/Download';
  const monitorIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const requestStoragePermission = async () => {
    try {
      const androidVersion = typeof Platform.Version === 'string'
        ? parseInt(Platform.Version, 10)
        : Platform.Version;

      // Request notification permission for Android 13+
      if (androidVersion >= 33) {
        try {
          const notificationPermission = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
            {
              title: "通知权限",
              message: "需要通知权限以显示文件监控状态",
              buttonNeutral: "稍后询问",
              buttonNegative: "取消",
              buttonPositive: "确定"
            }
          );
          if (notificationPermission !== PermissionsAndroid.RESULTS.GRANTED) {
            console.warn('Notification permission denied');
          }
        } catch (error) {
          console.warn('Notification permission request failed:', error);
        }
      }

      // For Android 11+, request MANAGE_EXTERNAL_STORAGE
      if (androidVersion >= 30) {
        try {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.MANAGE_EXTERNAL_STORAGE,
            {
              title: "文件访问权限",
              message: "需要完整的存储访问权限以监控PDF文件",
              buttonNeutral: "稍后询问",
              buttonNegative: "取消",
              buttonPositive: "确定"
            }
          );

          if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
            Alert.alert(
              '需要权限',
              '请在设置中授予完整的存储访问权限以继续使用此功能',
              [
                { text: '取消', style: 'cancel' },
                {
                  text: '去设置',
                  onPress: async () => {
                    try {
                      await Linking.openSettings();
                    } catch (error) {
                      console.error('Error opening settings:', error);
                    }
                  }
                }
              ]
            );
            return false;
          }
          return true;
        } catch (error) {
          console.error('Storage permission request failed:', error);
          return false;
        }
      } else {
        // For Android < 11, request legacy storage permissions
        try {
          const results = await PermissionsAndroid.requestMultiple([
            PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
            PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE
          ]);

          const isGranted = Object.values(results).every(
            permission => permission === PermissionsAndroid.RESULTS.GRANTED
          );

          if (!isGranted) {
            Alert.alert(
              '需要权限',
              '请在设置中授予存储权限以继续使用此功能',
              [
                { text: '取消', style: 'cancel' },
                {
                  text: '去设置',
                  onPress: async () => {
                    try {
                      await Linking.openSettings();
                    } catch (error) {
                      console.error('Error opening settings:', error);
                    }
                  }
                }
              ]
            );
            return false;
          }
          return isGranted;
        } catch (error) {
          console.error('Legacy storage permission request failed:', error);
          return false;
        }
      }
    } catch (err) {
      console.error('Permission request error:', err);
      return false;
    }
  };

  const startMonitoring = async () => {
    try {
      const hasPermission = await requestStoragePermission();
      if (!hasPermission) {
        Alert.alert('错误', '需要存储权限才能监听文件夹');
        return;
      }

      const exists = await RNFS.exists(DOWNLOAD_PATH);
      if (!exists) {
        Alert.alert('错误', '下载目录不存在');
        return;
      }

      monitorIntervalRef.current = setInterval(async () => {
        try {
          const hasNewPDFs = await monitorPDFFiles();
          if (hasNewPDFs) {
            Alert.alert(
              '提示',
              '检测到新的PDF文件',
              [{ text: 'OK' }],
              { cancelable: true }
            );
          }
        } catch (error) {
          console.error('Error in monitoring interval:', error);
        }
      }, 5000);

      setIsMonitoring(true);
    } catch (error) {
      console.error('Error in startMonitoring:', error);
      Alert.alert('错误', '无法开始监听文件夹');
    }
  };

  useEffect(() => {
    return () => {
      if (monitorIntervalRef.current) {
        clearInterval(monitorIntervalRef.current);
        monitorIntervalRef.current = null;
      }
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.welcomeText}>
        欢迎登录：{organizationName}
      </Text>
      <TouchableOpacity
        style={[styles.startButton, isMonitoring && styles.monitoringButton]}
        onPress={startMonitoring}
        disabled={isMonitoring}
      >
        <Text style={styles.startButtonText}>
          {isMonitoring ? '监听中...' : '开始监听'}
        </Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <Text style={styles.logoutButtonText}>退出登录</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    width: '100%',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 30,
    color: '#333',
  },
  startButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
  },
  monitoringButton: {
    backgroundColor: '#666',
  },
  startButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});

export default WelcomeComponent;
