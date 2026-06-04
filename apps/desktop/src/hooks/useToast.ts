import { create } from "zustand";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  add: (toast: Omit<Toast, "id">) => void;
  remove: (id: string) => void;
  clear: () => void;
}

let toastId = 0;

export const useToastStore = create<ToastStore>((set, get) => ({
  toasts: [],
  add: (toast) => {
    const id = `toast-${++toastId}`;
    const duration = toast.duration ?? 4000;
    set({ toasts: [...get().toasts, { ...toast, id }] });
    setTimeout(() => {
      get().remove(id);
    }, duration);
  },
  remove: (id) => {
    set({ toasts: get().toasts.filter((t) => t.id !== id) });
  },
  clear: () => set({ toasts: [] }),
}));

export function toast(type: ToastType, title: string, message?: string) {
  useToastStore.getState().add({ type, title, message });
}
