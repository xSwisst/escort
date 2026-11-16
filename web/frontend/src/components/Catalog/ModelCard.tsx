import React from 'react';
import { Model } from '../../types/model';
import styles from './ModelCard.module.css';

interface ModelCardProps {
  model: Model;
  isFavorite: boolean;
  onToggleFavorite: (id: string) => void;
  onOpenDetails: (model: Model) => void;
  onBookNow: (model: Model) => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({
  model,
  isFavorite,
  onToggleFavorite,
  onOpenDetails,
}) => {
  return (
    <article className={styles.card} onClick={() => onOpenDetails(model)}>
      <div className={styles.photoWrap}>
        <img
          src={model.photos[0]}
          alt={model.name}
          className={styles.photo}
          loading="lazy"
        />

        <div className={styles.badges}>
          {model.isHealthChecked && (
            <div className={`${styles.badge} ${styles.badgeHealth}`}>
              <span>HEALTH+</span>
            </div>
          )}
          {model.isVerified && (
            <div className={`${styles.badge} ${styles.badgeCheck}`}>
              <span>CHECK</span>
            </div>
          )}
        </div>

        <button
          type="button"
          className={`${styles.favoriteFloating} ${isFavorite ? styles.favoriteActive : ''}`}
          aria-label={isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(model.id);
          }}
        >
          {isFavorite ? (
            <svg
              width="17"
              height="17"
              viewBox="0 0 512 512"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
              className={styles.heartSvg}
            >
              <path
                d="M241 87.1l15 20.7 15-20.7C296 52.5 336.2 32 378.9 32 452.4 32 512 91.6 512 165.1l0 2.6c0 112.2-139.9 242.5-212.9 298.2-12.4 9.4-27.6 14.1-43.1 14.1s-30.8-4.6-43.1-14.1C139.9 410.2 0 279.9 0 167.7l0-2.6C0 91.6 59.6 32 133.1 32 175.8 32 216 52.5 241 87.1z"
                fill="#ff3b5c"
              />
            </svg>
          ) : (
            <svg
              width="17"
              height="17"
              viewBox="0 0 512 512"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
              className={styles.heartSvg}
            >
              <path
                d="M241 87.1l15 20.7 15-20.7C296 52.5 336.2 32 378.9 32 452.4 32 512 91.6 512 165.1l0 2.6c0 112.2-139.9 242.5-212.9 298.2-12.4 9.4-27.6 14.1-43.1 14.1s-30.8-4.6-43.1-14.1C139.9 410.2 0 279.9 0 167.7l0-2.6C0 91.6 59.6 32 133.1 32 175.8 32 216 52.5 241 87.1z"
                fill="none"
                stroke="#fff"
                strokeWidth="32"
              />
            </svg>
          )}
        </button>
      </div>

      <div className={styles.cardInfo}>
        <div className={styles.nameRow}>
          <h2 className={styles.name}>{model.name}</h2>
          <span className={styles.priceTeaser}>
            {new Intl.NumberFormat('ru-RU').format(model.prices.oneHour)} ₽/ч
          </span>
        </div>
        <p className={styles.params}>
          {model.age} лет • {model.height} см • {model.bust} size
        </p>
      </div>
    </article>
  );
};
