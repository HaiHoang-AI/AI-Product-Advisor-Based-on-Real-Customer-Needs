"use client";

import { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { ChatMessage, MessageContent } from "./types";
import { ProductCard } from "./ProductCard";
import { NeedSummary } from "./NeedSummary";
import { ComparisonView } from "./ComparisonView";
import { QuickReply } from "./QuickReply";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Xin chào! Em là trợ lý AI của Điện Máy Xanh. Em có thể giúp anh/chị tìm và so sánh sản phẩm phù hợp nhất với nhu cầu. Anh/chị muốn tìm sản phẩm gì ạ?",
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
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

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

      if (!response.body) throw new Error("No body");
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
            const dataStr = line.slice(6);
            if (dataStr === "[DONE]") continue;

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
              console.error("Failed to parse SSE JSON", e, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [...prev, { id: uuidv4(), role: "assistant", text: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (msg: ChatMessage) => {
    const isUser = msg.role === "user";
    return (
      <div key={msg.id} className={`flex gap-3 mb-6 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        <Avatar className={`w-8 h-8 ${isUser ? "bg-slate-200" : "bg-[#00a651]"}`}>
          {isUser ? <User className="w-5 h-5 m-auto text-slate-600" /> : <Bot className="w-5 h-5 m-auto text-white" />}
        </Avatar>
        <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? "items-end" : "items-start"}`}>
          {msg.text && (
            <div className={`p-3 rounded-2xl ${isUser ? "bg-[#00a651] text-white rounded-tr-none" : "bg-white border border-slate-100 shadow-sm text-slate-800 rounded-tl-none whitespace-pre-wrap"}`}>
              {msg.text}
            </div>
          )}
          {msg.events?.map((ev, i) => (
            <div key={i} className="w-full">
              {ev.type === "products" && (
                <div className="flex flex-col gap-2">
                  {ev.content.map((p: any, idx: number) => (
                    <ProductCard key={p.id || idx} product={p} rank={idx + 1} />
                  ))}
                </div>
              )}
              {ev.type === "comparison" && <ComparisonView data={ev.content} />}
              {ev.type === "need_summary" && <NeedSummary data={ev.content} />}
              {ev.type === "follow_up" && (
                <QuickReply replies={ev.content} onSelect={handleSend} />
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-50">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="max-w-3xl mx-auto flex flex-col">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="flex gap-3 mb-6">
              <Avatar className="w-8 h-8 bg-[#00a651]">
                <Bot className="w-5 h-5 m-auto text-white" />
              </Avatar>
              <div className="p-3 bg-white border border-slate-100 shadow-sm rounded-2xl rounded-tl-none flex gap-1 items-center">
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-slate-300 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="p-4 bg-white border-t border-slate-200">
        <form
          className="max-w-3xl mx-auto flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputValue);
          }}
        >
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 rounded-full border-slate-300 focus-visible:ring-[#00a651]"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()} className="rounded-full bg-[#00a651] hover:bg-green-700">
            <Send className="w-4 h-4 text-white" />
          </Button>
        </form>
      </div>
    </div>
  );
}
