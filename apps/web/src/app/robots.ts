import { MetadataRoute } from 'next';

// Marketing site canonical base
const baseUrl = process.env.NEXT_PUBLIC_MARKETING_URL || process.env.NEXT_PUBLIC_WEB_URL || 'https://authora.studio';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/dashboard/', '/login', '/register', '/setup', '/onboarding'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
