import React from 'react';
import { Send } from 'lucide-react';
import { Model } from '../../types/model';
import { ModelCard } from './ModelCard';
import styles from './Catalog.module.css';

interface CatalogProps {
  models: Model[];
  favoriteIds: string[];
  onToggleFavorite: (id: string) => void;
  onOpenDetails: (model: Model) => void;
  onBookNow: (model: Model) => void;
  onOpenTelegram: () => void;
}

export const Catalog: React.FC<CatalogProps> = ({
  models,
  favoriteIds,
  onToggleFavorite,
  onOpenDetails,
  onBookNow,
  onOpenTelegram,
}) => {
  return (
    <section id="catalog" className={styles.catalogSection} aria-label="Каталог анкет">
      <div className={styles.headingRow}>
        <div>
          <h2 className={styles.title}>Одни из лучших наших моделей</h2>
          <p className={styles.subtitle}>
            Анкеты проходят внутреннюю модерацию и регулярный медицинский контроль.
          </p>
        </div>
      </div>

      <div className={styles.modelsGrid}>
        {models.map((model) => (
          <ModelCard
            key={model.id}
            model={model}
            isFavorite={favoriteIds.includes(model.id)}
            onToggleFavorite={onToggleFavorite}
            onOpenDetails={onOpenDetails}
            onBookNow={onBookNow}
          />
        ))}
      </div>

      <div className={styles.tgBanner}>
        <div>
          <h3 className={styles.tgBannerTitle}>Открыть полный каталог</h3>
          <p className={styles.tgBannerText}>
            Все анкеты с видеовизитками, выбором городов и прямым бронированием в Telegram сервисе.
          </p>
        </div>

        <button
          type="button"
          className={styles.tgBannerBtn}
          onClick={onOpenTelegram}
        >
          <Send size={16} />
          <span>Открыть полный каталог</span>
        </button>
      </div>
    </section>
  );
};
