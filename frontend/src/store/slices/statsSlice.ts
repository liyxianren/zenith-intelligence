import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface StatsData {
  totalProblems: number;
  solvedProblems: number;
  learningTime: number;
  accuracy: number;
  weeklyProgress: {
    day: string;
    problems: number;
  }[];
}

interface StatsState {
  stats: StatsData | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: StatsState = {
  stats: null,
  isLoading: false,
  error: null,
};

const statsSlice = createSlice({
  name: 'stats',
  initialState,
  reducers: {
    setStats: (state, action: PayloadAction<StatsData>) => {
      state.stats = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setStats, setLoading, setError } = statsSlice.actions;
export default statsSlice.reducer;