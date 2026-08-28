import { Button } from "@/components/ui/button";

export function QuickReply({ replies, onSelect }: { replies: string[]; onSelect: (reply: string) => void }) {
  if (!replies || replies.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 my-2">
      {replies.map((reply, i) => (
        <Button
          key={i}
          variant="outline"
          size="sm"
          className="rounded-full border-green-200 text-green-700 bg-white hover:bg-green-50 hover:text-green-800"
          onClick={() => onSelect(reply)}
        >
          {reply}
        </Button>
      ))}
    </div>
  );
}
