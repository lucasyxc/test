import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ActivityIndicator, Alert, Platform, PermissionsAndroid, Linking } from 'react-native';
import LoginComponent from '../components/LoginComponent';
import WelcomeComponent from '../components/WelcomeComponent';
import { AuthService } from '../services/AuthService';

const MainScreen: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [organizationName, setOrganizationName] = useState('');
  const [organizationId, setOrganizationId] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const requestPermissions = async () => {
    if (Platform.OS === 'android') {
      try {
        if (Platform.Version >= 33) {
          const notificationGranted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
            {
              title: '通知权限',
              message: '需要通知权限以保持后台监听状态',
              buttonPositive: '确定',
              buttonNegative: '取消',
            }
          );
          if (notificationGranted !== PermissionsAndroid.RESULTS.GRANTED) {
            Alert.alert(
              '需要通知权限',
              '请在设置中授予通知权限以保持后台监听状态',
              [
                { text: '取消', style: 'cancel' },
                { text: '去设置', onPress: () => Linking.openSettings() }
              ]
            );
            return false;
          }
        }

        if (Platform.Version >= 30) {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.MANAGE_EXTERNAL_STORAGE,
            {
              title: '存储权限',
              message: '需要存储权限以监控下载文件夹',
              buttonPositive: '确定',
              buttonNegative: '取消',
            }
          );
          if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
            Alert.alert(
              '需要存储权限',
              '请在设置中授予存储权限以监控下载文件夹',
              [
                { text: '取消', style: 'cancel' },
                { text: '去设置', onPress: () => Linking.openSettings() }
              ]
            );
            return false;
          }
        } else {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
            {
              title: '存储权限',
              message: '需要存储权限以监控下载文件夹',
              buttonPositive: '确定',
              buttonNegative: '取消',
            }
          );
          if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
            Alert.alert(
              '需要存储权限',
              '请在设置中授予存储权限以监控下载文件夹',
              [
                { text: '取消', style: 'cancel' },
                { text: '去设置', onPress: () => Linking.openSettings() }
              ]
            );
            return false;
          }
        }
        return true;
      } catch (err) {
        console.error('Permission request error:', err);
        Alert.alert('错误', '请求权限时发生错误，请重试');
        return false;
      }
    }
    return true;
  };

  const attemptLogin = async (username: string, password: string) => {
    try {
      const response = await fetch('https://aiforoptometry.com/jtlogin/verif', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      const data = await response.json();
      if (data.success) {
        await AuthService.saveOrgData({
          id: data.organization_id,
          name: data.organization_name,
        });
        await handleLoginSuccess(data.organization_id, data.organization_name);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Auto-login failed:', error);
      return false;
    }
  };

  const checkAuth = async () => {
    try {
      const credentials = await AuthService.getCredentials();
      if (credentials) {
        const success = await attemptLogin(credentials.username, credentials.password);
        if (!success) {
          await AuthService.logout();
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = async (orgId: string, orgName: string): Promise<void> => {
    setOrganizationId(orgId);
    setOrganizationName(orgName);
    setIsLoggedIn(true);
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {!isLoggedIn ? (
        <LoginComponent onLoginSuccess={handleLoginSuccess} />
      ) : (
        <WelcomeComponent
          organizationName={organizationName}
          onLogout={async () => {
            await AuthService.logout();
            setIsLoggedIn(false);
            setOrganizationName('');
            setOrganizationId('');
          }}
          requestPermissions={requestPermissions}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
});

export default MainScreen;
