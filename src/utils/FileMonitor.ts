import { NativeEventEmitter, NativeModules, PermissionsAndroid } from 'react-native';

const { FileMonitorModule } = NativeModules;

class FileMonitor {
  private static instance: FileMonitor;
  private eventEmitter: NativeEventEmitter;
  private monitoringPath: string | null = null;
  private listeners: Set<(filePath: string) => void> = new Set();

  private constructor() {
    this.eventEmitter = new NativeEventEmitter(FileMonitorModule);
    this.eventEmitter.addListener('onPdfFileCreated', this.handlePdfCreated);
  }

  public static getInstance(): FileMonitor {
    if (!FileMonitor.instance) {
      FileMonitor.instance = new FileMonitor();
    }
    return FileMonitor.instance;
  }

  private handlePdfCreated = async (filePath: string) => {
    try {
      // Convert PDF to Excel
      await FileMonitorModule.convertPdfToExcel(filePath);

      // Convert PDF to JSON
      await FileMonitorModule.convertPdfToJson(filePath);

      // Notify all listeners
      this.listeners.forEach(listener => listener(filePath));
    } catch (error) {
      console.error('Error processing PDF file:', error);
    }
  };

  public async startMonitoring(folderPath: string): Promise<boolean> {
    try {
      const hasPermission = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE
      );

      if (!hasPermission) {
        throw new Error('Storage permission not granted');
      }

      await FileMonitorModule.startMonitoring(folderPath);
      this.monitoringPath = folderPath;
      return true;
    } catch (error) {
      console.error('Error starting monitoring:', error);
      return false;
    }
  }

  public stopMonitoring(): void {
    if (this.monitoringPath) {
      FileMonitorModule.stopMonitoring();
      this.monitoringPath = null;
    }
  }

  public addListener(callback: (filePath: string) => void): () => void {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }
}

export default FileMonitor.getInstance();
