import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth0, Auth0Provider } from '@auth0/auth0-react';

interface AuthContextType {
  user: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginWithRedirect: () => Promise<void>;
  logout: (options?: { returnTo?: string }) => void;
  getAccessTokenSilently: (options?: any) => Promise<string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const domain = import.meta.env.VITE_AUTH0_DOMAIN;
const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
const audience = import.meta.env.VITE_AUTH0_AUDIENCE;

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  if (!domain || !clientId) {
    throw new Error('Auth0域名和客户端ID必须配置');
  }

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: audience,
      }}
    >
      <AuthContextProvider>{children}</AuthContextProvider>
    </Auth0Provider>
  );
};

const AuthContextProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const auth0 = useAuth0();

  const value: AuthContextType = {
    user: auth0.user,
    isAuthenticated: auth0.isAuthenticated,
    isLoading: auth0.isLoading,
    loginWithRedirect: auth0.loginWithRedirect,
    logout: auth0.logout,
    getAccessTokenSilently: auth0.getAccessTokenSilently,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
