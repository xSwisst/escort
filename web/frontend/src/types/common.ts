export interface City {
  id: string;
  name: string;
  country: string;
  isPopular?: boolean;
}

export type SortOption = 'recommended' | 'price-asc' | 'price-desc' | 'rating-desc';

export interface FilterState {
  cityId: string;
  searchQuery: string;
  verifiedOnly: boolean;
  healthCheckedOnly: boolean;
  minPrice?: number;
  maxPrice?: number;
  ageRange?: [number, number];
  sort: SortOption;
  onlyFavorites: boolean;
}
