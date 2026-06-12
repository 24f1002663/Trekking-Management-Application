<template>
  <div class="dashboard">
    <h1 class="heading">Reports &amp; Statistics</h1>

    <div class="cards">
      <div class="stat-card">
        <h3>Total Users</h3>
        <p v-text="report.total_users"></p>
      </div>
      <div class="stat-card">
        <h3>Total Staff</h3>
        <p v-text="report.total_staff"></p>
      </div>
      <div class="stat-card">
        <h3>Total Treks</h3>
        <p v-text="report.total_treks"></p>
      </div>
      <div class="stat-card">
        <h3>Total Bookings</h3>
        <p v-text="report.total_bookings"></p>
      </div>
    </div>

    <div class="cards" style="grid-template-columns: repeat(3, 1fr);">
      <div class="stat-card">
        <h3>Completed Bookings</h3>
        <p v-text="report.completed_bookings"></p>
      </div>
      <div class="stat-card">
        <h3>Successful Payments</h3>
        <p v-text="report.successful_payments"></p>
      </div>
      <div class="stat-card">
        <h3>Pending Payments</h3>
        <p v-text="report.pending_payments"></p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '../../api.js'

export default {
  data() {
    return {
      report: {
        total_users: 0, total_staff: 0, total_treks: 0,
        total_bookings: 0, completed_bookings: 0,
        successful_payments: 0, pending_payments: 0,
      },
    }
  },
  async mounted() {
    const data = await apiFetch('/admin/reports')
    if (data.success) this.report = data.report
  },
}
</script>
