import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  name: string | null
  picture_url: string | null
  subscription_tier: string
  created_at: string
}

export interface Job {
  job_id: string
  status: 'pending' | 'extracting' | 'translating' | 'applying_tone' | 'reconstructing' | 'completed' | 'failed'
  progress: number
  filename?: string
  source_language?: string
  target_language?: string
  current_page?: number
  total_pages?: number
  error?: string
  created_at?: string
}

interface AppState {
  user: User | null
  isAuthenticated: boolean
  token: string | null
  currentJob: Job | null
  reviewPanelSync: boolean

  setUser: (user: User | null) => void
  setAuthenticated: (isAuthenticated: boolean) => void
  setToken: (token: string | null) => void
  setCurrentJob: (job: Job | null) => void
  updateJobProgress: (progress: number, status?: Job['status']) => void
  toggleSync: () => void
  reset: () => void
}

const initialState = {
  user: null,
  isAuthenticated: false,
  token: null,
  currentJob: null,
  reviewPanelSync: true,
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        setUser: (user) =>
          set({ user, isAuthenticated: !!user }, undefined, 'setUser'),

        setAuthenticated: (isAuthenticated) =>
          set({ isAuthenticated }, undefined, 'setAuthenticated'),

        setToken: (token) =>
          set({ token }, undefined, 'setToken'),

        setCurrentJob: (currentJob) =>
          set({ currentJob }, undefined, 'setCurrentJob'),

        updateJobProgress: (progress, status) =>
          set(
            (state) => ({
              currentJob: state.currentJob
                ? { ...state.currentJob, progress, ...(status && { status }) }
                : null,
            }),
            undefined,
            'updateJobProgress'
          ),

        toggleSync: () =>
          set(
            (state) => ({ reviewPanelSync: !state.reviewPanelSync }),
            undefined,
            'toggleSync'
          ),

        reset: () => set(initialState, undefined, 'reset'),
      }),
      {
        name: 'transkeep-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          token: state.token,
          reviewPanelSync: state.reviewPanelSync,
        }),
      }
    ),
    { name: 'TransKeep' }
  )
)
