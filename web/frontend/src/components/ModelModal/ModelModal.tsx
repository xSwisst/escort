import React, { useEffect, useState } from 'react';
import { Model } from '../../types/model';
import styles from './ModelModal.module.css';

interface ModelModalProps {
  model: Model | null;
  onClose: () => void;
  onBook: (model: Model) => void;
}

export const ModelModal: React.FC<ModelModalProps> = ({
  model,
  onClose,
  onBook,
}) => {
  const [activeModel, setActiveModel] = useState<Model | null>(model);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (model) {
      setActiveModel(model);
      setIsClosing(false);
    } else if (activeModel && !isClosing) {
      setIsClosing(true);
      const timer = setTimeout(() => {
        setIsClosing(false);
        setActiveModel(null);
      }, 260);
      return () => clearTimeout(timer);
    }
  }, [model]);

  const handleClose = () => {
    if (isClosing) return;
    setIsClosing(true);
    setTimeout(() => {
      setIsClosing(false);
      setActiveModel(null);
      onClose();
    }, 260);
  };

  useEffect(() => {
    if (!activeModel) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };

    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeModel, isClosing]);

  if (!activeModel) return null;

  const formatRubles = (val?: number) => {
    if (!val) return 'По запросу';
    return `${val.toLocaleString('ru-RU')} ₽`;
  };

  return (
    <div
      className={`${styles.sheetOverlay} ${isClosing ? styles.sheetOverlayClosing : ''}`}
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className={`${styles.modelsSheet} ${isClosing ? styles.modelsSheetClosing : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.sheetDrag}>
          <div className={styles.sheetDragLine} />
        </div>

        <div className={styles.scrollArea}>
          <div className={styles.photoWrap}>
            <img
              src={activeModel.photos[0]}
              alt={activeModel.name}
              className={styles.mainPhoto}
            />
            <div className={styles.badges}>
              {activeModel.isHealthChecked && (
                <div className={`${styles.badge} ${styles.badgeHealth}`}>
                  <span>HEALTH+</span>
                </div>
              )}
              {activeModel.isVerified && (
                <div className={`${styles.badge} ${styles.badgeCheck}`}>
                  <span>CHECK</span>
                </div>
              )}
            </div>
          </div>

          <div className={styles.infoBlock}>
            <h2 className={styles.name}>{activeModel.name}</h2>
            <div className={styles.specsLine}>
              {activeModel.age} лет • {activeModel.height} см • {activeModel.bust} size • {activeModel.cityName}
            </div>
            <p className={styles.desc}>{activeModel.description}</p>
          </div>

          <div className={styles.tariffsBlock}>
            <div className={styles.tariffRow}>
              <span>1 час</span>
              <span className={styles.tariffPrice}>{formatRubles(activeModel.prices.oneHour)}</span>
            </div>
            <div className={styles.tariffRow}>
              <span>2 часа</span>
              <span className={styles.tariffPrice}>{formatRubles(activeModel.prices.twoHours)}</span>
            </div>
            <div className={styles.tariffRow}>
              <span>Вся ночь</span>
              <span className={styles.tariffPrice}>{formatRubles(activeModel.prices.night)}</span>
            </div>
          </div>

          <button
            type="button"
            className={styles.orderBtn}
            onClick={() => {
              handleClose();
              onBook(activeModel);
            }}
          >
            <span>Подробнее</span>
          </button>
        </div>
      </div>
    </div>
  );
};
