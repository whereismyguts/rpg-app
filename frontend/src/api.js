const BASE_URL = '/api';

class ApiClient {
  constructor() {
    this.playerUuid = null;
  }

  setPlayerUuid(uuid) {
    this.playerUuid = uuid;
  }

  async request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getConfig() {
    return this.request('/config');
  }

  async login(initData, playerUuid, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        init_data: initData,
        player_uuid: playerUuid,
        password: password,
      }),
    });
  }

  async getMe() {
    return this.request(`/users/me?player_uuid=${this.playerUuid}`);
  }

  async getStats() {
    return this.request(`/users/stats?player_uuid=${this.playerUuid}`);
  }

  async getQR(format = 'base64') {
    return this.request(`/users/qr?player_uuid=${this.playerUuid}&format=${format}`);
  }

  async lookupUser(uuid) {
    return this.request(`/users/lookup?player_uuid=${uuid}`);
  }

  async sendMoney(toUuid, amount) {
    return this.request('/transfer/send', {
      method: 'POST',
      body: JSON.stringify({
        from_uuid: this.playerUuid,
        to_uuid: toUuid,
        amount: amount,
      }),
    });
  }
}

export const api = new ApiClient();
