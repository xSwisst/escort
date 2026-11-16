import { useState, useMemo } from 'react';
import { Model } from '../types/model';
import { FilterState } from '../types/common';

const initialFilters: FilterState = {
  cityId: 'all',
  searchQuery: '',
  verifiedOnly: false,
  healthCheckedOnly: false,
  sort: 'recommended',
  onlyFavorites: false,
};

export function useModelFilters(allModels: Model[], favoriteIds: string[]) {
  const [filters, setFilters] = useState<FilterState>(initialFilters);

  const setCity = (cityId: string) => {
    setFilters((prev) => ({ ...prev, cityId }));
  };

  const setSearchQuery = (searchQuery: string) => {
    setFilters((prev) => ({ ...prev, searchQuery }));
  };

  const toggleVerified = () => {
    setFilters((prev) => ({ ...prev, verifiedOnly: !prev.verifiedOnly }));
  };

  const toggleHealthChecked = () => {
    setFilters((prev) => ({ ...prev, healthCheckedOnly: !prev.healthCheckedOnly }));
  };

  const setSort = (sort: FilterState['sort']) => {
    setFilters((prev) => ({ ...prev, sort }));
  };

  const setOnlyFavorites = (onlyFavorites: boolean) => {
    setFilters((prev) => ({ ...prev, onlyFavorites }));
  };

  const resetFilters = () => {
    setFilters(initialFilters);
  };

  const filteredModels = useMemo(() => {
    return allModels
      .filter((model) => {
        // City filter
        if (filters.cityId !== 'all' && model.cityId !== filters.cityId) {
          return false;
        }

        // Favorites filter
        if (filters.onlyFavorites && !favoriteIds.includes(model.id)) {
          return false;
        }

        // Verified filters
        if (filters.verifiedOnly && !model.isVerified) {
          return false;
        }
        if (filters.healthCheckedOnly && !model.isHealthChecked) {
          return false;
        }

        // Search query
        if (filters.searchQuery.trim()) {
          const query = filters.searchQuery.toLowerCase().trim();
          const matchName = model.name.toLowerCase().includes(query);
          const matchCode = model.code.toLowerCase().includes(query);
          const matchCity = model.cityName.toLowerCase().includes(query);
          const matchDesc = model.description.toLowerCase().includes(query);
          if (!matchName && !matchCode && !matchCity && !matchDesc) {
            return false;
          }
        }

        return true;
      })
      .sort((a, b) => {
        if (filters.sort === 'price-asc') {
          return a.prices.oneHour - b.prices.oneHour;
        }
        if (filters.sort === 'price-desc') {
          return b.prices.oneHour - a.prices.oneHour;
        }
        if (filters.sort === 'rating-desc') {
          return b.rating - a.rating;
        }
        return (b.isTopChoice ? 1 : 0) - (a.isTopChoice ? 1 : 0);
      });
  }, [allModels, filters, favoriteIds]);

  return {
    filters,
    filteredModels,
    setCity,
    setSearchQuery,
    toggleVerified,
    toggleHealthChecked,
    setSort,
    setOnlyFavorites,
    resetFilters,
  };
}
