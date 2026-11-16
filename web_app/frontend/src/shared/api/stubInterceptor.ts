import { getMockTelegramUser } from '@/shared/mocks/mockTelegram';
import type {
  AboutResponse,
  BookingPaymentMethodKey,
  BookingPaymentResponse,
  BookingPrepareRequest,
  BookingPrepareResponse,
  FavoriteCodesResponse,
  ModelDetails,
  ProfileAddressItem,
  ProfileAddressResponse,
  ProfileCityResponse,
  ProfileClient,
  ProfileOrderHistoryItem,
  ProfileOrdersResponse,
  ProfilePromoResponse,
  ProfileResponse,
  SupportResponse,
  WebAppSessionResponse,
} from '@/shared/types/web-app';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

type RequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  token?: string | null;
};

type StubState = {
  session: WebAppSessionResponse;
  about: AboutResponse;
  support: SupportResponse;
  profile: ProfileResponse;
  favorites: string[];
  orders: ProfileOrderHistoryItem[];
  models: ModelDetails[];
  preparedBookings: Record<string, BookingPrepareResponse>;
  nextAddressId: number;
};

const STUB_STORAGE_KEY = 'escort_v1_web_app.stub_state.v1';

function isoDate(offsetDays = 0) {
  return new Date(Date.now() + (offsetDays * 24 * 60 * 60 * 1000)).toISOString();
}

function createProfileClient(overrides: Partial<ProfileClient> = {}): ProfileClient {
  return {
    workerId: 112233,
    agreementAccepted: true,
    agreementId: 'stub-agreement-1',
    isBanned: false,
    cityStatus: 1,
    firstCity: 'Москва',
    secondCity: 'Санкт-Петербург',
    orders: 3,
    rating: 4.9,
    promo: null,
    promoAmount: null,
    dateRegister: isoDate(-45),
    addressSystemEnabled: true,
    balance: 0,
    ...overrides,
  };
}

function createStubModels(): ModelDetails[] {
  return [
    {
      code: 'eva-amber',
      name: 'Eva Amber',
      cityStatus: 1,
      age: 22,
      height: 168,
      tits: 3,
      description: 'Яркая модель для вечерних встреч и комфортного отдыха.',
      prices: {
        oneHour: 18000,
        twoHours: 32000,
        threeHours: 46000,
        night: 120000,
      },
      flags: {
        verification: true,
        document: true,
        dynamic: true,
      },
      previewPhotoRef: null,
      previewPhotoUrl: null,
      photoRefs: [],
      photoUrls: [],
      orders: 124,
      rating: 4.9,
      reviewsCount: 2,
      services: [
        { id: 1, name: 'Классический отдых' },
        { id: 2, name: 'Романтическая встреча' },
      ],
      additionals: [
        { id: 101, name: 'Выезд за МКАД', price: 5000 },
        { id: 102, name: 'Премиум бельё', price: 3000 },
      ],
      reviews: [
        { id: 1, author: 'Алексей', reviewDate: isoDate(-10), body: 'Очень приятная и внимательная.', score: 5 },
        { id: 2, author: 'Максим', reviewDate: isoDate(-4), body: 'Все как договаривались.', score: 5 },
      ],
    },
    {
      code: 'luna-velvet',
      name: 'Luna Velvet',
      cityStatus: 1,
      age: 24,
      height: 171,
      tits: 2,
      description: 'Спокойный формат, хорошее общение и мягкая атмосфера.',
      prices: {
        oneHour: 16000,
        twoHours: 29000,
        threeHours: 42000,
        night: 110000,
      },
      flags: {
        verification: true,
        document: false,
        dynamic: false,
      },
      previewPhotoRef: null,
      previewPhotoUrl: null,
      photoRefs: [],
      photoUrls: [],
      orders: 98,
      rating: 4.8,
      reviewsCount: 1,
      services: [
        { id: 3, name: 'Отдых в отеле' },
        { id: 4, name: 'Сопровождение' },
      ],
      additionals: [
        { id: 103, name: 'Продление 30 мин', price: 4000 },
      ],
      reviews: [
        { id: 3, author: 'Игорь', reviewDate: isoDate(-7), body: 'Комфортно и без суеты.', score: 5 },
      ],
    },
    {
      code: 'mia-storm',
      name: 'Mia Storm',
      cityStatus: 2,
      age: 23,
      height: 167,
      tits: 3,
      description: 'Энергичная, стильная, отлично подходит для длинных встреч.',
      prices: {
        oneHour: 17000,
        twoHours: 31000,
        threeHours: 45000,
        night: 115000,
      },
      flags: {
        verification: true,
        document: true,
        dynamic: true,
      },
      previewPhotoRef: null,
      previewPhotoUrl: null,
      photoRefs: [],
      photoUrls: [],
      orders: 140,
      rating: 5,
      reviewsCount: 1,
      services: [
        { id: 5, name: 'Ужин и сопровождение' },
      ],
      additionals: [
        { id: 104, name: 'Такси по городу', price: 2500 },
        { id: 105, name: 'Поздний выезд', price: 4500 },
      ],
      reviews: [
        { id: 4, author: 'Роман', reviewDate: isoDate(-2), body: 'Очень сильная анкета.', score: 5 },
      ],
    },
  ];
}

