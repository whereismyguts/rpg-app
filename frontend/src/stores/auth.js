import { writable } from 'svelte/store';

function createAuthStore() {
  const { subscribe, set, update } = writable({
    isAuthenticated: false,
    playerUuid: null,
    name: null,
    balance: 0,
    hp: 100,
  });

  return {
    subscribe,
    login: (userData) => {
      set({
        isAuthenticated: true,
        playerUuid: userData.player_uuid,
        name: userData.name,
        balance: userData.balance,
        hp: userData.hp ?? 100,
      });
      localStorage.setItem('rpg_player_uuid', userData.player_uuid);
    },
    logout: () => {
      set({
        isAuthenticated: false,
        playerUuid: null,
        name: null,
        balance: 0,
        hp: 100,
      });
      localStorage.removeItem('rpg_player_uuid');
    },
    updateBalance: (newBalance) => {
      update(state => ({ ...state, balance: newBalance }));
    },
    updateHp: (newHp) => {
      update(state => ({ ...state, hp: newHp }));
    },
    restore: () => {
      const uuid = localStorage.getItem('rpg_player_uuid');
      if (uuid) {
        return uuid;
      }
      return null;
    }
  };
}

export const auth = createAuthStore();
