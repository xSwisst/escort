export interface ModelPrices {
  oneHour: number;
  twoHours: number;
  threeHours: number;
  night: number;
}

export interface ModelService {
  id: number;
  name: string;
  included: boolean;
}

export interface ModelAdditional {
  id: number;
  name: string;
  price: number;
}

export interface ModelReview {
  id: number;
  author: string;
  city: string;
  date: string;
  rating: number;
  comment: string;
}

export interface Model {
  id: string;
  code: string;
  name: string;
  cityId: string;
  cityName: string;
  age: number;
  height: number;
  weight: number;
  bust: number;
  waist: number;
  hips: number;
  rating: number;
  reviewsCount: number;
  isVerified: boolean;
  isHealthChecked: boolean;
  isTopChoice: boolean;
  photos: string[];
  description: string;
  languages: string[];
  prices: ModelPrices;
  services: ModelService[];
  additionals: ModelAdditional[];
  reviews: ModelReview[];
}
