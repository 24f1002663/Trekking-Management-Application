<template>
  <div class="dashboard">
    <h1 class="heading">Admin Dashboard</h1>

    <div class="cards">
      <div class="stat-card">
        <h3>Total Users</h3>
        <p v-text="stats.total_users"></p>
      </div>
      <div class="stat-card">
        <h3>Total Staff</h3>
        <p v-text="stats.total_staff"></p>
      </div>
      <div class="stat-card">
        <h3>Total Treks</h3>
        <p v-text="stats.total_treks"></p>
      </div>
      <div class="stat-card">
        <h3>Total Bookings</h3>
        <p v-text="stats.total_bookings"></p>
      </div>
    </div>

    <div class="content-box">
      <h2>Welcome, Administrator</h2>
      <p>Use the navigation bar above to manage the trekking platform.</p>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '../../api.js'

export default {
  data() {
    return {
      stats: { total_users: 0, total_staff: 0, total_treks: 0, total_bookings: 0 },
    }
  },
  async mounted() {
    const data = await apiFetch('/admin/dashboard')
    if (data.success) this.stats = data.dashboard
  },
}
</script>