function createDefaultState(): StubState {
  const mockUser = getMockTelegramUser();
  const client = createProfileClient();
  const addresses: ProfileAddressItem[] = [
    { id: 1, title: 'Дом', address: 'Москва, Пресненская набережная, 8', createdAt: isoDate(-20) },
    { id: 2, title: 'Апартаменты', address: 'Москва, 1-я Тверская-Ямская, 7', createdAt: isoDate(-8) },
  ];
  const orders: ProfileOrderHistoryItem[] = [
    {
      number: 'STUB-24001',
      date: isoDate(-14),
      modelInfo: 'Eva Amber',
      city: 'Москва',
      status: 'paid',
      tariffPlan: '2 часа',
      promo: null,
    },
    {
      number: 'STUB-24002',
      date: isoDate(-9),
      modelInfo: 'Luna Velvet',
      city: 'Москва',
      status: 'completed',
      tariffPlan: '1 час',
      promo: 'WELCOME10',
    },
    {
      number: 'STUB-24003',
      date: isoDate(-3),
      modelInfo: 'Mia Storm',
      city: 'Санкт-Петербург',
      status: 'new',
      tariffPlan: 'Ночь',
      promo: null,
    },
  ];

  return {
    session: {
      sessionToken: 'stub-session-token',
      expiresAt: isoDate(30),
      user: {
        telegramId: mockUser.id,
        firstName: mockUser.first_name,
        lastName: mockUser.last_name ?? null,
        username: mockUser.username ?? null,
        photoUrl: mockUser.photo_url ?? null,
      },
      client: {
        workerId: client.workerId,
        agreementAccepted: client.agreementAccepted,
        isBanned: client.isBanned,
      },
      environment: {
        telegram: false,
        mock: true,
      },
    },
    about: {
      title: 'Escort Web App Stub',
      agreementUrl: 'https://t.me/escort_stub_bot',
      apiUrl: 'stub://local',
      webAppUrl: 'stub://local/webapp',
      infoChannel: 'https://t.me/escort_info',
      reviewsChannel: 'https://t.me/escort_reviews',
      sections: ['about', 'models', 'support', 'profile'],
    },
    support: {
      supportBotUrl: 'https://t.me/escort_support_bot',
      infoChannel: 'https://t.me/escort_info',
      reviewsChannel: 'https://t.me/escort_reviews',
    },
    profile: {
      user: {
        telegramId: mockUser.id,
        firstName: mockUser.first_name,
        lastName: mockUser.last_name ?? null,
        username: mockUser.username ?? null,
        photoUrl: mockUser.photo_url ?? null,
        isMock: true,
      },
      client: {
        ...client,
        orders: orders.length,
      },
      addresses,
    },
    favorites: ['eva-amber'],
    orders,
    models: createStubModels(),
    preparedBookings: {},
    nextAddressId: 3,
  };
}

