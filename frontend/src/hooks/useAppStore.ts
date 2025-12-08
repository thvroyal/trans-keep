import { useAppStore as useStore } from '@/store/appStore'
import type { User, Job } from '@/store/appStore'

export type { User, Job }

export function useAppStore() {
  return useStore()
}

export function useUser() {
  return useStore((state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    setUser: state.setUser,
  }))
}

export function useCurrentJob() {
  return useStore((state) => ({
    currentJob: state.currentJob,
    setCurrentJob: state.setCurrentJob,
    updateJobProgress: state.updateJobProgress,
  }))
}

export function useReviewSync() {
  return useStore((state) => ({
    syncEnabled: state.reviewPanelSync,
    toggleSync: state.toggleSync,
  }))
}
