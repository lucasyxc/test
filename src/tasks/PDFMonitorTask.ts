import { NativeEventEmitter, NativeModules } from 'react-native';
import RNFS from 'react-native-fs';

const DOWNLOAD_PATH = '/storage/emulated/0/Download';
let lastCheckedFiles: string[] = [];

const checkForNewPDFs = async () => {
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
  } catch (error) {
    console.error('Error monitoring PDF files:', error);
  }
};

// Register the headless task
const PDFMonitorTask = async () => {
  // Run initial check
  await checkForNewPDFs();

  // Set up periodic checking
  setInterval(checkForNewPDFs, 5000); // Check every 5 seconds

  // Return a promise that never resolves to keep the service running
  return new Promise(() => {});
};

export default PDFMonitorTask;
