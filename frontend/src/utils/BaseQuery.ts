import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { RootState } from "../store";
import { jwtDecode } from "jwt-decode";
import type {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
} from "@reduxjs/toolkit/query";
import { logout } from "../features/auth/authSlice";
import { TokenType } from "../types";

const getBaseUrl = (): string => {
  const hostname = window.location.hostname;
  const subdomain = hostname.split(".")[0]; // assuming your site is at tenantone.example.com
  const baseUrl = `http://${subdomain}.example.com:8000/`;
  return baseUrl;
};

const isTokenExpired = (token: string | undefined): boolean => {
  try {
    if (!token) {
      return true;
    }

    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    // Assuming ACCESS_TOKEN_LIFETIME is in seconds
    const tokenLifetime = 20; // in 20 seconds, also for minute  4 * 60,  4 minutes in seconds

    // Calculate the refresh threshold based on token lifetime
    const refreshThreshold = decoded.exp - tokenLifetime;

    // Check if token is expired or needs refresh
    return currentTime >= refreshThreshold;
  } catch (error) {
    return true;
  }
};

// Custom base query with token management
const baseQuery = fetchBaseQuery({
  baseUrl: getBaseUrl(),
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;
    const tokens = state.auth.userTokens;
    if (tokens) {
      headers.set("authorization", `Bearer ${tokens.access}`);
    }
    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);
  const tokens = JSON.parse(
    localStorage.getItem("userTokens") || "null"
  ) as TokenType | null;

  if (
    (result.error && result.error.status === 401) ||
    isTokenExpired(tokens?.access)
  ) {
    const refreshResult = await baseQuery(
      {
        url: "users/token/refresh/",
        method: "POST",
        body: { refresh: tokens?.refresh },
      },
      api,
      extraOptions
    );

    if (refreshResult.data) {
      const newToken = refreshResult.data;
      localStorage.setItem("userTokens", JSON.stringify(newToken));

      result = await baseQuery(args, api, extraOptions);
    } else {
      // Handle token refresh failure
      api.dispatch(logout());
    }
  }

  return result;
};
