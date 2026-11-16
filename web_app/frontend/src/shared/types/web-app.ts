export type AppSection = 'about' | 'models' | 'support' | 'profile';

export type WebAppSessionResponse = {
  sessionToken: string;
  expiresAt: string;
  user: {
    telegramId: number;
    firstName: string;
    lastName?: string | null;
    username?: string | null;
    photoUrl?: string | null;
  };
  client: {
    workerId?: number | null;
    agreementAccepted: boolean;
    isBanned: boolean;
  };
  environment: {
    telegram: boolean;
    mock: boolean;
  };
};

export type AboutResponse = {
  title: string;
  agreementUrl?: string | null;
  apiUrl?: string | null;
  webAppUrl?: string | null;
  infoChannel: string;
  reviewsChannel: string;
  sections: AppSection[];
};

export type SupportResponse = {
  supportBotUrl: string;
  infoChannel: string;
  reviewsChannel: string;
};

export type FavoriteCodesResponse = {
  codes: string[];
};

export type ProfileClient = {
  workerId?: number | null;
  agreementAccepted: boolean;
  agreementId?: string | null;
  isBanned: boolean;
  cityStatus: number;
  firstCity?: string | null;
  secondCity?: string | null;
  orders: number;
  rating: number;
  promo?: string | null;
  promoAmount?: number | null;
  dateRegister?: string | null;
  addressSystemEnabled?: boolean;
  balance?: number;
};

export type ProfileAddressItem = {
  id: number;
  title: string;
  address: string;
  createdAt?: string | null;
};

export type ProfileResponse = {
  user: {
    telegramId: number;
    firstName: string;
    lastName?: string | null;
    username?: string | null;
    photoUrl?: string | null;
    isMock: boolean;
  };
  client: ProfileClient;
  addresses: ProfileAddressItem[];
};

export type ProfileCityResponse = {
  client: ProfileClient;
};

export type ProfilePromo = {
  code?: string | null;
  amount?: number | null;
  isActive: boolean;
};

export type ProfilePromoResponse = {
  promo: ProfilePromo;
  client?: ProfileClient;
};

export type ProfileAddressResponse = {
  addresses: ProfileAddressItem[];
};

export type ProfileOrderHistoryItem = {
  number: string;
  date?: string | null;
  modelInfo?: string | null;
  city?: string | null;
  status: string;
  tariffPlan?: string | null;
  promo?: string | null;
};

export type ProfileOrdersResponse = {
  items: ProfileOrderHistoryItem[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
};

export type ModelSummary = {
  code: string;
  name: string;
  cityStatus: number;
  age: number;
  height: number;
  tits: number;
  description?: string | null;
  prices: {
    oneHour?: number | null;
    twoHours?: number | null;
    threeHours?: number | null;
    night?: number | null;
  };
  flags: {
    verification: boolean;
    document: boolean;
    dynamic: boolean;
  };
  photoRefs: string[];
  photoUrls: string[];
  previewPhotoRef?: string | null;
  previewPhotoUrl?: string | null;
  orders: number;
  rating: number;
  reviewsCount: number;
};

export type ModelDetails = ModelSummary & {
  services: Array<{ id: number; name: string }>;
  additionals: Array<{ id: number; name: string; price: number }>;
  reviews: Array<{
    id: number;
    author?: string | null;
    reviewDate?: string | null;
    body?: string | null;
    score: number;
  }>;
};

export type BookingPrepareRequest = {
  meetingDate: string;
  meetingTime: string;
  meetingPlace: 'model' | 'client';
  tariff: '1h' | '2h' | '3h' | 'night';
  addressId?: number | null;
  additionals?: number[];
};

export type BookingPaymentMethodKey = 'card' | 'cash';

export type BookingPrepareResponse = {
  orderNumber: string;
  modelName: string;
  modelCode: string;
  amount: number;
  additionalSum: number;
  currency: string;
  tariff: {
    key: BookingPrepareRequest['tariff'];
    amount: number;
  };
  additionals: Array<{
    id: number;
    name: string;
    price: number;
  }>;
  paymentMethods: Array<{
    key: BookingPaymentMethodKey;
  }>;
};

export type BookingPaymentResponse = {
  orderNumber: string;
  modelName: string;
  modelCode: string;
  amount: number;
  currency: string;
  paymentMethod: BookingPaymentMethodKey;
  status: 'card_requisites' | 'manual_support' | 'cash_unavailable';
  card?: {
    cardNumber: string;
    holderName: string;
    bankName: string;
  } | null;
};
