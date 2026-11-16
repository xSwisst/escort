import React from 'react';
import { Star } from 'lucide-react';
import { CLIENT_REVIEWS } from '../../data/reviewsData';
import styles from './Reviews.module.css';

export const Reviews: React.FC = () => {
  return (
    <section id="reviews" className={styles.section} aria-label="Отзывы гостей">
      <div className={styles.headingBlock}>
        <h2 className={styles.title}>Отзывы гостей</h2>
        <p className={styles.subtitle}>Мнения клиентов о качестве сервиса и пунктуальности</p>
      </div>

      <div className={styles.grid}>
        {CLIENT_REVIEWS.map((item) => (
          <article key={item.id} className={styles.card}>
            <div className={styles.header}>
              <div>
                <h3 className={styles.authorName}>{item.clientName}</h3>
                <span className={styles.badge}>{item.clientBadge}</span>
              </div>
              <div style={{ display: 'flex', gap: '2px', color: '#F5A623' }}>
                {[...Array(item.rating)].map((_, i) => (
                  <Star key={i} size={13} fill="currentColor" />
                ))}
              </div>
            </div>

            <p className={styles.comment}>"{item.content}"</p>

            <div className={styles.footer}>
              <span>{item.city}</span>
              <span>{item.date}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};
