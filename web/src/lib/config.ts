declare global {
  interface Window {
    __APP_CONFIG__?: {
      appName?: string;
      webDomain?: string;
      botUsername?: string;
      botUrl?: string;
      supportBotUrl?: string;
      webAppUrl?: string;
      contactEmail?: string;
    };
  }
}

export const site = {
  get name(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.appName) ||
      process.env.NEXT_PUBLIC_APP_NAME ||
      'ELEGANT AGENCY'
    );
  },

  get domain(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.webDomain) ||
      process.env.NEXT_PUBLIC_WEB_DOMAIN ||
      'localhost'
    );
  },

  get botUsername(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.botUsername) ||
      process.env.NEXT_PUBLIC_BOT_USERNAME ||
      '@ElegantAgencyApp'
    );
  },

  get botUrl(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.botUrl) ||
      process.env.NEXT_PUBLIC_BOT_URL ||
      'https://t.me/ElegantAgencyApp'
    );
  },

  get supportBotUrl(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.supportBotUrl) ||
      process.env.NEXT_PUBLIC_SUPPORT_BOT_URL ||
      'https://t.me/ElegantAgencySupportApp'
    );
  },

  get webAppUrl(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.webAppUrl) ||
      process.env.NEXT_PUBLIC_WEB_APP_URL ||
      'https://app.elegant-agency.fun'
    );
  },

  get contactEmail(): string {
    return (
      (typeof window !== 'undefined' && window.__APP_CONFIG__?.contactEmail) ||
      process.env.NEXT_PUBLIC_CONTACT_EMAIL ||
      ''
    );
  },

  copyrightYear: 2026,

  assets: {
    campaign: '/campaign-1536.webp',
    webp: '/campaign-768.webp 768w, /campaign-1536.webp 1536w',
    avif: '/campaign-768.avif 768w, /campaign-1536.avif 1536w',
  },
};

export const muses = [
  {
    id: '01',
    title: 'Грация',
    note: 'Тихая уверенность. Безупречное присутствие.',
    index: 0,
    chapter: 'Самообладание без лишних усилий.',
  },
  {
    id: '02',
    title: 'Обаяние',
    note: 'Теплота, интеллект и собственный притягательный мир.',
    index: 1,
    chapter: 'Пространство преображается.',
  },
  {
    id: '03',
    title: 'Интрига',
    note: 'Вдумчивый взгляд. Беседа, стоящая каждого мгновения.',
    index: 2,
    chapter: 'Всегда есть что открыть.',
  },
] as const;

export type Muse = typeof muses[number];

export type Overlay =
  | { type: 'menu' }
  | { type: 'enquiry'; muse?: string }
  | { type: 'muse'; index: number }
  | { type: 'privacy' }
  | { type: 'legal' }
  | null;
