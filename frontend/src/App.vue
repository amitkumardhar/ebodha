<template>
  <v-app>
    <v-app-bar app flat border v-if="!isLoginPage">
      <v-container class="d-flex align-center py-0 fill-height" style="max-width: 1200px;">
        <div class="d-flex align-center" style="flex: 1;">
            <div class="text-h6 font-weight-black tracking-wide">E-Bodha</div>
        </div>
        
        <div class="d-flex align-center">
            <v-img src="/logo.png" width="40" contain></v-img>
        </div>

        <div class="d-flex justify-end" style="flex: 1;">
            <AccountMenu />
        </div>
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

    <v-footer app border height="40" class="justify-center">
        <div class="text-caption text-medium-emphasis">
            Made at IIT Bhilai
        </div>
    </v-footer>
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