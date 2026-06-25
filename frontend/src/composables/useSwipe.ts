import { ref } from "vue";

const tabs = ["itinerary", "map", "budget", "memories", "poi", "packing", "photos", "polls"] as const;

export function useSwipeTabs(activeTab: ReturnType<typeof ref<string>>) {
  let startX = 0;
  let startY = 0;
  let swiping = false;

  function onTouchStart(e: TouchEvent) {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    swiping = true;
  }

  function onTouchEnd(e: TouchEvent) {
    if (!swiping) return;
    swiping = false;
    const diffX = e.changedTouches[0].clientX - startX;
    const diffY = e.changedTouches[0].clientY - startY;
    if (Math.abs(diffX) < 50 || Math.abs(diffY) > Math.abs(diffX) * 1.5) return;
    const currentIdx = tabs.indexOf(activeTab.value as typeof tabs[number]);
    if (diffX > 0 && currentIdx > 0) {
      activeTab.value = tabs[currentIdx - 1];
    } else if (diffX < 0 && currentIdx < tabs.length - 1) {
      activeTab.value = tabs[currentIdx + 1];
    }
  }

  return { onTouchStart, onTouchEnd };
}