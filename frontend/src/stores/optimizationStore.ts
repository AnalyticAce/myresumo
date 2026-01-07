import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { OptimizationState, OptimizationRequest } from '@/types/optimization'

interface OptimizationStore extends OptimizationState {
  // Actions
  setCurrentStep: (step: 1 | 2 | 3 | 4) => void
  setRequest: (request: Partial<OptimizationRequest>) => void
  setAnalysis: (analysis: OptimizationState['analysis']) => void
  setResult: (result: OptimizationState['result']) => void
  setProcessing: (isProcessing: boolean) => void
  setError: (error: string | undefined) => void
  reset: () => void
}

const initialState: OptimizationState = {
  step: 1,
  request: {},
  isProcessing: false,
}

export const useOptimizationStore = create<OptimizationStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setCurrentStep: (step) => set({ step }),

      setRequest: (newRequest) => 
        set({ request: { ...get().request, ...newRequest } }),

      setAnalysis: (analysis) => set({ analysis }),

      setResult: (result) => set({ result }),

      setProcessing: (isProcessing) => set({ isProcessing }),

      setError: (error) => set({ error }),

      reset: () => set(initialState),
    }),
    {
      name: 'optimization-store',
    }
  )
)
