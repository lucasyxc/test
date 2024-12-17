import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import LoginComponent from '../components/LoginComponent';
import WelcomeComponent from '../components/WelcomeComponent';

const MainScreen: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [organizationName, setOrganizationName] = useState('');
  const [organizationId, setOrganizationId] = useState('');

  const handleLoginSuccess = (orgId: string, orgName: string) => {
    setOrganizationId(orgId);
    setOrganizationName(orgName);
    setIsLoggedIn(true);
  };

  return (
    <View style={styles.container}>
      {!isLoggedIn ? (
        <LoginComponent onLoginSuccess={handleLoginSuccess} />
      ) : (
        <WelcomeComponent organizationName={organizationName} />
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
