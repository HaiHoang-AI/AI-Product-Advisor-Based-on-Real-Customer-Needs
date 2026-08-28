"use client";

import { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { ChatMessage, MessageContent } from "./types";
import { ProductCard } from "./ProductCard";
import { NeedSummary } from "./NeedSummary";
import { ComparisonView } from "./ComparisonView";
import { QuickReply } from "./QuickReply";
import { Send, Bot, User, Sparkles, RefreshCw, ShieldCheck, Zap } from "lucide-react";

interface ChatPanelProps {
  onInitialPrompt?: string;
}

export function ChatPanel({ onInitialPrompt }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "👋 Xin chào! Em là **Trợ lý AI Điện Máy Xanh**.\n\nEm được thiết kế để lắng nghe **nhu cầu thật** của anh/chị (ngân sách, số người dùng, không gian phòng, ưu tiên tiết kiệm điện hay độ êm...) và đề xuất các sản phẩm tối ưu nhất kèm phân tích **điểm mạnh & điểm đánh đổi**.\n\n💡 *Anh/chị đang quan tâm đến sản phẩm nào ạ? (Ví dụ: Tủ lạnh cho gia đình 4 người, Máy lạnh phòng 18m², Laptop đồ họa...)*",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setConversationId(uuidv4());
  }, []);

  useEffect(() => {
    if (onInitialPrompt) {
      handleSend(onInitialPrompt);
    }
  }, [onInitialPrompt]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: ChatMessage = { id: uuidv4(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    const assistantMsgId = uuidv4();
    setMessages((prev) => [...prev, { id: assistantMsgId, role: "assistant", events: [] }]);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, conversation_id: conversationId }),
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (!dataStr || dataStr === "[DONE]") continue;

            try {
              const eventData: MessageContent = JSON.parse(dataStr);
              setMessages((prev) => {
                const newMsgs = [...prev];
                const lastMsg = newMsgs[newMsgs.length - 1];
                if (lastMsg.id === assistantMsgId) {
                  if (eventData.type === "text") {
                    lastMsg.text = (lastMsg.text || "") + eventData.content;
                  } else {
                    lastMsg.events = lastMsg.events || [];
                    lastMsg.events.push(eventData);
                  }
                }
                return newMsgs;
              });
            } catch (e) {
              console.error("Failed to parse SSE event", e, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: uuidv4(),
          role: "assistant",
          text: "Xin lỗi anh/chị, kết nối đến máy chủ AI bị gián đoạn. Vui lòng thử lại sau ít giây.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetChat = () => {
    setConversationId(uuidv4());
    setMessages([
      {
        id: "welcome-reset",
        role: "assistant",
        text: "👋 Cuộc hội thoại mới đã sẵn sàng! Anh/chị muốn tìm hiểu và so sánh sản phẩm gì ạ?",
      },
    ]);
  };

  const starterChips = [
    "Tủ lạnh cho 4 người dưới 15 triệu, tiết kiệm điện",
    "Máy lạnh phòng 18m² dưới 20 triệu, chạy êm",
    "Laptop làm việc văn phòng mượt dưới 18 triệu",
    "Tủ lạnh side by side dung tích lớn cho 6 người",
  ];

  return (
    <div className="flex flex-col h-full bg-slate-50/50 dark:bg-slate-950">
      {/* Top Header of Chat Area */}
      <div className="px-4 py-3 border-b border-slate-200/80 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between z-10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-sm shadow-emerald-600/30">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-slate-900 dark:text-white">
                Trợ Lý AI Điện Máy Xanh
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              RAG Hybrid Engine • 10,438 Sản Phẩm
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/60 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
            <ShieldCheck className="w-3 h-3 text-emerald-600" />
            Zero Hallucination
          </span>
          <button
            onClick={handleResetChat}
            className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
            title="Bắt đầu hội thoại mới"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                    isUser
                      ? "bg-slate-800 text-white"
                      : "bg-emerald-600 text-white shadow-sm shadow-emerald-600/30"
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`flex flex-col gap-2 max-w-[88%] sm:max-w-[82%] ${
                    isUser ? "items-end" : "items-start"
                  }`}
                >
                  {msg.text && (
                    <div
                      className={`p-3.5 sm:p-4 rounded-2xl text-sm leading-relaxed ${
                        isUser
                          ? "bg-emerald-600 text-white rounded-tr-none shadow-sm shadow-emerald-600/20"
                          : "bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-xs text-slate-800 dark:text-slate-100 rounded-tl-none whitespace-pre-wrap"
                      }`}
                    >
                      {msg.text}
                    </div>
                  )}

                  {msg.events?.map((ev, i) => (
                    <div key={i} className="w-full">
                      {ev.type === "need_summary" && <NeedSummary data={ev.content} />}
                      {ev.type === "products" && (
                        <div className="space-y-2 mt-2">
                          {ev.content.map((p: any, idx: number) => (
                            <ProductCard key={p.product_id || p.id || idx} product={p} rank={p.rank || idx + 1} />
                          ))}
                        </div>
                      )}
                      {ev.type === "comparison" && <ComparisonView data={ev.content} />}
                      {ev.type === "follow_up" && (
                        <QuickReply replies={ev.content} onSelect={handleSend} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white shrink-0">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs rounded-2xl rounded-tl-none flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce delay-100"></div>
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce delay-200"></div>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium ml-2">
                  AI đang tra cứu catalog & tính toán trade-off...
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Suggested Starter Chips */}
      {messages.length <= 1 && (
        <div className="p-3 bg-white/70 dark:bg-slate-900/70 border-t border-slate-100 dark:border-slate-800">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              Gợi ý câu hỏi mẫu:
            </div>
            <div className="flex flex-wrap gap-2">
              {starterChips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(chip)}
                  className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-emerald-50 hover:text-emerald-700 dark:hover:bg-emerald-950/60 dark:hover:text-emerald-300 border border-slate-200/80 dark:border-slate-700 transition-all cursor-pointer text-left"
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <form
          className="max-w-3xl mx-auto flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputValue);
          }}
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Nhập nhu cầu mua sắm (VD: Mua tủ lạnh 4 người, tiết kiệm điện dưới 15tr)..."
            className="flex-1 px-4 py-3 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="w-11 h-11 rounded-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white flex items-center justify-center shadow-md shadow-emerald-600/30 transition-all cursor-pointer shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
