import React from 'react';
import { AGENCY_SERVICES } from '../../data/servicesData';
import styles from './Services.module.css';

export const Services: React.FC = () => {
  return (
    <section id="services" className={styles.section} aria-label="VIP Услуги">
      <div className={styles.headingBlock}>
        <h2 className={styles.title}>Форматы встреч</h2>
        <p className={styles.subtitle}>Индивидуальный сервис высшего уровня</p>
      </div>

      <div className={styles.grid}>
        {AGENCY_SERVICES.map((item) => (
          <div key={item.id} className={styles.card}>
            <div className={styles.topRow}>
              <h3 className={styles.cardTitle}>{item.title}</h3>
              <span className={styles.tag}>{item.tag}</span>
            </div>
            <p className={styles.desc}>{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
