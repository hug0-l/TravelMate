import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default api;

/* Auth */
export const authApi = {
  register: (data: { email: string; name: string; password: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
};

/* Trips */
export const tripApi = {
  list: () => api.get("/trips/"),
  get: (id: string) => api.get(`/trips/${id}`),
  create: (data: {
    title: string;
    description?: string;
    start_date: string;
    end_date?: string;
    duration_days?: number;
    origin_country?: string;
    destination_country?: string;
    destination_tz_offset?: number;
  }) => api.post("/trips/", data),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/trips/${id}`, data),
  delete: (id: string) => api.delete(`/trips/${id}`),
};

/* Days */
export const dayApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/days`),
  create: (tripId: string, data: { date: string; title?: string }) =>
    api.post(`/trips/${tripId}/days`, data),
  update: (dayId: string, data: Record<string, unknown>) =>
    api.put(`/days/${dayId}`, data),
  delete: (dayId: string) => api.delete(`/days/${dayId}`),
  reorder: (tripId: string, dayIds: string[]) =>
    api.put(`/trips/${tripId}/days/reorder`, { day_ids: dayIds }),
};

/* Activities */
export const activityApi = {
  list: (dayId: string) => api.get(`/days/${dayId}/activities`),
  create: (
    dayId: string,
    data: {
      title: string;
      notes?: string;
      start_time?: string;
      end_time?: string;
      duration_minutes?: number;
      category?: string;
      location_id?: string;
      assignee_id?: string;
    },
  ) => api.post(`/days/${dayId}/activities`, data),
  update: (activityId: string, data: Record<string, unknown>) =>
    api.put(`/activities/${activityId}`, data),
  delete: (activityId: string) => api.delete(`/activities/${activityId}`),
  reorder: (dayId: string, activityIds: string[]) =>
    api.put(`/days/${dayId}/activities/reorder`, { activity_ids: activityIds }),
};

/* Geocode */
export const geocodeApi = {
  search: (q: string) => api.get("/geocode/search", { params: { q } }),
};

/* Memories */
export const memoryApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/memories`),
  create: (tripId: string, data: {
    title: string;
    content?: string;
    date: string;
    photo_urls?: string[];
  }) => api.post(`/trips/${tripId}/memories`, data),
  update: (memoryId: string, data: Record<string, unknown>) =>
    api.put(`/memories/${memoryId}`, data),
  delete: (memoryId: string) => api.delete(`/memories/${memoryId}`),
};

/* Expenses */
export const expenseApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/expenses`),
  create: (
    tripId: string,
    data: {
      title: string;
      category?: string;
      amount: number;
      currency?: string;
      notes?: string;
      date?: string;
      activity_id?: string;
      paid_by: string;
      split_with?: string[];
    },
  ) => api.post(`/trips/${tripId}/expenses`, data),
  update: (expenseId: string, data: Record<string, unknown>) =>
    api.put(`/expenses/${expenseId}`, data),
  delete: (expenseId: string) => api.delete(`/expenses/${expenseId}`),
  budgetSummary: (tripId: string) =>
    api.get(`/trips/${tripId}/budget-summary`),
  settleSplit: (splitId: string) =>
    api.put(`/splits/${splitId}/settle`),
};

/* Share */
export const shareApi = {
  get: (shareCode: string) => api.get(`/trips/share/${shareCode}`),
};

/* Guest */
export const guestApi = {
  join: (data: { trip_id: string; join_code: string; nickname: string }) =>
    api.post("/trips/join", data),
  getJoinInfo: (tripId: string) =>
    api.get(`/trips/${tripId}/join-info`),
};

/* Packing List */
export const packingApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/packing`),
  create: (tripId: string, data: { name: string; category?: string; quantity?: number }) =>
    api.post(`/trips/${tripId}/packing`, data),
  update: (itemId: string, data: Record<string, unknown>) =>
    api.put(`/packing/${itemId}`, data),
  delete: (itemId: string) => api.delete(`/packing/${itemId}`),
  batchToggle: (tripId: string, itemIds: string[], checked: boolean) =>
    api.put(`/trips/${tripId}/packing/batch-toggle`, { item_ids: itemIds, checked }),
};

/* Comments */
export const commentApi = {
  list: (activityId: string) => api.get(`/activities/${activityId}/comments`),
  create: (activityId: string, data: { content: string }) =>
    api.post(`/activities/${activityId}/comments`, data),
  delete: (commentId: string) => api.delete(`/comments/${commentId}`),
};

/* Polls */
export const pollApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/polls`),
  create: (tripId: string, data: { question: string; options: string[] }) =>
    api.post(`/trips/${tripId}/polls`, data),
  vote: (pollId: string, optionId: string) =>
    api.post(`/polls/${pollId}/vote`, { option_id: optionId }),
  close: (pollId: string) => api.put(`/polls/${pollId}/close`),
};

/* POIs */
export const poiApi = {
  list: (tripId: string) => api.get(`/trips/${tripId}/pois`),
  create: (tripId: string, data: {
    name: string;
    address?: string;
    lat?: number;
    lng?: number;
    place_id?: string;
    notes?: string;
    category?: string;
  }) => api.post(`/trips/${tripId}/pois`, data),
  update: (poiId: string, data: Record<string, unknown>) =>
    api.put(`/pois/${poiId}`, data),
  delete: (poiId: string) => api.delete(`/pois/${poiId}`),
};
