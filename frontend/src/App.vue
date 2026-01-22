<template>
  <v-app>
    <v-app-bar app flat border v-if="!isLoginPage">
      <v-app-bar-title class="text-h6 font-weight-black tracking-wide">
        E-BODHA
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <AccountMenu />
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-0 fill-height">
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