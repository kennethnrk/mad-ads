import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { loginUser, registerUser, getCurrentUser, logoutUser as apiLogoutUser } from '../services/api';

// Async thunks
export const login = createAsyncThunk(
  'user/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await loginUser(credentials);
      // After login, fetch user data
      const userData = await getCurrentUser();
      return { token: response.access_token, user: userData };
    } catch (error) {
      return rejectWithValue(error.message || 'Login failed');
    }
  }
);

export const register = createAsyncThunk(
  'user/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await registerUser(userData);
      // After registration, automatically login
      const loginResponse = await loginUser({
        email: userData.email,
        password: userData.password,
      });
      const currentUser = await getCurrentUser();
      return { token: loginResponse.access_token, user: currentUser };
    } catch (error) {
      return rejectWithValue(error.message || 'Registration failed');
    }
  }
);

export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (_, { rejectWithValue }) => {
    try {
      const userData = await getCurrentUser();
      return userData;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch user');
    }
  }
);

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('authToken') || null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// User slice
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    logout: (state) => {
      apiLogoutUser();
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      });

    // Register
    builder
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      });

    // Fetch user
    builder
      .addCase(fetchUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
        state.token = null;
        // Clear invalid token
        localStorage.removeItem('authToken');
      });
  },
});

export const { logout, clearError } = userSlice.actions;
export default userSlice.reducer;

