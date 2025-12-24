/** @type {import('next').NextConfig} */
import * as nextSafe from 'next-safe';

const isProd = process.env.NODE_ENV === 'production';
const serverUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const securityHeaders = nextSafe.default({
  isDev: !isProd,
  contentSecurityPolicy: {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      "'unsafe-eval'",
      "'unsafe-inline'",
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'",
      'https://fonts.googleapis.com',
    ],
    'font-src': [
      "'self'",
      'https://fonts.gstatic.com',
    ],
    'img-src': [
      "'self'",
      'data:',
      'blob:',
    ],
    'connect-src': [
      "'self'",
      serverUrl,
      'ws:',
      'wss:',
    ],
  },
  frameGuard: 'deny',
});

const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: isProd,
  },

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },

  images: {
    dangerouslyAllowSVG: true,
    contentDispositionType: 'inline',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.example.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },

  webpack: (config, options) => {
    config.module.rules.push({
      test: /\.(glsl|vs|fs|vert|frag)$/,
      use: ['raw-loader'],
    });

    return config;
  },
};

export default nextConfig;