<template>
  <div class="dashboard">
    <h1 class="heading">Staff Dashboard</h1>

    <!-- Stats -->
    <div class="cards">
      <div class="stat-card">
        <h3>Assigned Treks</h3>
        <p v-text="treks.length"></p>
      </div>
      <div class="stat-card">
        <h3>Total Participants</h3>
        <p v-text="totalParticipants"></p>
      </div>
      <div class="stat-card">
        <h3>Active Treks</h3>
        <p v-text="activeCount"></p>
      </div>
    </div>

    <!-- Assigned Treks Table -->
    <div class="content-box">
      <h2>My Assigned Treks</h2>
      <table>
        <thead>
          <tr>
            <th>Trek Name</th>
            <th>Location</th>
            <th>Start</th>
            <th>End</th>
            <th>Seats</th>
            <th>Booked</th>
            <th>Participants</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in treks" :key="t.trekid">
            <td v-text="t.trekname"></td>
            <td v-text="t.location"></td>
            <td v-text="t.startdate"></td>
            <td v-text="t.enddate"></td>
            <td v-text="t.seats"></td>
            <td v-text="t.bookedseats"></td>
            <td v-text="t.participants"></td>
            <td>
              <select v-model="t.status" @change="updateStatus(t.trekid, t.status)">
                <option value="Open">Open</option>
                <option value="Started">Started</option>
                <option value="Completed">Completed</option>
                <option value="Closed">Closed</option>
              </select>
            </td>
            <td>
              <button class="action-btn edit" @click="openSlots(t)">Slots</button>
              <button class="action-btn assign" @click="openParticipants(t)">Participants</button>
              <button class="action-btn del" @click="openReject(t)">Reject</button>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="9">No treks assigned yet.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Update Slots Modal -->
    <div class="modal-overlay" :class="{ active: showSlotsModal }">
      <div class="modal-box">
        <h3>Update Seats</h3>
        <p style="margin-bottom:10px;">Trek: <b v-text="selectedTrekName"></b></p>
        <label style="font-size:13px; color:#555; display:block; margin-bottom:4px;">Total Seats</label>
        <input type="number" v-model="newSeats"
               style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:12px;">
        <div class="modal-actions">
          <button class="btn-save" @click="saveSlots()">Update</button>
          <button class="btn-cancel" @click="showSlotsModal = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Participants Modal -->
    <div class="modal-overlay" :class="{ active: showParticipants }">
      <div class="modal-box" style="width:650px;">
        <h3>Participants — <span v-text="selectedTrekName"></span></h3>
        <table style="margin-top:12px;">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Gender</th>
              <th>Booking</th>
              <th>Payment</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in participants" :key="p.bookingid">
              <td v-text="p.name"></td>
              <td v-text="p.email"></td>
              <td v-text="p.phone || '-'"></td>
              <td v-text="p.gender"></td>
              <td v-text="p.status"></td>
              <td v-text="p.paymentstatus"></td>
            </tr>
            <tr v-if="participants.length === 0">
              <td colspan="6">No participants yet.</td>
            </tr>
          </tbody>
        </table>
        <div class="modal-actions" style="margin-top:14px;">
          <button class="btn-cancel" @click="showParticipants = false">Close</button>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div class="modal-overlay" :class="{ active: showRejectModal }">
      <div class="modal-box">
        <h3>Reject Trek Assignment</h3>
        <p style="margin-bottom:10px;">Trek: <b v-text="selectedTrekName"></b></p>
        <label style="font-size:13px; color:#555; display:block; margin-bottom:4px;">Reason for rejection</label>
        <textarea v-model="rejectReason" placeholder="Enter your reason..."
                  style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:12px; height:80px;"></textarea>
        <div class="modal-actions">
          <button class="btn-save" @click="submitReject()">Submit</button>
          <button class="btn-cancel" @click="showRejectModal = false">Cancel</button>
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
      treks: [],
      participants: [],
      showSlotsModal: false,
      showParticipants: false,
      showRejectModal: false,
      selectedTrekId: null,
      selectedTrekName: '',
      newSeats: 0,
      rejectReason: '',
    }
  },
  computed: {
    totalParticipants() {
      return this.treks.reduce((sum, t) => sum + (t.participants || 0), 0)
    },
    activeCount() {
      return this.treks.filter((t) => t.status === 'Open' || t.status === 'Started').length
    },
  },
  mounted() {
    this.loadTreks()
  },
  methods: {
    async loadTreks() {
      const data = await apiFetch('/staff/dashboard')
      if (data.success) this.treks = data.treks
    },
    async updateStatus(id, status) {
      const data = await apiFetch('/staff/treks/' + id + '/status', {
        method: 'PUT',
        json: { status },
      })
      alert(data.message)
      await this.loadTreks()
    },
    openSlots(t) {
      this.selectedTrekId = t.trekid
      this.selectedTrekName = t.trekname
      this.newSeats = t.seats
      this.showSlotsModal = true
    },
    async saveSlots() {
      const data = await apiFetch('/staff/treks/' + this.selectedTrekId + '/slots', {
        method: 'PUT',
        json: { seats: this.newSeats },
      })
      alert(data.message)
      if (data.success) {
        this.showSlotsModal = false
        await this.loadTreks()
      }
    },
    async openParticipants(t) {
      this.selectedTrekName = t.trekname
      this.participants = []
      this.showParticipants = true
      const data = await apiFetch('/staff/treks/' + t.trekid + '/participants')
      if (data.success) this.participants = data.participants
    },
    openReject(t) {
      this.selectedTrekId = t.trekid
      this.selectedTrekName = t.trekname
      this.rejectReason = ''
      this.showRejectModal = true
    },
    async submitReject() {
      if (!this.rejectReason.trim()) {
        alert('Please enter a reason.')
        return
      }
      const data = await apiFetch('/staff/treks/' + this.selectedTrekId + '/reject', {
        method: 'POST',
        json: { reason: this.rejectReason },
      })
      alert(data.message)
      if (data.success) {
        this.showRejectModal = false
        await this.loadTreks()
      }
    },
  },
}
</script>
