declare global {
  interface Window {
    __APP_CONFIG__?: {
      bot_username?: string;
      web_domain?: string;
    };
  }
}

export const getBotUsername = (): string => {
  if (typeof window !== 'undefined' && window.__APP_CONFIG__?.bot_username) {
    return window.__APP_CONFIG__.bot_username.replace(/^@/, '');
  }
  const envBot = (import.meta as any).env?.VITE_BOT_USERNAME;
  if (envBot) {
    return envBot.replace(/^@/, '');
  }
  return 'escort_main_bot';
};

export const getTelegramBotUrl = (modelCode?: string): string => {
  const username = getBotUsername();
  const baseUrl = `https://t.me/${username}`;
  if (modelCode) {
    return `${baseUrl}?start=${encodeURIComponent(modelCode)}`;
  }
  return baseUrl;
};
