import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  id: string | null;
  name: string | null;
  email: string | null;
  token: string | null;
  isAuthenticated: boolean;
}

const initialState: UserState = {
  id: null,
  name: null,
  email: null,
  token: null,
  isAuthenticated: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<{
      id: string;
      name: string;
      email: string;
      token: string;
    }>) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
      state.email = action.payload.email;
      state.token = action.payload.token;
      state.isAuthenticated = true;
    },
    loginUser: (state, action: PayloadAction<{
      email: string;
      password: string;
    }>) => {
      // 模拟登录成功
      state.id = '1';
      state.name = '用户';
      state.email = action.payload.email;
      state.token = 'mock-token';
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.id = null;
      state.name = null;
      state.email = null;
      state.token = null;
      state.isAuthenticated = false;
    },
  },
});

export const { setUser, loginUser, logout } = userSlice.actions;
export default userSlice.reducer;