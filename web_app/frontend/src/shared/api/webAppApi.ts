import { apiRequest } from '@/shared/api/client';
import { getMockTelegramUser } from '@/shared/mocks/mockTelegram';
import type {
  AboutResponse,
  BookingPaymentMethodKey,
  BookingPaymentResponse,
  BookingPrepareRequest,
  BookingPrepareResponse,
  FavoriteCodesResponse,
  ModelDetails,
  ModelSummary,
  ProfileAddressResponse,
  ProfileCityResponse,
  ProfileOrdersResponse,
  ProfilePromoResponse,
  ProfileResponse,
  SupportResponse,
  WebAppSessionResponse,
} from '@/shared/types/web-app';

export function createMockSession(): Promise<WebAppSessionResponse> {
  return apiRequest<WebAppSessionResponse>('/web-app/api/v1/auth/session', {
    method: 'POST',
    body: {
      mockUser: getMockTelegramUser(),
    },
  });
}

export function createTelegramSession(initData: string): Promise<WebAppSessionResponse> {
  return apiRequest<WebAppSessionResponse>('/web-app/api/v1/auth/session', {
    method: 'POST',
    body: {
      initData,
    },
  });
}

export function getAbout(token: string) {
  return apiRequest<AboutResponse>('/web-app/api/v1/about', { token });
}

export function getSupport(token: string) {
  return apiRequest<SupportResponse>('/web-app/api/v1/support', { token });
}

export function getProfile(token: string) {
  return apiRequest<ProfileResponse>('/web-app/api/v1/profile', { token });
}

export function setProfileCity(token: string, cityName: string, slot?: number) {
  return apiRequest<ProfileCityResponse>('/web-app/api/v1/profile/city', {
    method: 'PUT',
    token,
    body: {
      cityName,
      slot,
    },
  });
}

export function setProfileCityStatus(token: string, cityStatus: number) {
  return apiRequest<ProfileCityResponse>('/web-app/api/v1/profile/city-status', {
    method: 'PUT',
    token,
    body: {
      cityStatus,
    },
  });
}

export function addProfileAddress(token: string, title: string, address: string) {
  return apiRequest<ProfileAddressResponse>('/web-app/api/v1/profile/address', {
    method: 'PUT',
    token,
    body: {
      title,
      address,
    },
  });
}

export function deleteProfileAddress(token: string, addressId: number) {
  return apiRequest<ProfileAddressResponse>(`/web-app/api/v1/profile/address/${addressId}`, {
    method: 'DELETE',
    token,
  });
}

export function getProfilePromo(token: string) {
  return apiRequest<ProfilePromoResponse>('/web-app/api/v1/profile/promo', { token });
}

export function activateProfilePromo(token: string, code: string) {
  return apiRequest<ProfilePromoResponse>('/web-app/api/v1/profile/promo', {
    method: 'PUT',
    token,
    body: {
      code,
    },
  });
}

export function getProfileOrders(token: string, page = 1, pageSize = 100) {
  const searchParams = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
  });

  return apiRequest<ProfileOrdersResponse>(`/web-app/api/v1/profile/orders?${searchParams.toString()}`, { token });
}

export function getFavorites(token: string) {
  return apiRequest<FavoriteCodesResponse>('/web-app/api/v1/favorites', { token });
}

export function addFavorite(token: string, code: string) {
  return apiRequest<FavoriteCodesResponse>(`/web-app/api/v1/favorites/${code}`, {
    method: 'PUT',
    token,
  });
}

export function removeFavorite(token: string, code: string) {
  return apiRequest<FavoriteCodesResponse>(`/web-app/api/v1/favorites/${code}`, {
    method: 'DELETE',
    token,
  });
}

export async function getModels(token: string) {
  return apiRequest<{ items: ModelSummary[] }>('/web-app/api/v1/models', { token });
}

export function getModel(token: string, code: string) {
  return apiRequest<ModelDetails>(`/web-app/api/v1/models/${code}`, { token });
}

export function markModelOpened(token: string, code: string) {
  return apiRequest<{ ok: boolean }>(`/web-app/api/v1/models/${code}/opened`, {
    method: 'POST',
    token,
  });
}

export function prepareModelBooking(token: string, code: string, body: BookingPrepareRequest) {
  return apiRequest<BookingPrepareResponse>(`/web-app/api/v1/models/${code}/booking/prepare`, {
    method: 'POST',
    token,
    body,
  });
}

export function resolveModelBookingPayment(token: string, orderNumber: string, paymentMethod: BookingPaymentMethodKey) {
  return apiRequest<BookingPaymentResponse>(`/web-app/api/v1/bookings/${orderNumber}/payment`, {
    method: 'POST',
    token,
    body: {
      paymentMethod,
    },
  });
}
