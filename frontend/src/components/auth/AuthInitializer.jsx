import { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from 'store/hooks';
import { fetchUser } from 'store/userSlice';

/**
 * Component that initializes authentication on app load
 * Checks for existing token and fetches user data if token exists
 */
export default function AuthInitializer({ children }) {
  const dispatch = useAppDispatch();
  const { token, user, isLoading } = useAppSelector((state) => state.user);
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Only run once on mount
    if (hasInitialized.current) return;
    
    // If we have a token but no user data, fetch user data
    const storedToken = localStorage.getItem('authToken');
    if (storedToken && !user && !isLoading) {
      hasInitialized.current = true;
      dispatch(fetchUser());
    }
  }, [dispatch, token, user, isLoading]);

  return children;
}

