import React from 'react';
import { Send } from 'lucide-react';
import styles from './Footer.module.css';

interface FooterProps {
  onOpenConcierge: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenConcierge }) => {
  return (
    <footer className={styles.footer} aria-label="Подвал сайта">
      <div className={styles.topGrid}>
        <div className={styles.brandCol}>
          <div className={styles.brandHeader}>
            <img src="/logo.svg" alt="Elegant Agency" className={styles.footerLogo} />
            <div className={styles.brandName}>Elegant Agency • VIP Service</div>
          </div>
          <p className={styles.brandDesc}>
            Внутренняя модерация анкет, безопасность данных и персональный менеджер 24/7.
          </p>
          <button
            type="button"
            className={styles.tgFooterBtn}
            onClick={onOpenConcierge}
          >
            <Send size={15} />
            <span>Открыть каталог</span>
          </button>
        </div>

        <div className={styles.navColumns}>
          <div className={styles.col}>
            <h4 className={styles.colTitle}>Разделы</h4>
            <ul className={styles.linksList}>
              <li>
                <a href="#catalog" className={styles.link}>
                  Модели
                </a>
              </li>
              <li>
                <a href="#guarantees" className={styles.link}>
                  Гарантии и безопасность
                </a>
              </li>
              <li>
                <a href="#services" className={styles.link}>
                  Форматы встреч
                </a>
              </li>
              <li>
                <a href="#reviews" className={styles.link}>
                  Отзывы
                </a>
              </li>
              <li>
                <a href="#faq" className={styles.link}>
                  Информация
                </a>
              </li>
            </ul>
          </div>

          <div className={styles.col}>
            <h4 className={styles.colTitle}>Связь с нами</h4>
            <ul className={styles.linksList}>
              <li className={styles.link}>Москва, Башня Федерация</li>
              <li className={styles.link}>Круглосуточно, 24/7</li>
              <li className={styles.link} onClick={onOpenConcierge}>Поддержка: @support</li>
              <li className={styles.link}>Конфиденциально 100%</li>
              <li className={styles.link}>Бронирование онлайн</li>
            </ul>
          </div>
        </div>
      </div>

      <div className={styles.bottomBar}>
        <div>© 2026 Elegant Agency. Все права защищены. 18+</div>
        <div>Оформление заявок и координация встреч осуществляется через Telegram.</div>
      </div>
    </footer>
  );
};
