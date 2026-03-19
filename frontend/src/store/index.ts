import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slices/userSlice';
import problemReducer from './slices/problemSlice';
import courseReducer from './slices/courseSlice';
import statsReducer from './slices/statsSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
    problem: problemReducer,
    course: courseReducer,
    stats: statsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