function getState(): StubState {
  if (typeof window === 'undefined') {
    return createDefaultState();
  }

  const rawState = window.localStorage.getItem(STUB_STORAGE_KEY);
  if (!rawState) {
    const nextState = createDefaultState();
    window.localStorage.setItem(STUB_STORAGE_KEY, JSON.stringify(nextState));
    return nextState;
  }

  try {
    return JSON.parse(rawState) as StubState;
  } catch {
    const nextState = createDefaultState();
    window.localStorage.setItem(STUB_STORAGE_KEY, JSON.stringify(nextState));
    return nextState;
  }
}

function saveState(state: StubState) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(STUB_STORAGE_KEY, JSON.stringify(state));
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function getPathname(path: string) {
  return new URL(path, 'https://stub.local').pathname;
}

function getSearchParams(path: string) {
  return new URL(path, 'https://stub.local').searchParams;
}

function parseRouteParams(pathname: string, pattern: RegExp) {
  return pathname.match(pattern);
}

function buildProfileCityResponse(state: StubState): ProfileCityResponse {
  return {
    client: clone(state.profile.client),
  };
}

function buildProfileAddressResponse(state: StubState): ProfileAddressResponse {
  return {
    addresses: clone(state.profile.addresses),
  };
}

function buildProfilePromoResponse(state: StubState): ProfilePromoResponse {
  return {
    promo: {
      code: state.profile.client.promo ?? null,
      amount: state.profile.client.promoAmount ?? null,
      isActive: Boolean(state.profile.client.promo),
    },
    client: clone(state.profile.client),
  };
}

function buildFavoritesResponse(state: StubState): FavoriteCodesResponse {
  return {
    codes: [...state.favorites],
  };
}

function paginateOrders(items: ProfileOrderHistoryItem[], page: number, pageSize: number): ProfileOrdersResponse {
  const startIndex = (page - 1) * pageSize;
  const pagedItems = items.slice(startIndex, startIndex + pageSize);
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return {
    items: clone(pagedItems),
    pagination: {
      page,
      pageSize,
      total,
      totalPages,
    },
  };
}

function getActiveCityStatus(state: StubState) {
  return Math.max(1, state.profile.client.cityStatus || 1);
}

function getTariffAmount(model: ModelDetails, tariff: BookingPrepareRequest['tariff']) {
  if (tariff === '1h') {
    return model.prices.oneHour ?? 0;
  }
  if (tariff === '2h') {
    return model.prices.twoHours ?? 0;
  }
  if (tariff === '3h') {
    return model.prices.threeHours ?? 0;
  }
  return model.prices.night ?? 0;
}

function buildPreparedBooking(
  model: ModelDetails,
  body: BookingPrepareRequest,
): BookingPrepareResponse {
  const tariffAmount = getTariffAmount(model, body.tariff);
  const additionals = model.additionals.filter((item) => body.additionals?.includes(item.id));
  const additionalSum = additionals.reduce((sum, item) => sum + item.price, 0);
  const orderNumber = `STUB-${Date.now()}`;

  return {
    orderNumber,
    modelName: model.name,
    modelCode: model.code,
    amount: tariffAmount + additionalSum,
    additionalSum,
    currency: 'RUB',
    tariff: {
      key: body.tariff,
      amount: tariffAmount,
    },
    additionals,
    paymentMethods: [
      { key: 'card' },
      { key: 'cash' },
    ],
  };
}

function assertToken(options: RequestOptions) {
  if (!options.token) {
    throw new Error('STUB_AUTH_REQUIRED');
  }
}

