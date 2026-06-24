export interface User {
  id: string;
  email: string;
  name: string;
}

export interface Trip {
  id: string;
  title: string;
  description: string | null;
  start_date: string;
  end_date: string;
  cover_url: string | null;
  share_code: string;
  visibility: "private" | "shared" | "public";
  origin_country: string | null;
  destination_country: string | null;
  destination_tz_offset: number | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface Day {
  id: string;
  trip_id: string;
  date: string;
  title: string | null;
  order_index: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface Activity {
  id: string;
  day_id: string;
  location_id: string | null;
  title: string;
  notes: string | null;
  start_time: string | null;
  end_time: string | null;
  duration_minutes: number | null;
  transport_mode: string | null;
  from_location_id: string | null;
  to_location_id: string | null;
  category: ActivityCategory;
  order_index: number;
  created_at: string | null;
  updated_at: string | null;
  location: { lat: number | null; lng: number | null; name?: string | null } | null;
}

export type ActivityCategory =
  | "transport"
  | "food"
  | "attraction"
  | "shopping"
  | "accommodation"
  | "flight"
  | "train"
  | "bus"
  | "ferry"
  | "other";

export interface Memory {
  id: string;
  trip_id: string;
  user_id: string;
  user_name: string;
  title: string;
  content: string | null;
  photo_urls: string[] | null;
  date: string;
  created_at: string | null;
}

export interface Location {
  id: string;
  name: string;
  address: string | null;
  lat: number | null;
  lng: number | null;
  place_id: string | null;
}

export interface POI {
  id: string;
  trip_id: string;
  name: string;
  address: string | null;
  lat: number | null;
  lng: number | null;
  place_id: string | null;
  notes: string | null;
  category: string;
  created_at: string | null;
}

export interface GeocodeResult {
  display_name: string;
  lat: number;
  lng: number;
  place_id: string;
}

export const CATEGORY_LABELS: Record<ActivityCategory, string> = {
  transport: "🚆 交通",
  food: "🍜 美食",
  attraction: "🏛️ 景點",
  shopping: "🛍️ 購物",
  accommodation: "🏨 住宿",
  flight: "✈️ 航班",
  train: "🚄 火車",
  bus: "🚌 巴士",
  ferry: "⛴️ 渡輪",
  other: "📌 其他",
};

export const CATEGORY_COLORS: Record<ActivityCategory, string> = {
  transport: "bg-blue-100 text-blue-800",
  food: "bg-orange-100 text-orange-800",
  attraction: "bg-purple-100 text-purple-800",
  shopping: "bg-pink-100 text-pink-800",
  accommodation: "bg-green-100 text-green-800",
  flight: "bg-sky-100 text-sky-800",
  train: "bg-teal-100 text-teal-800",
  bus: "bg-amber-100 text-amber-800",
  ferry: "bg-cyan-100 text-cyan-800",
  other: "bg-gray-100 text-gray-800",
};
