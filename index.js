/**
 * @format
 */

import {AppRegistry} from 'react-native';
import App from './App';
import {name as appName} from './app.json';
import PDFMonitorTask from './src/tasks/PDFMonitorTask';

AppRegistry.registerComponent(appName, () => App);
AppRegistry.registerHeadlessTask('PDFMonitorTask', () => PDFMonitorTask);
