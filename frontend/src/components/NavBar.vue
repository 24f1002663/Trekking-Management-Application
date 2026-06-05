<template>
  <nav class="navbar">
    <div class="logo">Trek Management</div>

    <div class="nav-links">
      <template v-if="role === 'admin'">
        <router-link to="/admindashboard">Dashboard</router-link>
        <router-link to="/adminstaff">Staff</router-link>
        <router-link to="/admintreks">Treks</router-link>
        <router-link to="/adminusers">Users</router-link>
        <router-link to="/adminbookings">Bookings</router-link>
        <router-link to="/adminreports">Reports</router-link>
        <router-link to="/adminnotifications">Notifications</router-link>
      </template>
      <template v-else-if="role === 'staff'">
        <router-link to="/staffdashboard">Dashboard</router-link>
      </template>
      <template v-else>
        <router-link to="/userdashboard">Dashboard</router-link>
      </template>
    </div>

    <div class="nav-user">
      <span>Welcome, {{ name }}</span>
      <button @click="doLogout">Logout</button>
    </div>
  </nav>
</template>

<script>
import { getRole, getName, logout } from '../api.js'

export default {
  data() {
    return {
      role: getRole(),
      name: getName(),
    }
  },
  methods: {
    doLogout() {
      logout()
    },
  },
}
</script>
