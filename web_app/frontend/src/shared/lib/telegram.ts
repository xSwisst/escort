type TelegramInset = {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
};

type TelegramEventName =
  | 'fullscreenChanged'
  | 'fullscreenFailed'
  | 'safeAreaChanged'
  | 'contentSafeAreaChanged';

export function normalizeTelegramHref(rawValue: string) {
  const value = rawValue.trim();

  if (!value) {
    return '';
  }

  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  const normalizedValue = value
    .replace(/^@/, '')
    .replace(/^t\.me\//i, '')
    .replace(/^telegram\.me\//i, '');

  return normalizedValue ? `https://t.me/${normalizedValue}` : '';
}

type TelegramWebApp = {
  version?: string;
  isFullscreen?: boolean;
  isClosingConfirmationEnabled?: boolean;
  initData?: string;
  initDataUnsafe?: Record<string, unknown>;
  ready?: () => void;
  expand?: () => void;
  disableVerticalSwipes?: () => void;
  enableClosingConfirmation?: () => void;
  requestFullscreen?: () => Promise<void> | void;
  isVersionAtLeast?: (version: string) => boolean;
  onEvent?: (eventType: TelegramEventName, eventHandler: () => void) => void;
  offEvent?: (eventType: TelegramEventName, eventHandler: () => void) => void;
  safeAreaInset?: TelegramInset;
  contentSafeAreaInset?: TelegramInset;
  BackButton?: {
    isVisible?: boolean;
    show?: () => void;
    hide?: () => void;
    onClick?: (callback: () => void) => void;
    offClick?: (callback: () => void) => void;
  };
};

type TelegramGlobal = {
  WebApp?: TelegramWebApp;
};

function getTelegramLaunchParams() {
  if (typeof window === 'undefined') {
    return new URLSearchParams();
  }

  const searchParams = new URLSearchParams(window.location.search);
  if (searchParams.has('tgWebAppData') || searchParams.has('tgWebAppPlatform')) {
    return searchParams;
  }

  const hash = window.location.hash.replace(/^#/, '');
  return new URLSearchParams(hash);
}

function getTelegramGlobal(): TelegramGlobal | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return (window as Window & { Telegram?: TelegramGlobal }).Telegram ?? null;
}

export function getTelegramWebApp(): TelegramWebApp | null {
  return getTelegramGlobal()?.WebApp ?? null;
}

export function getTelegramInitData(): string {
  const runtimeValue = String(getTelegramWebApp()?.initData ?? '').trim();
  if (runtimeValue) {
    return runtimeValue;
  }

  return String(getTelegramLaunchParams().get('tgWebAppData') ?? '').trim();
}

export function isTelegramWebAppAvailable() {
  return Boolean(getTelegramInitData());
}

export function hasTelegramLaunchContext() {
  const launchParams = getTelegramLaunchParams();
  return Boolean(getTelegramWebApp() || launchParams.get('tgWebAppPlatform') || launchParams.get('tgWebAppData'));
}

export async function waitForTelegramInitData(timeoutMs = 1500, intervalMs = 50): Promise<string> {
  const deadline = Date.now() + timeoutMs;

  while (Date.now() <= deadline) {
    const initData = getTelegramInitData();
    if (initData) {
      return initData;
    }

    await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
  }

  return '';
}

function getInsetValue(value: number | undefined, fallback = 0) {
  return Number.isFinite(value) ? Math.max(0, Number(value)) : fallback;
}

function compareTelegramVersion(currentVersion: string, requiredVersion: string) {
  const current = currentVersion.split('.').map((part) => Number.parseInt(part, 10) || 0);
  const required = requiredVersion.split('.').map((part) => Number.parseInt(part, 10) || 0);
  const maxLength = Math.max(current.length, required.length);

  for (let index = 0; index < maxLength; index += 1) {
    const currentPart = current[index] ?? 0;
    const requiredPart = required[index] ?? 0;

    if (currentPart === requiredPart) {
      continue;
    }

    return currentPart > requiredPart;
  }

  return true;
}

function isTelegramVersionAtLeast(webApp: TelegramWebApp, requiredVersion: string) {
  if (webApp.isVersionAtLeast) {
    return webApp.isVersionAtLeast(requiredVersion);
  }

  const currentVersion = String(webApp.version ?? '').trim();
  if (!currentVersion) {
    return false;
  }

  return compareTelegramVersion(currentVersion, requiredVersion);
}

function applyTelegramSafeArea() {
  if (typeof document === 'undefined') {
    return;
  }

  const webApp = getTelegramWebApp();
  const root = document.documentElement;
  const safeAreaInset = webApp?.safeAreaInset ?? {};
  const contentSafeAreaInset = webApp?.contentSafeAreaInset ?? safeAreaInset;

  const safeTop = getInsetValue(safeAreaInset.top);
  const safeBottom = getInsetValue(safeAreaInset.bottom);
  const safeLeft = getInsetValue(safeAreaInset.left);
  const safeRight = getInsetValue(safeAreaInset.right);

  root.style.setProperty('--tg-safe-top', `${safeTop}px`);
  root.style.setProperty('--tg-safe-bottom', `${safeBottom}px`);
  root.style.setProperty('--tg-safe-left', `${safeLeft}px`);
  root.style.setProperty('--tg-safe-right', `${safeRight}px`);
  root.style.setProperty('--tg-content-safe-top', `${getInsetValue(contentSafeAreaInset.top, safeTop)}px`);
  root.style.setProperty('--tg-content-safe-bottom', `${getInsetValue(contentSafeAreaInset.bottom, safeBottom)}px`);
  root.style.setProperty('--tg-content-safe-left', `${getInsetValue(contentSafeAreaInset.left, safeLeft)}px`);
  root.style.setProperty('--tg-content-safe-right', `${getInsetValue(contentSafeAreaInset.right, safeRight)}px`);
  root.dataset.tgFullscreen = webApp?.isFullscreen ? 'true' : 'false';
}

function isTelegramMobilePlatform(): boolean {
  if (typeof window === 'undefined') return false;
  const platform = String(
    (window as Window & { Telegram?: { WebApp?: { platform?: string } } }).Telegram?.WebApp?.platform ?? '',
  ).toLowerCase();
  return platform === 'ios' || platform === 'android' || platform === 'android_x' || platform === 'ios_x';
}

function requestTelegramFullscreen(webApp: TelegramWebApp) {
  if (!isTelegramMobilePlatform()) {
    return;
  }

  if (!isTelegramVersionAtLeast(webApp, '8.0')) {
    return;
  }

  try {
    const result = webApp.requestFullscreen?.();
    if (result && typeof (result as Promise<void>).catch === 'function') {
      void (result as Promise<void>).catch(() => undefined);
    }
  } catch {
    return;
  }
}

export function initTelegramWebApp() {
  const webApp = getTelegramWebApp();
  if (!webApp) {
    applyTelegramSafeArea();
    return () => undefined;
  }

  const handleFullscreenChange = () => {
    applyTelegramSafeArea();
  };

  const handleSafeAreaChange = () => {
    applyTelegramSafeArea();
  };

  webApp?.ready?.();
  webApp?.expand?.();
  webApp?.disableVerticalSwipes?.();
  webApp?.enableClosingConfirmation?.();
  applyTelegramSafeArea();
  requestTelegramFullscreen(webApp);

  webApp.onEvent?.('fullscreenChanged', handleFullscreenChange);
  webApp.onEvent?.('fullscreenFailed', handleFullscreenChange);
  webApp.onEvent?.('safeAreaChanged', handleSafeAreaChange);
  webApp.onEvent?.('contentSafeAreaChanged', handleSafeAreaChange);

  return () => {
    webApp.offEvent?.('fullscreenChanged', handleFullscreenChange);
    webApp.offEvent?.('fullscreenFailed', handleFullscreenChange);
    webApp.offEvent?.('safeAreaChanged', handleSafeAreaChange);
    webApp.offEvent?.('contentSafeAreaChanged', handleSafeAreaChange);
  };
}

export function bindTelegramBackButton(isVisible: boolean, onClick: () => void) {
  const backButton = getTelegramWebApp()?.BackButton;
  if (!backButton) {
    return () => undefined;
  }

  backButton.offClick?.(onClick);

  if (!isVisible) {
    backButton.hide?.();
    return () => undefined;
  }

  backButton.show?.();
  backButton.onClick?.(onClick);

  return () => {
    backButton.offClick?.(onClick);
    backButton.hide?.();
  };
}

export function extractTelegramHandle(rawValue: string, fallbackValue: string) {
  const value = rawValue.trim();

  if (!value) {
    return fallbackValue;
  }

  if (value.startsWith('@')) {
    return value;
  }

  const match = value.match(/(?:t\.me|telegram\.me)\/([^/?#]+)/i);
  const handle = match?.[1] ?? value.replace(/^https?:\/\//i, '').split('/').filter(Boolean).at(-1);

  return handle ? `@${handle.replace(/^@/, '')}` : fallbackValue;
}
