<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps<{
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const confirmBtn = ref<HTMLButtonElement | null>(null)
const cancelBtn = ref<HTMLButtonElement | null>(null)

const iconBgClass = computed(() => {
  switch (props.variant) {
    case 'danger': return 'bg-red-100'
    case 'warning': return 'bg-amber-100'
    default: return 'bg-indigo-100'
  }
})

const iconText = computed(() => {
  switch (props.variant) {
    case 'danger':
    case 'warning':
      return '⚠️'
    default:
      return 'ℹ️'
  }
})

const confirmBtnClass = computed(() => {
  if (props.loading) return 'bg-indigo-400 cursor-not-allowed'
  switch (props.variant) {
    case 'danger': return 'bg-red-600 hover:bg-red-700'
    case 'warning': return 'bg-amber-600 hover:bg-amber-700'
    default: return 'bg-indigo-600 hover:bg-indigo-700'
  }
})

watch(() => props.show, async (val) => {
  if (val) {
    await nextTick()
    confirmBtn.value?.focus()
  }
})

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('cancel')
    return
  }
  if (e.key !== 'Tab') return
  if (!confirmBtn.value || !cancelBtn.value) return
  if (e.shiftKey) {
    if (document.activeElement === confirmBtn.value) {
      e.preventDefault()
      cancelBtn.value.focus()
    }
  } else {
    if (document.activeElement === cancelBtn.value) {
      e.preventDefault()
      confirmBtn.value.focus()
    }
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
        @click.self="emit('cancel')"
        @keydown="onKeydown"
      >
        <div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
          <div
            class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full text-2xl"
            :class="iconBgClass"
          >
            {{ iconText }}
          </div>

          <h3 class="text-center text-lg font-bold">
            {{ title || '確認' }}
          </h3>

          <p v-if="message" class="mt-2 text-center text-sm text-gray-500">
            {{ message }}
          </p>

          <div class="mt-6 flex gap-3">
            <button
              ref="cancelBtn"
              class="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
              @click="emit('cancel')"
            >
              {{ cancelText || '取消' }}
            </button>

            <button
              ref="confirmBtn"
              :disabled="loading"
              :class="confirmBtnClass"
              class="flex-1 rounded-lg px-4 py-2 text-sm text-white"
              @click="emit('confirm')"
            >
              <span
                v-if="loading"
                class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
              />
              <span v-else>{{ confirmText || '確認' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
