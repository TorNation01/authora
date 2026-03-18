/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      { source: '/finish-your-book', destination: '/write-your-book', permanent: true },
      { source: '/start', destination: '/write-your-book', permanent: true },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },
  async rewrites() {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      { source: '/health', destination: `${apiUrl}/health` },
      { source: '/health/ready', destination: `${apiUrl}/health/ready` },
      { source: '/api/:path*', destination: `${apiUrl}/api/:path*` },
    ];
  },
};

module.exports = nextConfig;
