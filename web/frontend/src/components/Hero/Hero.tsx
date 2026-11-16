import React from 'react';
import styles from './Hero.module.css';

interface HeroProps {
  onOpenConcierge?: () => void;
  onExploreCatalog?: () => void;
}

export const Hero: React.FC<HeroProps> = () => {
  return (
    <section className={styles.heroSection} aria-label="Главный экран">
      <div className={styles.bannerCard}>
        <img
          src="/banner.jpg"
          alt="Elegant Agency VIP"
          className={styles.bannerImg}
        />
        <div className={styles.bannerOverlay}>
          <span className={styles.bannerTag}>VIP Сервис</span>
          <h1 className={styles.bannerTitle}>
            Премиальное сопровождение и VIP консьерж
          </h1>
        </div>
      </div>
    </section>
  );
};
