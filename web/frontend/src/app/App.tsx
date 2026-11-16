import React, { useState } from 'react';
import { MODELS_DATA } from '../data/modelsData';
import { Model } from '../types/model';
import { useFavorites } from '../hooks/useFavorites';

import { JsonLd } from '../components/SEO/JsonLd';
import { Header } from '../components/Header/Header';
import { Hero } from '../components/Hero/Hero';
import { Catalog } from '../components/Catalog/Catalog';
import { Guarantees } from '../components/Guarantees/Guarantees';
import { Services } from '../components/Services/Services';
import { Reviews } from '../components/Reviews/Reviews';
import { FAQ } from '../components/FAQ/FAQ';
import { Footer } from '../components/Footer/Footer';
import { BottomNav, AppNavTab } from '../components/BottomNav/BottomNav';
import { ModelModal } from '../components/ModelModal/ModelModal';
import { getTelegramBotUrl } from '../utils/config';

import styles from './App.module.css';

export const App: React.FC = () => {
  const { favoriteIds, toggleFavorite } = useFavorites();
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [activeTab, setActiveTab] = useState<AppNavTab>('models');

  const handleOpenTelegram = (modelCode?: string) => {
    const url = getTelegramBotUrl(modelCode);
    window.open(url, '_blank');
  };


  const handleExploreCatalog = () => {
    const el = document.getElementById('catalog');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const isProgrammaticScroll = React.useRef(false);
  const scrollTimeoutRef = React.useRef<number | null>(null);

  const handleSelectTab = (tab: AppNavTab) => {
    setActiveTab(tab);
    if (tab === 'profile') {
      handleOpenTelegram();
      return;
    }

    isProgrammaticScroll.current = true;
    if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
    scrollTimeoutRef.current = window.setTimeout(() => {
      isProgrammaticScroll.current = false;
    }, 700);

    const targetMap: Record<string, string> = {
      models: 'catalog',
      guarantees: 'guarantees',
      services: 'services',
      faq: 'faq',
    };

    const targetId = targetMap[tab];
    if (targetId) {
      const el = document.getElementById(targetId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  React.useEffect(() => {
    const sectionIds: { id: string; tab: AppNavTab }[] = [
      { id: 'catalog', tab: 'models' },
      { id: 'guarantees', tab: 'guarantees' },
      { id: 'services', tab: 'services' },
      { id: 'faq', tab: 'faq' },
    ];

    const observer = new IntersectionObserver(
      (entries) => {
        if (isProgrammaticScroll.current) return;
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length > 0) {
          visible.sort((a, b) => b.intersectionRatio - a.intersectionRatio);
          const matched = sectionIds.find((s) => s.id === visible[0].target.id);
          if (matched) {
            setActiveTab((prev) => (prev === matched.tab ? prev : matched.tab));
          }
        }
      },
      {
        rootMargin: '-15% 0px -45% 0px',
        threshold: [0.1, 0.3, 0.6],
      }
    );

    sectionIds.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className={styles.app}>
      <JsonLd />

      <Header onOpenConcierge={() => handleOpenTelegram()} />

      <main className={styles.mainContent}>
        <div className={styles.container}>
          <Hero
            onOpenConcierge={() => handleOpenTelegram()}
            onExploreCatalog={handleExploreCatalog}
          />

          <Catalog
            models={MODELS_DATA}
            favoriteIds={favoriteIds}
            onToggleFavorite={toggleFavorite}
            onOpenDetails={(model) => setSelectedModel(model)}
            onBookNow={(model) => handleOpenTelegram(model.code)}
            onOpenTelegram={() => handleOpenTelegram()}
          />

          <Guarantees />
          <Services />
          <Reviews />
          <FAQ />
          <Footer onOpenConcierge={() => handleOpenTelegram()} />
        </div>
      </main>

      {/* Floating Bottom Nav for both PC & Mobile */}
      <BottomNav activeTab={activeTab} onSelectTab={handleSelectTab} />

      {/* Model Bottom Sheet */}
      <ModelModal
        model={selectedModel}
        onClose={() => setSelectedModel(null)}
        onBook={(model) => handleOpenTelegram(model.code)}
      />
    </div>
  );
};
