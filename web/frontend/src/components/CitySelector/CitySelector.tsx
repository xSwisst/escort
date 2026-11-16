import React, { useEffect } from 'react';
import { Check } from 'lucide-react';
import { CITIES } from '../../data/cities';
import styles from './CitySelector.module.css';

interface CitySelectorProps {
  isOpen: boolean;
  currentCityId: string;
  onClose: () => void;
  onSelectCity: (cityId: string) => void;
}

export const CitySelector: React.FC<CitySelectorProps> = ({
  isOpen,
  currentCityId,
  onClose,
  onSelectCity,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={styles.sheetOverlay} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.sheet} onClick={(e) => e.stopPropagation()}>
        <div className={styles.sheetDrag}>
          <div className={styles.sheetDragLine} />
        </div>

        <div className={styles.body}>
          <h3 className={styles.title}>Выбор города</h3>

          <div className={styles.menu}>
            {CITIES.map((city) => {
              const isSelected = city.id === currentCityId;
              return (
                <button
                  key={city.id}
                  type="button"
                  className={`${styles.item} ${isSelected ? styles.itemCurrent : ''}`}
                  onClick={() => {
                    onSelectCity(city.id);
                    onClose();
                  }}
                >
                  <span>{city.name}</span>
                  {isSelected ? (
                    <Check size={16} />
                  ) : (
                    <span className={styles.country}>{city.country}</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
