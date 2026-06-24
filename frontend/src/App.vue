<script setup lang="ts">
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();
onMounted(() => auth.restoreSession());
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <router-view />
  </div>
</template>
