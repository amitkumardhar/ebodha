<template>
  <v-app>
    <v-app-bar app flat border v-if="!isLoginPage">
      <v-container class="d-flex align-center py-0 fill-height" style="max-width: 1200px;">
        <v-app-bar-title class="text-h6 font-weight-black tracking-wide">
          E-Bodha
        </v-app-bar-title>
        <v-spacer></v-spacer>
        <AccountMenu />
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container 
        class="pa-0 mx-auto" 
        :class="{ 'fill-height': isLoginPage, 'mt-6': !isLoginPage }"
        style="max-width: 1200px;"
      >
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AccountMenu from './components/AccountMenu.vue'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'Login')
</script>

<style>
.tracking-wide {
    letter-spacing: 0.1em;
}
</style>