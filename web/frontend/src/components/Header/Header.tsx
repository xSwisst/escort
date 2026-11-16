import React from 'react';
import { Send } from 'lucide-react';
import styles from './Header.module.css';

interface HeaderProps {
  onOpenConcierge: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenConcierge }) => {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <a href="#" className={styles.logo}>
          <img src="/logo.svg" alt="Elegant Agency" className={styles.logoImg} />
          <div className={styles.logoText}>
            <span className={styles.logoTitle}>Elegant Agency</span>
            <span className={styles.logoSubtitle}>VIP Escort Service</span>
          </div>
        </a>

        <nav className={styles.desktopNav} aria-label="Основное меню">
          <a href="#catalog" className={styles.navLink}>Модели</a>
          <a href="#guarantees" className={styles.navLink}>Гарантии</a>
          <a href="#services" className={styles.navLink}>Форматы</a>
          <a href="#reviews" className={styles.navLink}>Отзывы</a>
          <a href="#faq" className={styles.navLink}>FAQ</a>
        </nav>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.tgTopBtn}
            onClick={onOpenConcierge}
          >
            <Send size={14} />
            <span>Открыть каталог</span>
          </button>
        </div>
      </div>
    </header>
  );
};