export async function interceptStubRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = options.method ?? 'GET';
  const pathname = getPathname(path);
  const searchParams = getSearchParams(path);
  const state = getState();

  if (pathname === '/web-app/api/v1/auth/session' && method === 'POST') {
    const body = (options.body ?? {}) as { mockUser?: { id?: number; first_name?: string; last_name?: string; username?: string; photo_url?: string }; initData?: string };
    const incomingUser = body.mockUser;

    if (incomingUser?.id) {
      state.session.user.telegramId = incomingUser.id;
      state.session.user.firstName = incomingUser.first_name ?? state.session.user.firstName;
      state.session.user.lastName = incomingUser.last_name ?? null;
      state.session.user.username = incomingUser.username ?? null;
      state.session.user.photoUrl = incomingUser.photo_url ?? null;
      state.profile.user.telegramId = incomingUser.id;
      state.profile.user.firstName = incomingUser.first_name ?? state.profile.user.firstName;
      state.profile.user.lastName = incomingUser.last_name ?? null;
      state.profile.user.username = incomingUser.username ?? null;
      state.profile.user.photoUrl = incomingUser.photo_url ?? null;
    }

    state.session.environment.telegram = Boolean(body.initData);
    state.session.environment.mock = !body.initData;
    saveState(state);
    return clone(state.session) as T;
  }

  if (pathname === '/web-app/api/v1/about' && method === 'GET') {
    assertToken(options);
    return clone(state.about) as T;
  }

  if (pathname === '/web-app/api/v1/support' && method === 'GET') {
    assertToken(options);
    return clone(state.support) as T;
  }

  if (pathname === '/web-app/api/v1/profile' && method === 'GET') {
    assertToken(options);
    return clone(state.profile) as T;
  }

  if (pathname === '/web-app/api/v1/profile/city' && method === 'PUT') {
    assertToken(options);
    const body = (options.body ?? {}) as { cityName?: string; slot?: number };
    const cityName = String(body.cityName ?? '').trim();
    const slot = body.slot === 2 ? 2 : 1;

    if (!cityName) {
      throw new Error('Город не найден');
    }

    if (slot === 2) {
      state.profile.client.secondCity = cityName;
    } else {
      state.profile.client.firstCity = cityName;
    }
    state.profile.client.cityStatus = slot;

    saveState(state);
    return buildProfileCityResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/profile/city-status' && method === 'PUT') {
    assertToken(options);
    const body = (options.body ?? {}) as { cityStatus?: number };
    state.profile.client.cityStatus = body.cityStatus === 2 ? 2 : 1;
    saveState(state);
    return buildProfileCityResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/profile/address' && method === 'PUT') {
    assertToken(options);
    const body = (options.body ?? {}) as { title?: string; address?: string };
    const title = String(body.title ?? '').trim();
    const address = String(body.address ?? '').trim();

    if (!title || !address) {
      throw new Error('Заполните адрес');
    }

    state.profile.addresses = [
      {
        id: state.nextAddressId,
        title,
        address,
        createdAt: new Date().toISOString(),
      },
      ...state.profile.addresses,
    ];
    state.nextAddressId += 1;
    saveState(state);
    return buildProfileAddressResponse(state) as T;
  }

  const deleteAddressMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/profile\/address\/(\d+)$/);
  if (deleteAddressMatch && method === 'DELETE') {
    assertToken(options);
    const addressId = Number(deleteAddressMatch[1]);
    state.profile.addresses = state.profile.addresses.filter((item) => item.id !== addressId);
    saveState(state);
    return buildProfileAddressResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/profile/promo' && method === 'GET') {
    assertToken(options);
    return buildProfilePromoResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/profile/promo' && method === 'PUT') {
    assertToken(options);
    const body = (options.body ?? {}) as { code?: string };
    const promoCode = String(body.code ?? '').trim().toUpperCase();
    const promoCatalog: Record<string, number> = {
      WELCOME10: 10,
      VIP25: 25,
    };

    if (!promoCatalog[promoCode]) {
      throw new Error('Промокод не найден');
    }

    state.profile.client.promo = promoCode;
    state.profile.client.promoAmount = promoCatalog[promoCode];
    saveState(state);
    return buildProfilePromoResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/profile/orders' && method === 'GET') {
    assertToken(options);
    const page = Math.max(1, Number(searchParams.get('page') ?? '1'));
    const pageSize = Math.max(1, Number(searchParams.get('pageSize') ?? '100'));
    return paginateOrders(state.orders, page, pageSize) as T;
  }

  if (pathname === '/web-app/api/v1/favorites' && method === 'GET') {
    assertToken(options);
    return buildFavoritesResponse(state) as T;
  }

  const favoriteMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/favorites\/([^/]+)$/);
  if (favoriteMatch && method === 'PUT') {
    assertToken(options);
    const code = decodeURIComponent(favoriteMatch[1]);
    if (!state.favorites.includes(code)) {
      state.favorites.push(code);
      saveState(state);
    }
    return buildFavoritesResponse(state) as T;
  }

  if (favoriteMatch && method === 'DELETE') {
    assertToken(options);
    const code = decodeURIComponent(favoriteMatch[1]);
    state.favorites = state.favorites.filter((item) => item !== code);
    saveState(state);
    return buildFavoritesResponse(state) as T;
  }

  if (pathname === '/web-app/api/v1/models' && method === 'GET') {
    assertToken(options);
    const activeCityStatus = getActiveCityStatus(state);
    const items = state.models.filter((item) => item.cityStatus === activeCityStatus);
    return {
      items: clone(items),
    } as T;
  }

  const prepareBookingMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/models\/([^/]+)\/booking\/prepare$/);
  if (prepareBookingMatch && method === 'POST') {
    assertToken(options);
    const code = decodeURIComponent(prepareBookingMatch[1]);
    const model = state.models.find((item) => item.code === code);
    const body = (options.body ?? {}) as BookingPrepareRequest;

    if (!model) {
      throw new Error('Модель не найдена');
    }

    if (body.meetingPlace === 'client' && !body.addressId) {
      throw new Error('Нужно выбрать адрес');
    }

    const preparedBooking = buildPreparedBooking(model, body);
    state.preparedBookings[preparedBooking.orderNumber] = preparedBooking;
    saveState(state);
    return clone(preparedBooking) as T;
  }

  const markOpenedMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/models\/([^/]+)\/opened$/);
  if (markOpenedMatch && method === 'POST') {
    assertToken(options);
    const code = decodeURIComponent(markOpenedMatch[1]);
    const model = state.models.find((item) => item.code === code);

    if (!model) {
      throw new Error('Модель не найдена');
    }

    return {
      ok: true,
    } as T;
  }

  const modelMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/models\/([^/]+)$/);
  if (modelMatch && method === 'GET') {
    assertToken(options);
    const code = decodeURIComponent(modelMatch[1]);
    const model = state.models.find((item) => item.code === code);

    if (!model) {
      throw new Error('Модель не найдена');
    }

    return clone(model) as T;
  }

  const bookingPaymentMatch = parseRouteParams(pathname, /^\/web-app\/api\/v1\/bookings\/([^/]+)\/payment$/);
  if (bookingPaymentMatch && method === 'POST') {
    assertToken(options);
    const orderNumber = decodeURIComponent(bookingPaymentMatch[1]);
    const preparedBooking = state.preparedBookings[orderNumber];
    const body = (options.body ?? {}) as { paymentMethod?: BookingPaymentMethodKey };
    const paymentMethod = body.paymentMethod ?? 'card';

    if (!preparedBooking) {
      throw new Error('Бронирование не найдено');
    }

    const response: BookingPaymentResponse = {
      orderNumber: preparedBooking.orderNumber,
      modelName: preparedBooking.modelName,
      modelCode: preparedBooking.modelCode,
      amount: preparedBooking.amount,
      currency: preparedBooking.currency,
      paymentMethod,
      status: paymentMethod === 'card' ? 'card_requisites' : 'manual_support',
      card: paymentMethod === 'card'
        ? {
            cardNumber: '2200 7001 1234 5678',
            holderName: 'Escort Web App',
            bankName: 'T-Bank',
          }
        : null,
    };

    return response as T;
  }

  throw new Error(`STUB_NOT_IMPLEMENTED: ${method} ${pathname}`);
}
