import { create } from 'zustand';
import type { UIState } from '../types';

interface UIStore extends UIState {
  toggleProfileModal: () => void;
  setActiveNavItem: (item: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  profileModalOpen: false,
  activeNavItem: 'reports',

  toggleProfileModal: () => {
    set((state) => ({ 
      profileModalOpen: !state.profileModalOpen 
    }));
  },

  setActiveNavItem: (item: string) => {
    set({ activeNavItem: item });
  },
}));
