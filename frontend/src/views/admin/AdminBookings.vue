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
            <th>Actions</th>
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
            <td>
              <div class="action-buttons">
                <button v-if="b.status === 'Booked' && b.paymentstatus === 'Pending'"
                        class="btn btn-sm btn-success"
                        @click="updatePayment(b.bookingid, 'Completed')">
                  Mark Paid
                </button>
                <button v-if="b.status === 'Booked' && b.paymentstatus === 'Completed'"
                        class="btn btn-sm btn-warning"
                        @click="updatePayment(b.bookingid, 'Pending')">
                  Mark Unpaid
                </button>
                <button v-if="b.status === 'Booked'"
                        class="btn btn-sm btn-danger"
                        @click="openCancelModal(b)">
                  Cancel
                </button>
                <span v-if="b.status !== 'Booked'" class="text-muted">—</span>
              </div>
            </td>
          </tr>
          <tr v-if="bookingList.length === 0">
            <td colspan="7">No bookings found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Cancel Booking Modal -->
    <div v-if="cancelModal.show" class="modal-overlay" @click.self="cancelModal.show = false">
      <div class="modal-box">
        <h3>Cancel Booking #{{ cancelModal.bookingid }}</h3>
        <p>Trek: <strong>{{ cancelModal.trek }}</strong> | User: <strong>{{ cancelModal.user }}</strong></p>
        <label>Reason for cancellation:</label>
        <textarea v-model="cancelModal.reason" rows="3" placeholder="Enter reason..."></textarea>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="cancelModal.show = false">Close</button>
          <button class="btn btn-danger" @click="cancelBooking" :disabled="!cancelModal.reason.trim()">Confirm Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch } from '../../api.js'

export default {
  data() {
    return {
      bookingList: [],
      cancelModal: { show: false, bookingid: null, trek: '', user: '', reason: '' },
    }
  },
  async mounted() {
    await this.loadBookings()
  },
  methods: {
    async loadBookings() {
      const data = await apiFetch('/admin/bookings')
      if (data.success) this.bookingList = data.bookings
    },
    async updatePayment(bookingid, status) {
      const data = await apiFetch(`/admin/bookings/${bookingid}/payment`, {
        method: 'PUT',
        json: { paymentstatus: status },
      })
      if (data.success) {
        alert(data.message)
        await this.loadBookings()
      } else {
        alert(data.message || 'Failed to update payment')
      }
    },
    openCancelModal(b) {
      this.cancelModal = { show: true, bookingid: b.bookingid, trek: b.trek, user: b.user, reason: '' }
    },
    async cancelBooking() {
      const data = await apiFetch(`/admin/bookings/${this.cancelModal.bookingid}/cancel`, {
        method: 'PUT',
        json: { reason: this.cancelModal.reason },
      })
      if (data.success) {
        alert(data.message)
        this.cancelModal.show = false
        await this.loadBookings()
      } else {
        alert(data.message || 'Failed to cancel booking')
      }
    },
  },
}
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.btn-sm {
  padding: 4px 10px;
  font-size: 0.8rem;
  border-radius: 6px;
}
.text-muted {
  color: #888;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: var(--card-bg, #1e293b);
  padding: 24px;
  border-radius: 12px;
  width: 420px;
  max-width: 90vw;
}
.modal-box h3 {
  margin-top: 0;
}
.modal-box label {
  display: block;
  margin: 12px 0 6px;
  font-weight: 600;
}
.modal-box textarea {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #444;
  background: var(--input-bg, #0f172a);
  color: inherit;
  resize: vertical;
}
.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
