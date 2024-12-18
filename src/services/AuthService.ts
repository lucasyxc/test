import AsyncStorage from '@react-native-async-storage/async-storage';

const AUTH_KEY = '@auth_credentials';
const ORG_KEY = '@org_data';

export interface AuthData {
  username: string;
  password: string;
}

export interface OrgData {
  id: string;
  name: string;
}

export const AuthService = {
  saveCredentials: async (data: AuthData) => {
    await AsyncStorage.setItem(AUTH_KEY, JSON.stringify(data));
  },

  getCredentials: async (): Promise<AuthData | null> => {
    const data = await AsyncStorage.getItem(AUTH_KEY);
    return data ? JSON.parse(data) : null;
  },

  saveOrgData: async (data: OrgData) => {
    await AsyncStorage.setItem(ORG_KEY, JSON.stringify(data));
  },

  getOrgData: async (): Promise<OrgData | null> => {
    const data = await AsyncStorage.getItem(ORG_KEY);
    return data ? JSON.parse(data) : null;
  },

  logout: async () => {
    await AsyncStorage.multiRemove([AUTH_KEY, ORG_KEY]);
  }
};
