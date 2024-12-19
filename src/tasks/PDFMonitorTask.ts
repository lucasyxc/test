import { NativeEventEmitter, NativeModules } from 'react-native';
import RNFS from 'react-native-fs';

const DOWNLOAD_PATH = '/storage/emulated/0/Download';
let lastCheckedFiles: string[] = [];

// Core monitoring function for foreground use
export const monitorPDFFiles = async () => {
  try {
    const files = await RNFS.readDir(DOWNLOAD_PATH);
    const currentPDFs = files
      .filter(file => file.name.toLowerCase().endsWith('.pdf'))
      .map(file => file.path);

    // Find new PDF files
    const newPDFs = currentPDFs.filter(pdf => !lastCheckedFiles.includes(pdf));

    // Update last checked files
    lastCheckedFiles = currentPDFs;

    // Notify for each new PDF
    for (const pdfPath of newPDFs) {
      NativeModules.PDFMonitorModule.notifyNewPDF(pdfPath);
    }

    return newPDFs.length > 0;
  } catch (error) {
    console.error('Error monitoring PDF files:', error);
    return false;
  }
};
