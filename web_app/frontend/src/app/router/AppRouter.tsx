import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { useBootstrap } from '@/app/bootstrap/useBootstrap';
import { useTelegramWebAppRuntime } from '@/app/bootstrap/useTelegramWebAppRuntime';
import { useSessionStore } from '@/entities/session/sessionStore';
import { AboutPage } from '@/pages/about/AboutPage';
import { ModelDetailsPage } from '@/pages/model-details/ModelDetailsPage';
import { ModelsPage } from '@/pages/models/ModelsPage';
import { ProfilePage } from '@/pages/profile/ProfilePage';
import { SupportPage } from '@/pages/support/SupportPage';
import { SystemPage } from '@/pages/system/SystemPage';
import { env } from '@/shared/config/env';
import { normalizeTelegramHref } from '@/shared/lib/telegram';
import { AppShell } from '@/widgets/app-shell/AppShell';
import { OnboardingModal } from '@/features/onboarding';
import systemPageContentRaw from '@/pages/system/systemPageContent.yaml?raw';

const systemPageContent = JSON.parse(systemPageContentRaw) as {
  loadingTitle: string;
  loadingMessage: string;
  browserTitle: string;
  browserMessage: string;
  browserActionLabel: string;
  telegramErrorTitle: string;
  telegramErrorMessage: string;
  errorTitle: string;
  errorRetryLabel: string;
  errorFallbackMessage: string;
  notFoundTitle: string;
  notFoundMessage: string;
};

function AppContent() {
  useTelegramWebAppRuntime();
  useBootstrap();
  const status = useSessionStore((state) => state.status);
  const error = useSessionStore((state) => state.error);
  const bootstrap = useSessionStore((state) => state.bootstrap);
  const mainBotUrl = normalizeTelegramHref(env.mainBotUrl);

  if (status === 'idle' || status === 'loading') {
    return (
      <SystemPage
        title={systemPageContent.loadingTitle}
        message={systemPageContent.loadingMessage}
      />
    );
  }

  if (status === 'error') {
    if (error === 'WEB_APP_BROWSER_ONLY') {
      return (
        <SystemPage
          title={systemPageContent.browserTitle}
          message={systemPageContent.browserMessage}
          actionLabel={systemPageContent.browserActionLabel}
          actionHref={mainBotUrl}
          launchPrompt
        />
      );
    }

    if (error === 'WEB_APP_TELEGRAM_INITDATA_MISSING') {
      return (
        <SystemPage
          title={systemPageContent.browserTitle}
          actionLabel={systemPageContent.browserActionLabel}
          actionHref={mainBotUrl}
          launchPrompt
        />
      );
    }

    return (
      <SystemPage
        title={systemPageContent.errorTitle}
        message={error || systemPageContent.errorFallbackMessage}
        actionLabel={systemPageContent.errorRetryLabel}
        onAction={() => {
          void bootstrap();
        }}
      />
    );
  }

  return (
    <AppShell>
      <OnboardingModal />
      <Routes>
        <Route path="/" element={<Navigate to="/models" replace />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route path="/models/:code" element={<ModelDetailsPage />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route
          path="*"
          element={<SystemPage title={systemPageContent.notFoundTitle} message={systemPageContent.notFoundMessage} />}
        />
      </Routes>
    </AppShell>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
