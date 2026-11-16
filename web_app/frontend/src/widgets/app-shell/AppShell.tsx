import { useCallback, useEffect, useRef, useState } from 'react';
import type { PropsWithChildren } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { bindTelegramBackButton } from '@/shared/lib/telegram';
import { ElasticScrollArea } from '@/shared/ui/elastic-scroll/ElasticScrollArea';
import appShellContentRaw from '@/widgets/app-shell/appShellContent.yaml?raw';
import { BottomNav } from '@/widgets/bottom-nav/BottomNav';

const appShellContent = JSON.parse(appShellContentRaw) as {
  scrollToTopLabel: string;
};

export function AppShell({ children }: PropsWithChildren) {
  const location = useLocation();
  const navigate = useNavigate();
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);
  const [isNavHidden, setIsNavHidden] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);

  const shouldShowTelegramBackButton = !['/about', '/models', '/support', '/profile'].includes(location.pathname);

  const handleTelegramBack = useCallback(() => {
    const historyIndex = Number((window.history.state as { idx?: number } | null)?.idx ?? 0);

    if (historyIndex > 0) {
      navigate(-1);
      return;
    }

    if (location.pathname.startsWith('/models/')) {
      navigate('/models', { replace: true });
      return;
    }

    navigate('/models', { replace: true });
  }, [location.pathname, navigate]);

  useEffect(() => bindTelegramBackButton(shouldShowTelegramBackButton, handleTelegramBack), [
    handleTelegramBack,
    shouldShowTelegramBackButton,
  ]);

  useEffect(() => {
    if (!scrollAreaRef.current) {
      return;
    }

    scrollAreaRef.current.scrollTop = 0;
    setIsNavHidden(false);
    setShowScrollTop(false);
  }, [location.pathname, location.search]);

  const handleScrollStateChange = ({ scrollTop, direction }: { scrollTop: number; direction: 'up' | 'down' | 'idle' }) => {
    if (scrollTop <= 24) {
      setIsNavHidden(false);
      setShowScrollTop(false);
      return;
    }

    if (direction === 'down' && scrollTop > 72) {
      setIsNavHidden(true);
      setShowScrollTop(true);
      return;
    }

    if (direction === 'up') {
      setIsNavHidden(false);
      setShowScrollTop(false);
    }
  };

  const scrollToTop = () => {
    scrollAreaRef.current?.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
    setIsNavHidden(false);
    setShowScrollTop(false);
  };

  return (
    <div className="app-shell">
      <ElasticScrollArea
        ref={scrollAreaRef}
        className="app-shell__scroll"
        innerClassName="pb-32"
        onScrollStateChange={handleScrollStateChange}
      >
        <div key={location.pathname} className="app-shell__page-transition app-content-safe-top">
          {children}
        </div>
      </ElasticScrollArea>
      <div className={`scroll-top-layer${showScrollTop ? ' scroll-top-layer--visible' : ''}`}>
        <button
          type="button"
          className="scroll-top-button glass-block-soft glass-accent-blue"
          aria-label={appShellContent.scrollToTopLabel}
          onClick={scrollToTop}
        >
          <svg width="26" height="26" viewBox="0 0 384 512" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M214.6 17.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 117.3 160 480c0 17.7 14.3 32 32 32s32-14.3 32-32l0-362.7 105.4 105.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z" fill="currentColor" />
          </svg>
        </button>
      </div>
      <BottomNav hidden={isNavHidden} />
    </div>
  );
}
