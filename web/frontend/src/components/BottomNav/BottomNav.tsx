import React, { useRef, useState, useEffect } from 'react';
import styles from './BottomNav.module.css';

export type AppNavTab = 'models' | 'guarantees' | 'services' | 'faq' | 'profile';

interface BottomNavProps {
  activeTab: AppNavTab;
  onSelectTab: (tab: AppNavTab) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({
  activeTab,
  onSelectTab,
}) => {
  const [jelloTarget, setJelloTarget] = useState<string | null>(null);
  const jelloTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (jelloTimeoutRef.current) {
        window.clearTimeout(jelloTimeoutRef.current);
      }
    };
  }, []);

  const handleTabClick = (tab: AppNavTab) => {
    if (jelloTimeoutRef.current) {
      window.clearTimeout(jelloTimeoutRef.current);
    }

    setJelloTarget(null);

    window.requestAnimationFrame(() => {
      setJelloTarget(tab);
      jelloTimeoutRef.current = window.setTimeout(() => {
        setJelloTarget(null);
        jelloTimeoutRef.current = null;
      }, 580);
    });

    onSelectTab(tab);
  };

  const getActiveIndex = (): number => {
    switch (activeTab) {
      case 'models':
        return 0;
      case 'guarantees':
        return 1;
      case 'services':
        return 2;
      case 'faq':
        return 3;
      default:
        return -1;
    }
  };

  return (
    <nav className={styles.tabbarWrapper} aria-label="Навигационная панель">
      <div className={styles.tabbarRoot}>
        <div className={styles.switcher} data-active={getActiveIndex()} role="tablist">
          {/* 1. Модели (Каталог) */}
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'models'}
            className={`${styles.tabBtn} ${activeTab === 'models' ? styles.tabBtnActive : ''}`}
            onClick={() => handleTabClick('models')}
          >
            <div className={`${styles.iconWrap} ${jelloTarget === 'models' ? styles.navIconJello : ''}`}>
              <svg width="18" height="18" viewBox="0 0 384 512" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M80 176a112 112 0 1 1 224 0 112 112 0 1 1 -224 0zM223.9 349.1C305.9 334.1 368 262.3 368 176 368 78.8 289.2 0 192 0S16 78.8 16 176c0 86.3 62.1 158.1 144.1 173.1-.1 1-.1 1.9-.1 2.9l0 64-32 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l32 0 0 32c0 17.7 14.3 32 32 32s32-14.3 32-32l0-32 32 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-32 0 0-64c0-1 0-1.9-.1-2.9z" fill="currentColor"/>
              </svg>
            </div>
            <span>Модели</span>
          </button>

          {/* 2. Гарантии */}
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'guarantees'}
            className={`${styles.tabBtn} ${activeTab === 'guarantees' ? styles.tabBtnActive : ''}`}
            onClick={() => handleTabClick('guarantees')}
          >
            <div className={`${styles.iconWrap} ${jelloTarget === 'guarantees' ? styles.navIconJello : ''}`}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <span>Гарантии</span>
          </button>

          {/* 3. Форматы */}
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'services'}
            className={`${styles.tabBtn} ${activeTab === 'services' ? styles.tabBtnActive : ''}`}
            onClick={() => handleTabClick('services')}
          >
            <div className={`${styles.iconWrap} ${jelloTarget === 'services' ? styles.navIconJello : ''}`}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
              </svg>
            </div>
            <span>Форматы</span>
          </button>

          {/* 4. FAQ */}
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'faq'}
            className={`${styles.tabBtn} ${activeTab === 'faq' ? styles.tabBtnActive : ''}`}
            onClick={() => handleTabClick('faq')}
          >
            <div className={`${styles.iconWrap} ${jelloTarget === 'faq' ? styles.navIconJello : ''}`}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <span>FAQ</span>
          </button>
        </div>

        {/* 5. Бот / Telegram */}
        <button
          type="button"
          aria-label="Открыть Telegram бота"
          aria-selected={activeTab === 'profile'}
          className={`${styles.profileBtn} ${activeTab === 'profile' ? styles.profileBtnActive : ''}`}
          onClick={() => handleTabClick('profile')}
        >
          <div className={`${styles.profileIconWrap} ${jelloTarget === 'profile' ? styles.navIconJello : ''}`}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 8V4H8"/>
              <rect width="16" height="12" x="4" y="8" rx="3"/>
              <path d="M2 14h2"/>
              <path d="M20 14h2"/>
              <path d="M15 13v2"/>
              <path d="M9 13v2"/>
            </svg>
          </div>
        </button>
      </div>
    </nav>
  );
};
