import { ref } from "vue";

export function usePullToRefresh(onRefresh: () => Promise<void>) {
  const pullDistance = ref(0);
  const isRefreshing = ref(false);
  const pullThreshold = 80;
  let startY = 0;
  let isPulling = false;

  function onTouchStart(e: TouchEvent) {
    if (window.scrollY > 0) return;
    startY = e.touches[0].clientY;
    isPulling = true;
  }

  function onTouchMove(e: TouchEvent) {
    if (!isPulling || isRefreshing.value) return;
    const diff = e.touches[0].clientY - startY;
    if (diff > 0) {
      pullDistance.value = Math.min(diff * 0.5, 120);
    }
  }

  function onTouchEnd() {
    isPulling = false;
    if (pullDistance.value >= pullThreshold) {
      isRefreshing.value = true;
      pullDistance.value = 0;
      onRefresh().finally(() => {
        isRefreshing.value = false;
      });
    } else {
      pullDistance.value = 0;
    }
  }

  return {
    pullDistance,
    isRefreshing,
    pullThreshold,
    onTouchStart,
    onTouchMove,
    onTouchEnd,
  };
}
