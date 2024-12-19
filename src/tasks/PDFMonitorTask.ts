import { NativeEventEmitter, NativeModules, PermissionsAndroid, Platform } from 'react-native';
import RNFS from 'react-native-fs';

const DOWNLOAD_PATH = '/storage/emulated/0/Download';
let lastCheckedFiles: string[] = [];

const checkStoragePermission = async () => {
  const androidVersion = typeof Platform.Version === 'string'
    ? parseInt(Platform.Version, 10)
    : Platform.Version;

  if (androidVersion >= 30) {
    return await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.MANAGE_EXTERNAL_STORAGE);
  } else {
    const readPermission = await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE);
    const writePermission = await PermissionsAndroid.check(PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE);
    return readPermission && writePermission;
  }
};

export const monitorPDFFiles = async () => {
  try {
    const hasPermission = await checkStoragePermission();
    if (!hasPermission) {
      console.error('Storage permission not granted');
      return false;
    }

    const files = await RNFS.readDir(DOWNLOAD_PATH);
    const currentPDFs = files
      .filter(file => file.name.toLowerCase().endsWith('.pdf'))
      .map(file => file.path);

    const newPDFs = currentPDFs.filter(pdf => !lastCheckedFiles.includes(pdf));
    lastCheckedFiles = currentPDFs;

    for (const pdfPath of newPDFs) {
      NativeModules.PDFMonitorModule.notifyNewPDF(pdfPath);
    }

    return newPDFs.length > 0;
  } catch (error) {
    console.error('Error monitoring PDF files:', error);
    return false;
  }
};
