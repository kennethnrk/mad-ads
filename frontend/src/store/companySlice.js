import { createSlice } from '@reduxjs/toolkit';

// Initial state
const initialState = {
  company_id: null,
};

// Company slice
const companySlice = createSlice({
  name: 'company',
  initialState,
  reducers: {
    setCompanyId: (state, action) => {
      state.company_id = action.payload;
    },
    clearCompanyId: (state) => {
      state.company_id = null;
    },
  },
});

export const { setCompanyId, clearCompanyId } = companySlice.actions;
export default companySlice.reducer;

