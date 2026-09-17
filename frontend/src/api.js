import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function api(path, options = {}) {
  return axios({ baseURL: API_URL, url: path, ...options }).then((response) => response.data);
}