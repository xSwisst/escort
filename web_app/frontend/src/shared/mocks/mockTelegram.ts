export type MockTelegramUser = {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
};

const defaultMockUser: MockTelegramUser = {
  id: 8519809593,
  first_name: 'Escort',
  last_name: 'Browser',
  username: 'escort_browser',
  photo_url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=256&q=80',
};

export function getMockTelegramUser(): MockTelegramUser {
  return defaultMockUser;
}
