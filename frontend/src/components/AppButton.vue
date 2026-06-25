<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  rounded?: 'md' | 'lg' | 'xl' | 'full'
  loading?: boolean
  disabled?: boolean
  icon?: string
}>(), {
  variant: 'primary',
  size: 'md',
  rounded: 'lg',
  loading: false,
  disabled: false,
})
</script>

<template>
  <button
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-1.5 font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2',
      // Size
      size === 'sm' ? 'px-3 py-1.5 text-xs' : '',
      size === 'md' ? 'px-4 py-2 text-sm' : '',
      size === 'lg' ? 'px-6 py-3 text-base' : '',
      // Radius
      rounded === 'md' ? 'rounded-md' : '',
      rounded === 'lg' ? 'rounded-lg' : '',
      rounded === 'xl' ? 'rounded-xl' : '',
      rounded === 'full' ? 'rounded-full' : '',
      // Variant
      variant === 'primary' ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md hover:shadow-lg hover:from-indigo-500 hover:to-indigo-400 focus:ring-indigo-500' : '',
      variant === 'secondary' ? 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-indigo-500' : '',
      variant === 'danger' ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-md hover:shadow-lg hover:from-red-500 hover:to-red-400 focus:ring-red-500' : '',
      variant === 'ghost' ? 'text-gray-600 hover:bg-gray-100 focus:ring-gray-400' : '',
      // Disabled
      (disabled || loading) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
    ]"
  >
    <span v-if="loading" class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"></span>
    <span v-else-if="icon">{{ icon }}</span>
    <slot />
  </button>
</template>
