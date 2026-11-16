import { City } from '../types/common';

export const CITIES: City[] = [
  { id: 'all', name: 'Все города', country: 'Международный', isPopular: false },
  { id: 'msk', name: 'Москва', country: 'Россия', isPopular: true },
  { id: 'spb', name: 'Санкт-Петербург', country: 'Россия', isPopular: true },
  { id: 'dxb', name: 'Дубай', country: 'ОАЭ', isPopular: true },
  { id: 'sochi', name: 'Сочи', country: 'Россия', isPopular: true },
];

export const DEFAULT_CITY = CITIES[1]; // Москва
