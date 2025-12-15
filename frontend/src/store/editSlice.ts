import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface EditedBlock {
  originalText: string
  editedText: string
  editedAt: Date
}

interface EditState {
  // Map of block_id (string) to EditedBlock
  edits: Map<string, EditedBlock>
  
  // Actions
  setEdit: (blockId: string, originalText: string, editedText: string) => void
  clearEdit: (blockId: string) => void
  clearAllEdits: () => void
  getEdit: (blockId: string) => EditedBlock | undefined
  hasEdits: boolean
  getEditCount: () => number
}

// Helper to serialize/deserialize Map for persistence
const mapReplacer = (key: string, value: any) => {
  if (value instanceof Map) {
    return {
      dataType: 'Map',
      value: Array.from(value.entries()),
    }
  }
  return value
}

const mapReviver = (key: string, value: any) => {
  if (typeof value === 'object' && value !== null && value.dataType === 'Map') {
    return new Map(value.value)
  }
  return value
}

export const useEditStore = create<EditState>()(
  persist(
    (set, get) => ({
      edits: new Map<string, EditedBlock>(),

      setEdit: (blockId, originalText, editedText) => {
        set((state) => {
          const newEdits = new Map(state.edits)
          newEdits.set(blockId, {
            originalText,
            editedText,
            editedAt: new Date(),
          })
          return { edits: newEdits }
        })
      },

      clearEdit: (blockId) => {
        set((state) => {
          const newEdits = new Map(state.edits)
          newEdits.delete(blockId)
          return { edits: newEdits }
        })
      },

      clearAllEdits: () => {
        set({ edits: new Map() })
      },

      getEdit: (blockId) => {
        return get().edits.get(blockId)
      },

      get hasEdits() {
        return get().edits.size > 0
      },

      getEditCount: () => {
        return get().edits.size
      },
    }),
    {
      name: 'transkeep-edits',
      partialize: (state) => ({
        // Convert Map to array for persistence
        edits: Array.from(state.edits.entries()),
      }),
      // Custom storage to handle Map serialization
      storage: {
        getItem: (name: string) => {
          const str = localStorage.getItem(name)
          if (!str) return null
          try {
            const parsed = JSON.parse(str, mapReviver)
            // Convert array back to Map
            if (parsed.state?.edits && Array.isArray(parsed.state.edits)) {
              parsed.state.edits = new Map(parsed.state.edits)
            }
            return parsed
          } catch {
            return null
          }
        },
        setItem: (name: string, value: any) => {
          // Convert Map to array before storing
          const toStore = {
            ...value,
            state: {
              ...value.state,
              edits: value.state.edits instanceof Map 
                ? Array.from(value.state.edits.entries())
                : value.state.edits,
            },
          }
          localStorage.setItem(name, JSON.stringify(toStore, mapReplacer))
        },
        removeItem: (name: string) => localStorage.removeItem(name),
      },
    }
  )
)
