export interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  promo_price?: number;
  gifts?: string[];
  strengths: string[];
  trade_offs: string[];
  summary: string;
}

export interface Comparison {
  products: Product[];
  differences: Record<string, string>; // feature -> value or similar
}

export interface NeedSummaryData {
  category?: string;
  budget?: string;
  household_size?: string;
  priorities?: string[];
  room_area?: string;
  [key: string]: any;
}

export type MessageType = "text" | "products" | "comparison" | "need_summary" | "follow_up";

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
