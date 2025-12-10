import { create } from 'zustand';

interface ReviewState {
  // Synchronized scrolling
  syncScrolling: boolean;
  setSyncScrolling: (sync: boolean) => void;
  
  // Current scroll positions
  scrollPosition: number;
  setScrollPosition: (position: number) => void;
  
  // Highlighted block
  highlightedBlockId: string | null;
  setHighlightedBlockId: (blockId: string | null) => void;
  
  // Zoom level
  zoomLevel: number;
  setZoomLevel: (zoom: number) => void;
  
  // Current page
  currentPage: number;
  setCurrentPage: (page: number) => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  // Initial state
  syncScrolling: true,
  scrollPosition: 0,
  highlightedBlockId: null,
  zoomLevel: 1,
  currentPage: 1,
  
  // Actions
  setSyncScrolling: (sync) => set({ syncScrolling: sync }),
  setScrollPosition: (position) => set({ scrollPosition: position }),
  setHighlightedBlockId: (blockId) => set({ highlightedBlockId: blockId }),
  setZoomLevel: (zoom) => set({ zoomLevel: zoom }),
  setCurrentPage: (page) => set({ currentPage: page }),
}));

