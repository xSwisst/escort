import React from 'react';
import { CheckCircle } from 'lucide-react';
import { Model } from '../../types/model';
import { useBooking } from '../../hooks/useBooking';
import { getTelegramBotUrl } from '../../utils/config';
import styles from './BookingModal.module.css';


interface BookingModalProps {
  model: Model | null;
  isOpen: boolean;
  onClose: () => void;
}

export const BookingModal: React.FC<BookingModalProps> = ({
  model,
  isOpen,
  onClose,
}) => {
  const {
    form,
    step,
    setStep,
    isSuccess,
    summary,
    setTariff,
    updateField,
    submitBooking,
    resetBooking,
  } = useBooking(model);

  if (!isOpen || !model) return null;

  const formatRubles = (val: number) => {
    return new Intl.NumberFormat('ru-RU').format(val) + ' ₽';
  };

  const handleClose = () => {
    resetBooking();
    onClose();
  };

  return (
    <div className={styles.overlay} onClick={handleClose} role="dialog" aria-modal="true">
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>


        {isSuccess ? (
          <div className={styles.successBox}>
            <div className={styles.successIcon}>
              <CheckCircle size={28} />
            </div>
            <h3 className={styles.successTitle}>Бронирование подтверждено</h3>
            <p className={styles.successText}>
              Ваш запрос на встречу с моделью <strong>{model.name}</strong> успешно сформирован.
              Персональный VIP консьерж свяжется с вами в течение 5 минут для согласования деталей.
            </p>
            <button
              type="button"
              className={styles.nextBtn}
              onClick={() => {
                window.open(getTelegramBotUrl(model.code), '_blank');
                handleClose();
              }}

            >
              Открыть чат с консьержем в Telegram
            </button>
          </div>
        ) : (
          <>
            <h3 className={styles.title}>Бронирование встречи</h3>
            <p className={styles.subtitle}>
              Модель: {model.name} ({model.code}) • {model.cityName}
            </p>

            <div className={styles.stepIndicator}>
              <div className={`${styles.stepDot} ${step >= 1 ? styles.stepDotActive : ''}`} />
              <div className={`${styles.stepDot} ${step >= 2 ? styles.stepDotActive : ''}`} />
              <div className={`${styles.stepDot} ${step >= 3 ? styles.stepDotActive : ''}`} />
            </div>

            {step === 1 && (
              <div>
                <div className={styles.grid2}>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>Дата</label>
                    <input
                      type="date"
                      className={styles.input}
                      value={form.date}
                      onChange={(e) => updateField('date', e.target.value)}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>Время</label>
                    <input
                      type="time"
                      className={styles.input}
                      value={form.time}
                      onChange={(e) => updateField('time', e.target.value)}
                    />
                  </div>
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.label}>Место встречи</label>
                  <div className={styles.placeToggle}>
                    <button
                      type="button"
                      className={`${styles.placeBtn} ${form.place === 'model' ? styles.placeBtnActive : ''}`}
                      onClick={() => updateField('place', 'model')}
                    >
                      Апартаменты модели
                    </button>
                    <button
                      type="button"
                      className={`${styles.placeBtn} ${form.place === 'client' ? styles.placeBtnActive : ''}`}
                      onClick={() => updateField('place', 'client')}
                    >
                      Выезд (Отель / Адрес)
                    </button>
                  </div>
                </div>

                {form.place === 'client' && (
                  <div className={styles.formGroup}>
                    <label className={styles.label}>Адрес встречи или название отеля</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="Например: Four Seasons, номер 712"
                      value={form.address}
                      onChange={(e) => updateField('address', e.target.value)}
                    />
                  </div>
                )}

                <button
                  type="button"
                  className={styles.nextBtn}
                  onClick={() => setStep(2)}
                >
                  Продолжить к выбору тарифа
                </button>
              </div>
            )}

            {step === 2 && (
              <div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Длительность встречи</label>
                  <div className={styles.tariffsList}>
                    <div
                      className={`${styles.tariffCard} ${form.tariff === 'oneHour' ? styles.tariffCardActive : ''}`}
                      onClick={() => setTariff('oneHour')}
                    >
                      <span className={styles.tariffCardTitle}>1 час</span>
                      <span className={styles.tariffCardPrice}>{formatRubles(model.prices.oneHour)}</span>
                    </div>
                    <div
                      className={`${styles.tariffCard} ${form.tariff === 'twoHours' ? styles.tariffCardActive : ''}`}
                      onClick={() => setTariff('twoHours')}
                    >
                      <span className={styles.tariffCardTitle}>2 часа</span>
                      <span className={styles.tariffCardPrice}>{formatRubles(model.prices.twoHours)}</span>
                    </div>
                    <div
                      className={`${styles.tariffCard} ${form.tariff === 'threeHours' ? styles.tariffCardActive : ''}`}
                      onClick={() => setTariff('threeHours')}
                    >
                      <span className={styles.tariffCardTitle}>3 часа</span>
                      <span className={styles.tariffCardPrice}>{formatRubles(model.prices.threeHours)}</span>
                    </div>
                    <div
                      className={`${styles.tariffCard} ${form.tariff === 'night' ? styles.tariffCardActive : ''}`}
                      onClick={() => setTariff('night')}
                    >
                      <span className={styles.tariffCardTitle}>Вся ночь</span>
                      <span className={styles.tariffCardPrice}>{formatRubles(model.prices.night)}</span>
                    </div>
                  </div>
                </div>

                <div className={styles.summaryBox}>
                  <span className={styles.summaryTotalLabel}>Итоговая сумма:</span>
                  <span className={styles.summaryTotalPrice}>{formatRubles(summary.totalPrice)}</span>
                </div>

                <button
                  type="button"
                  className={styles.nextBtn}
                  onClick={() => setStep(3)}
                >
                  Перейти к контактам
                </button>

                <button
                  type="button"
                  className={styles.backBtn}
                  onClick={() => setStep(1)}
                >
                  Назад к дате и месту
                </button>
              </div>
            )}

            {step === 3 && (
              <div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>Как к вам обращаться</label>
                  <input
                    type="text"
                    className={styles.input}
                    placeholder="Ваше имя или псевдоним"
                    value={form.clientName}
                    onChange={(e) => updateField('clientName', e.target.value)}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label className={styles.label}>Контакт для связи (Telegram / Телефон)</label>
                  <input
                    type="text"
                    className={styles.input}
                    placeholder="@username или +7 (999) 000-00-00"
                    value={form.clientContact}
                    onChange={(e) => updateField('clientContact', e.target.value)}
                  />
                </div>

                <div className={styles.summaryBox}>
                  <span className={styles.summaryTotalLabel}>Итого к оплате:</span>
                  <span className={styles.summaryTotalPrice}>{formatRubles(summary.totalPrice)}</span>
                </div>

                <button
                  type="button"
                  className={styles.nextBtn}
                  onClick={submitBooking}
                >
                  Завершить бронирование
                </button>

                <button
                  type="button"
                  className={styles.backBtn}
                  onClick={() => setStep(2)}
                >
                  Назад к тарифу
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
