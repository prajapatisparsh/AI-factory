export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#05050a]">
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-2 border-[rgba(99,102,241,0.15)]" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[#6366f1] animate-spin" />
        </div>
        <p className="text-xs text-[#8888aa] animate-pulse">Loading AI Factory…</p>
      </div>
    </div>
  );
}
