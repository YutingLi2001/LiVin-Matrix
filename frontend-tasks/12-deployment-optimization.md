# Frontend Task 12: Deployment and Optimization

## Objective
Prepare the frontend application for production deployment with comprehensive optimization, build configuration, and GitHub Pages deployment setup.

## Description
Implement production-ready build processes, performance optimizations, and deployment workflows to ensure fast loading times, efficient resource usage, and reliable deployment to GitHub Pages.

## Requirements

### 1. Build Optimization

#### Webpack/Vite Configuration
```javascript
// vite.config.ts or webpack.config.js
export default {
  build: {
    target: 'es2018',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // Disable in production
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'd3'],
          ui: ['@radix-ui/react-dialog', 'framer-motion']
        }
      }
    }
  }
};
```

#### Bundle Splitting Strategy
- **Main bundle:** Core app logic and routing
- **Vendor bundle:** React, React DOM, core dependencies
- **Charts bundle:** Recharts, D3, visualization libraries
- **UI bundle:** Animation libraries, UI components
- **Async chunks:** Route-based code splitting

#### Asset Optimization
- Image compression and next-gen formats (WebP, AVIF)
- Font subsetting for custom fonts
- CSS purging for unused styles
- JavaScript minification and tree shaking
- Service worker for caching strategy

### 2. Performance Optimizations

#### Core Web Vitals Targets
- **Largest Contentful Paint (LCP):** < 2.5s
- **First Input Delay (FID):** < 100ms
- **Cumulative Layout Shift (CLS):** < 0.1
- **First Contentful Paint (FCP):** < 1.8s
- **Time to Interactive (TTI):** < 3.5s

#### Loading Performance
```typescript
// Lazy loading configuration
const MatrixAnalysisPage = lazy(() => import('./pages/MatrixAnalysisPage'));
const DataEntryPage = lazy(() => import('./pages/DataEntryPage'));

// Preload critical resources
const preloadCriticalResources = () => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = '/fonts/JetBrainsMono-Regular.woff2';
  link.as = 'font';
  link.type = 'font/woff2';
  link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
};
```

#### Runtime Performance
- React.memo for expensive components
- useMemo for complex calculations
- useCallback for event handlers
- Virtual scrolling for large lists
- Debounced search and filtering

### 3. GitHub Pages Deployment

#### GitHub Actions Workflow
```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test:ci

      - name: Build application
        run: npm run build
        env:
          PUBLIC_URL: /LiVin-Matrix

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

#### Build Configuration for GitHub Pages
```json
// package.json
{
  "homepage": "https://username.github.io/LiVin-Matrix",
  "scripts": {
    "build:gh-pages": "PUBLIC_URL=/LiVin-Matrix npm run build",
    "deploy": "npm run build:gh-pages && gh-pages -d dist"
  }
}
```

### 4. Caching Strategy

#### Service Worker Implementation
```typescript
// service-worker.ts
const CACHE_NAME = 'livin-matrix-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/fonts/JetBrainsMono-Regular.woff2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});
```

#### HTTP Caching Headers
```nginx
# For static assets
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

# For HTML files
location ~* \.html$ {
  expires 0;
  add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

### 5. SEO and Meta Tags

#### HTML Meta Configuration
```html
<!-- index.html -->
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#8b5cf6" />
  <meta name="description" content="LiVin Matrix - Personal life analytics with cyberpunk visualization" />
  
  <!-- OpenGraph tags -->
  <meta property="og:title" content="LiVin Matrix" />
  <meta property="og:description" content="Analyze correlations in your life data" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://username.github.io/LiVin-Matrix" />
  
  <!-- Preload critical resources -->
  <link rel="preload" href="/fonts/JetBrainsMono-Regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/css/critical.css" as="style" />
</head>
```

#### Robots.txt and Sitemap
```txt
# robots.txt
User-agent: *
Allow: /
Sitemap: https://username.github.io/LiVin-Matrix/sitemap.xml
```

### 6. Error Handling and Monitoring

#### Error Boundaries
```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Application error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <CyberpunkErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

#### Production Logging
```typescript
const logger = {
  error: (message: string, extra?: any) => {
    if (process.env.NODE_ENV === 'production') {
      // Send to monitoring service
      console.error(`[ERROR] ${message}`, extra);
    }
  },
  performance: (metric: string, value: number) => {
    if (process.env.NODE_ENV === 'production') {
      // Send performance metrics
      console.log(`[PERF] ${metric}: ${value}ms`);
    }
  }
};
```

### 7. Security Configuration

#### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.github.com;
">
```

#### Environment Variables
```typescript
// Environment configuration
const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'https://api.example.com',
  environment: process.env.NODE_ENV,
  version: process.env.REACT_APP_VERSION || '1.0.0',
  githubPages: process.env.REACT_APP_GITHUB_PAGES === 'true'
};
```

### 8. Progressive Web App (PWA) Features

#### Web App Manifest
```json
{
  "name": "LiVin Matrix",
  "short_name": "LiVin Matrix",
  "description": "Personal life analytics with cyberpunk visualization",
  "theme_color": "#8b5cf6",
  "background_color": "#000000",
  "display": "standalone",
  "start_url": "/",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 9. Monitoring and Analytics

#### Performance Monitoring
```typescript
// Web Vitals reporting
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

const sendToAnalytics = (metric) => {
  // Send to analytics service
  console.log(metric);
};

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

#### Basic Analytics Setup
```typescript
// Simple page view tracking
const trackPageView = (path: string) => {
  if (process.env.NODE_ENV === 'production') {
    // Send page view to analytics
    console.log(`Page view: ${path}`);
  }
};
```

## Acceptance Criteria
- [ ] Production build optimized for performance
- [ ] Bundle size under target limits (main bundle < 250KB gzipped)
- [ ] Core Web Vitals meet target thresholds
- [ ] GitHub Pages deployment workflow functional
- [ ] Service worker caching implemented
- [ ] Error boundaries handle crashes gracefully
- [ ] SEO meta tags properly configured
- [ ] Progressive Web App features working
- [ ] Security headers configured
- [ ] Performance monitoring in place

## Technical Notes
- Use Lighthouse CI for automated performance testing
- Implement proper cache busting for assets
- Ensure proper HTTPS configuration
- Test deployment process in staging environment
- Monitor bundle size changes in CI/CD

## Files to Create
- `vite.config.ts` or `webpack.config.js`
- `.github/workflows/deploy.yml`
- `public/manifest.json`
- `public/robots.txt`
- `src/service-worker.ts`
- `src/utils/analytics.ts`
- `src/components/ErrorBoundary.tsx`

## Dependencies
- Workbox (for service worker)
- web-vitals (for performance monitoring)
- @vitejs/plugin-pwa (for PWA features)
- gh-pages (for deployment)

## Performance Budget
- Main bundle: < 250KB gzipped
- Total initial load: < 500KB gzipped
- Time to Interactive: < 3.5 seconds
- First Contentful Paint: < 1.8 seconds

## Testing
- Lighthouse audits on production build
- Performance regression testing
- Cross-browser deployment testing
- Mobile performance testing

## Maintenance
- Regular dependency updates
- Performance monitoring review
- Bundle size monitoring
- Security audit reviews

## Estimated Time: 16-20 hours

## Priority: High
Essential for production deployment and user experience.