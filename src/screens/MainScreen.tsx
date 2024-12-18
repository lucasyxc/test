import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ActivityIndicator, Alert } from 'react-native';
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
          // Clear invalid credentials
          await AuthService.logout();
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = async (orgId: string, orgName: string) => {
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
