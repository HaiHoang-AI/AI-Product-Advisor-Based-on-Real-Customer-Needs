export interface Product {
  id?: string;
  product_id?: string;
  name: string;
  brand: string;
  price?: number;
  price_original?: number;
  price_promo?: number;
  promo_price?: number;
  promotion_gift?: string;
  gifts?: string[];
  strengths?: string[];
  trade_offs?: string[];
  summary?: string;
  specs?: Record<string, string>;
  data_sources?: string[];
  rank?: number;
}

export interface ComparisonItem {
  rank: number;
  name: string;
  price?: number;
  specs: Record<string, string>;
}

export interface NeedSummaryData {
  category?: string;
  budget?: string;
  budget_min?: string;
  household_size?: string;
  priorities?: string[];
  usage_purpose?: string[];
  room_area?: string;
  room_type?: string;
  installment?: string;
  missing_info?: string[];
  [key: string]: any;
}

export type MessageType = "text" | "products" | "comparison" | "need_summary" | "follow_up" | "error" | "done";

export interface MessageContent {
  type: MessageType;
  content: any;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text?: string;
  events?: MessageContent[];
}
