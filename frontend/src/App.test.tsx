import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock Auth0
vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    isLoading: false,
    isAuthenticated: false,
    user: null,
    loginWithRedirect: vi.fn(),
    logout: vi.fn(),
  }),
  Auth0Provider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(document.body).toBeInTheDocument();
  });
});
