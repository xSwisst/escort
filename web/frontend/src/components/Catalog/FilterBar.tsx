import React from 'react';
import { Search, SlidersHorizontal, ArrowUpDown } from 'lucide-react';
import { FilterState } from '../../types/common';
import styles from './FilterBar.module.css';

interface FilterBarProps {
  filters: FilterState;
  activeCityName: string;
  onOpenCitySwitcher: () => void;
  onSearchChange: (query: string) => void;
  onToggleVerified: () => void;
  onCycleSort: () => void;
  onSelectTab: (onlyFavorites: boolean) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  activeCityName,
  onOpenCitySwitcher,
  onSearchChange,
  onToggleVerified,
  onCycleSort,
  onSelectTab,
}) => {
  return (
    <div className={styles.wrapper}>
      {/* Authentic Section Switcher Tabs */}
      <div className={styles.modelsSections} role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={!filters.onlyFavorites}
          className={`${styles.modelsSectionsButton} ${
            !filters.onlyFavorites ? styles.modelsSectionsButtonActive : ''
          }`}
          onClick={() => onSelectTab(false)}
        >
          Все модели
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={filters.onlyFavorites}
          className={`${styles.modelsSectionsButton} ${
            filters.onlyFavorites ? styles.modelsSectionsButtonActive : ''
          }`}
          onClick={() => onSelectTab(true)}
        >
          Избранные
        </button>
      </div>

      <div className={styles.controls}>
        <div className={styles.searchRow}>
          <label className={styles.search}>
            <Search size={18} className={styles.searchIcon} />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Быстрый поиск"
              value={filters.searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
            />
          </label>

          <button
            type="button"
            className={styles.cityChip}
            onClick={onOpenCitySwitcher}
            aria-label="Выбрать город"
          >
            <span>{activeCityName}</span>
          </button>

          <div className={styles.toolbar}>
            <button
              type="button"
              className={`${styles.toolbarBtn} ${
                filters.verifiedOnly ? styles.toolbarBtnActive : ''
              }`}
              onClick={onToggleVerified}
              title="Фильтр: Только CHECK"
            >
              <SlidersHorizontal size={17} />
            </button>

            <button
              type="button"
              className={styles.toolbarBtn}
              onClick={onCycleSort}
              title="Сортировка"
            >
              <ArrowUpDown size={17} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
