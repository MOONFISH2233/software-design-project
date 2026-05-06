import { create } from 'zustand';

export const useUserStore = create((set) => ({
  user: null,
  token: localStorage.getItem('authToken') || '',
  
  setUser: (user) => set({ user }),
  
  setToken: (token) => {
    localStorage.setItem('authToken', token);
    set({ token });
  },
  
  logout: () => {
    localStorage.removeItem('authToken');
    set({ user: null, token: '' });
  },
}));
