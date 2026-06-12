<template>
  <div class="dashboard">
    <h1 class="heading">Booking Management</h1>

    <div class="content-box">
      <table>
        <thead>
          <tr>
            <th>Booking ID</th>
            <th>User</th>
            <th>Trek</th>
            <th>Booking Date</th>
            <th>Booking Status</th>
            <th>Payment Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookingList" :key="b.bookingid">
            <td v-text="b.bookingid"></td>
            <td v-text="b.user"></td>
            <td v-text="b.trek"></td>
            <td v-text="b.bookingdate"></td>
            <td>
              <span :class="'badge-' + b.status.toLowerCase()" v-text="b.status"></span>
            </td>
            <td>
              <span :class="b.paymentstatus === 'Completed' ? 'badge-completed' : 'badge-pending'"
                    v-text="b.paymentstatus"></span>
            </td>
          </tr>
          <tr v-if="bookingList.length === 0">
            <td colspan="6">No bookings found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '../../api.js'

export default {
  data() {
    return {
      bookingList: [],
    }
  },
  async mounted() {
    const data = await apiFetch('/admin/bookings')
    if (data.success) this.bookingList = data.bookings
  },
}
</script>
