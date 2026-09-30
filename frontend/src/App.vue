<template>
  <router-view />
  <NotificationToast />
</template>

<script setup lang="ts">
import NotificationToast from '@/components/composite/NotificationToast.vue'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
}
</style>
