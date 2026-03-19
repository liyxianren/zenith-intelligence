import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface Problem {
  id: string;
  content: string;
  type: 'text' | 'image';
  solution: string;
  timestamp: number;
}

interface ProblemState {
  problems: Problem[];
  currentProblem: Problem | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ProblemState = {
  problems: [],
  currentProblem: null,
  isLoading: false,
  error: null,
};

const problemSlice = createSlice({
  name: 'problem',
  initialState,
  reducers: {
    setProblems: (state, action: PayloadAction<Problem[]>) => {
      state.problems = action.payload;
    },
    addProblem: (state, action: PayloadAction<Problem>) => {
      state.problems.unshift(action.payload);
    },
    setCurrentProblem: (state, action: PayloadAction<Problem>) => {
      state.currentProblem = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setProblems, addProblem, setCurrentProblem, setLoading, setError } = problemSlice.actions;
export default problemSlice.reducer;