import { TgsPlayer } from '@/features/onboarding/TgsPlayer';

type SystemPageProps = {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  actionHref?: string;
  loading?: boolean;
  launchPrompt?: boolean;
};

export function SystemPage({ title, message, actionLabel, onAction, actionHref, loading = false, launchPrompt = false }: SystemPageProps) {
  if (loading) {
    return (
      <div className="app-loading-screen app-safe-screen" aria-label="Загрузка" aria-busy="true">
        <div className="app-loading-spinner" aria-hidden="true" />
      </div>
    );
  }

  return (
    <div className={`system-page${launchPrompt ? ' system-page--launch' : ''}`}>
      <div className="system-page__card">
        {launchPrompt ? <TgsPlayer url="/assets/open-telegram.tgs" className="system-page__animation" size={190} /> : <p className="system-page__eyebrow">VELVET ALLURE</p>}
        <h1 className="system-page__title">{title}</h1>
        {message ? <p className="system-page__message">{message}</p> : null}
        {actionHref && actionLabel ? (
          <a href={actionHref} className="system-page__btn" id="system-page-action-link">
            {actionLabel}
          </a>
        ) : null}
        {onAction && actionLabel && !actionHref ? (
          <button
            id="system-page-action-btn"
            type="button"
            className="system-page__btn"
            onClick={onAction}
          >
            {actionLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}
