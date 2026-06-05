<template>
  <div class="background"></div>

  <NavBar v-if="showNav" />

  <div class="container">
    <router-view />
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  components: { NavBar },
  computed: {
    // Navbar is hidden on the login/register pages (mirrors base.html).
    showNav() {
      return !this.$route.meta.public
    },
  },
}
</script>
