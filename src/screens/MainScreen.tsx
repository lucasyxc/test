import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  PermissionsAndroid,
} from 'react-native';
import { NavigationProp } from '@react-navigation/native';

interface MainScreenProps {
  navigation: NavigationProp<any>;
}

export const MainScreen: React.FC<MainScreenProps> = () => {
  const [selectedPath, setSelectedPath] = useState<string>('');
  const [isMonitoring, setIsMonitoring] = useState(false);

  const requestStoragePermission = async () => {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        {
          title: 'Storage Permission',
          message: 'App needs access to your storage to monitor PDF files.',
          buttonNeutral: 'Ask Me Later',
          buttonNegative: 'Cancel',
          buttonPositive: 'OK',
        },
      );
      return granted === PermissionsAndroid.RESULTS.GRANTED;
    } catch (err) {
      console.warn(err);
      return false;
    }
  };

  const handleSelectFolder = async () => {
    const hasPermission = await requestStoragePermission();
    if (!hasPermission) {
      Alert.alert('Permission Denied', 'Storage permission is required to monitor folders.');
      return;
    }
    // TODO: Implement folder selection using a native module
    // For now, we'll use a mock path
    setSelectedPath('/storage/emulated/0/Documents');
  };

  const handleStartMonitoring = () => {
    if (!selectedPath) {
      Alert.alert('Error', 'Please select a folder first');
      return;
    }
    setIsMonitoring(true);
    // TODO: Implement actual folder monitoring logic
    Alert.alert('Success', `Started monitoring folder: ${selectedPath}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>PDF Monitor</Text>
      <View style={styles.pathContainer}>
        <Text style={styles.pathLabel}>Selected Folder:</Text>
        <Text style={styles.pathText}>{selectedPath || 'No folder selected'}</Text>
      </View>
      <TouchableOpacity
        style={styles.button}
        onPress={handleSelectFolder}
        disabled={isMonitoring}
      >
        <Text style={styles.buttonText}>Select Folder</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.button, isMonitoring && styles.buttonDisabled]}
        onPress={handleStartMonitoring}
        disabled={isMonitoring || !selectedPath}
      >
        <Text style={styles.buttonText}>
          {isMonitoring ? 'Monitoring...' : 'Start Monitoring'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  pathContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  pathLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  pathText: {
    fontSize: 14,
    color: '#666',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
