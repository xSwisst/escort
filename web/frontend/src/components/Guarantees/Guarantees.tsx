import React from 'react';
import { ShieldCheck, UserCheck, HeartPulse, Clock } from 'lucide-react';
import styles from './Guarantees.module.css';

export const Guarantees: React.FC = () => {
  const items = [
    {
      icon: ShieldCheck,
      title: 'Безопасность данных',
      text: 'Доступ к заявке получает только рабочий контур сервиса и менеджер, который сопровождает оформление. Лишним участникам данные не раскрываются.',
    },
    {
      icon: UserCheck,
      title: 'Проверка анкет (CHECK)',
      text: 'Анкеты проходят внутреннюю модерацию и обновляются по статусам. Все данные соответствуют действительности.',
    },
    {
      icon: HeartPulse,
      title: 'Контроль здоровья (HEALTH+)',
      text: 'Регулярный медицинский контроль и проверка параметров для безопасного и комфортного отдыха.',
    },
    {
      icon: Clock,
      title: 'Поддержка 24/7',
      text: 'В спорной ситуации можно сразу написать в поддержку или менеджеру. Оперативная помощь на каждом этапе оформления.',
    },
  ];

  return (
    <section id="guarantees" className={styles.section} aria-label="Стандарты сервиса">
      <div className={styles.headingBlock}>
        <h2 className={styles.title}>Гарантии и безопасность</h2>
        <p className={styles.subtitle}>Правила сервиса, защита данных и стандарты оформления</p>
      </div>

      <div className={styles.grid}>
        {items.map((item, index) => {
          const Icon = item.icon;
          return (
            <div key={index} className={styles.card}>
              <div className={styles.iconWrap}>
                <Icon size={20} />
              </div>
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{item.title}</h3>
                <p className={styles.cardText}>{item.text}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
