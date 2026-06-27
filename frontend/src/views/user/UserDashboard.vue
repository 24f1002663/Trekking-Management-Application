<template>
  <div class="dashboard">
    <!-- Tabs -->
    <div class="page-actions">
      <button class="add-btn" @click="tab='home'; loadDashboard()">Dashboard</button>
      <button class="add-btn" @click="tab='treks'">Browse Treks</button>
      <button class="add-btn" @click="tab='bookings'; loadBookings()">My Bookings</button>
      <button class="add-btn" @click="tab='profile'; loadProfile()">Profile</button>
    </div>

    <!-- Dashboard Home -->
    <div v-if="tab=='home'">
      <h1 class="heading">Welcome, <span v-text="dashName"></span></h1>

      <div class="cards">
        <div class="stat-card">
          <h3>Active Bookings</h3>
          <p v-text="stats.active_bookings"></p>
        </div>
        <div class="stat-card">
          <h3>Completed Treks</h3>
          <p v-text="stats.completed_treks"></p>
        </div>
        <div class="stat-card">
          <h3>Cancelled</h3>
          <p v-text="stats.cancelled_bookings"></p>
        </div>
      </div>

      <div class="content-box">
        <h2>Recent Activity</h2>
        <table>
          <thead>
            <tr>
              <th>Trek</th>
              <th>Location</th>
              <th>Booked On</th>
              <th>Status</th>
              <th>Trek Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in stats.recent" :key="r.trekname + r.bookingdate">
              <td v-text="r.trekname"></td>
              <td v-text="r.location"></td>
              <td v-text="r.bookingdate"></td>
              <td v-text="r.status"></td>
              <td v-text="r.trekstatus"></td>
            </tr>
            <tr v-if="stats.recent.length === 0">
              <td colspan="5">No activity yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Browse Treks -->
    <div v-if="tab=='treks'">
      <div class="page-actions">
        <h1 class="heading" style="margin-bottom:0;">Available Treks</h1>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
          <input class="search-box" v-model="search" @input="loadTreks()" placeholder="Search..." style="margin-bottom:0; width:180px;">
          <input class="search-box" v-model="filterLocation" @input="loadTreks()" placeholder="Location..." style="margin-bottom:0; width:160px;">
          <input class="search-box" type="number" min="1" v-model="filterDuration" @input="loadTreks()" placeholder="Days" style="margin-bottom:0; width:100px;">
          <select v-model="filterDifficulty" @change="loadTreks()" style="padding:10px; border:1px solid #ccc; border-radius:8px;">
            <option value="">All Difficulties</option>
            <option>Easy</option>
            <option>Medium</option>
            <option>Hard</option>
          </select>
        </div>
      </div>

      <p v-if="bookingMsg"
         style="padding:10px; border-radius:6px; margin-bottom:16px; text-align:center;"
         :style="bookingSuccess ? 'background:#d4edda; color:#155724;' : 'background:#f8d7da; color:#721c24;'"
         v-text="bookingMsg"></p>

      <div class="cards">
        <div class="content-box" v-for="t in trekList" :key="t.trekid">
          <img v-if="t.images && t.images.length" :src="t.images[0]"
               style="width:100%; height:160px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
          <h3 v-text="t.trekname"></h3>
          <p v-text="'📍 ' + t.location"></p>
          <p v-text="'💪 ' + t.difficulty"></p>
          <p v-text="'⏱ ' + t.durationdays + ' days'"></p>
          <p v-text="'₹' + t.price"></p>
          <p v-text="'💺 ' + t.available_seats + ' seats left'"></p>
          <div style="display:flex; gap:8px; margin-top:10px;">
            <button class="action-btn edit" @click="openTrekDetail(t)">Details</button>
            <button class="action-btn assign"
                    @click="bookTrek(t.trekid)"
                    :disabled="t.available_seats === 0"
                    v-text="t.available_seats === 0 ? 'Full' : 'Book Now'"></button>
          </div>
        </div>
      </div>

      <p v-if="trekList.length === 0" style="text-align:center; color:#888; margin-top:20px;">No treks available right now.</p>
    </div>

    <!-- My Bookings -->
    <div v-if="tab=='bookings'">
      <div class="page-actions">
        <h1 class="heading" style="margin-bottom:0;">My Bookings</h1>
        <button class="add-btn" @click="exportBookings()">⬇ Export CSV</button>
      </div>

      <div class="content-box">
        <table>
          <thead>
            <tr>
              <th>Trek</th>
              <th>Location</th>
              <th>Start</th>
              <th>End</th>
              <th>Booked On</th>
              <th>Status</th>
              <th>Payment</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in bookingList" :key="b.bookingid">
              <td v-text="b.trekname"></td>
              <td v-text="b.location"></td>
              <td v-text="b.startdate"></td>
              <td v-text="b.enddate"></td>
              <td v-text="b.bookingdate"></td>
              <td v-text="b.status"></td>
              <td v-text="b.paymentstatus"></td>
              <td>
                <button v-if="b.status === 'Booked'"
                        class="action-btn del"
                        @click="cancelBooking(b.bookingid)">Cancel</button>
                <span v-else style="color:#999;">—</span>
              </td>
            </tr>
            <tr v-if="bookingList.length === 0">
              <td colspan="8">No bookings yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Profile -->
    <div v-if="tab=='profile'">
      <h1 class="heading">My Profile</h1>

      <div class="content-box" style="max-width:480px;">
        <label>Name</label>
        <input v-model="profile.name" placeholder="Name" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:12px;">

        <label>Phone</label>
        <input v-model="profile.phone" placeholder="Phone" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:12px;">

        <label>Gender</label>
        <select v-model="profile.gender" style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:12px;">
          <option>Male</option>
          <option>Female</option>
          <option>Other</option>
        </select>

        <label>New Password <span style="color:#aaa; font-size:12px;">(leave blank to keep current)</span></label>
        <input type="password" v-model="profile.newpassword" placeholder="New Password"
               style="width:100%; padding:10px; border:1px solid #ccc; border-radius:8px; margin-bottom:16px;">

        <p v-if="profileMsg" style="color:green; margin-bottom:10px;" v-text="profileMsg"></p>

        <button class="btn-save" @click="saveProfile()" style="width:100%; padding:10px; border:none; border-radius:8px; cursor:pointer;">Save Profile</button>
      </div>
    </div>

    <!-- Trek Detail Modal -->
    <div class="modal-overlay" :class="{ active: showDetail }">
      <div class="modal-box">
        <h3 v-text="detail.trekname"></h3>
        <img v-if="detail.images && detail.images.length"
             :src="detail.images[0]"
             style="width:100%; height:180px; object-fit:cover; border-radius:8px; margin-bottom:12px;">
        <p><b>Location:</b> <span v-text="detail.location"></span></p>
        <p><b>Difficulty:</b> <span v-text="detail.difficulty"></span></p>
        <p><b>Duration:</b> <span v-text="detail.durationdays + ' days'"></span></p>
        <p><b>Price:</b> ₹<span v-text="detail.price"></span></p>
        <p><b>Seats Available:</b> <span v-text="detail.available_seats"></span></p>
        <p><b>Start:</b> <span v-text="detail.startdate"></span></p>
        <p><b>End:</b> <span v-text="detail.enddate"></span></p>
        <p v-if="detail.description"><b>Description:</b> <span v-text="detail.description"></span></p>
        <p v-if="detail.instructions"><b>Instructions:</b> <span v-text="detail.instructions"></span></p>
        <div class="modal-actions">
          <button class="btn-save" @click="bookTrek(detail.trekid); showDetail=false"
                  :disabled="detail.available_seats === 0"
                  v-text="detail.available_seats === 0 ? 'Fully Booked' : 'Book Now'"></button>
          <button class="btn-cancel" @click="showDetail=false">Close</button>
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
      tab: 'home',
      dashName: '',
      stats: { active_bookings: 0, completed_treks: 0, cancelled_bookings: 0, recent: [] },
      trekList: [],
      bookingList: [],
      search: '',
      filterDifficulty: '',
      filterLocation: '',
      filterDuration: '',
      bookingMsg: '',
      bookingSuccess: false,
      profile: { name: '', phone: '', gender: '', newpassword: '' },
      profileMsg: '',
      detail: {},
      showDetail: false,
    }
  },
  mounted() {
    this.loadDashboard()
    this.loadTreks()
  },
  methods: {
    async loadDashboard() {
      const data = await apiFetch('/user/dashboard')
      if (data.success) {
        this.dashName = data.name
        this.stats = {
          active_bookings: data.active_bookings,
          completed_treks: data.completed_treks,
          cancelled_bookings: data.cancelled_bookings,
          recent: data.recent,
        }
      }
    },
    async loadTreks() {
      let url = '/user/treks?search=' + encodeURIComponent(this.search)
      if (this.filterDifficulty) url += '&difficulty=' + this.filterDifficulty
      if (this.filterLocation) url += '&location=' + encodeURIComponent(this.filterLocation)
      if (this.filterDuration) url += '&duration=' + encodeURIComponent(this.filterDuration)
      const data = await apiFetch(url)
      if (data.success) this.trekList = data.treks
    },
    async bookTrek(id) {
      const data = await apiFetch('/user/book/' + id, { method: 'POST' })
      this.bookingMsg = data.message
      this.bookingSuccess = data.success
      if (data.success) {
        await this.loadTreks()
        await this.loadDashboard()
        setTimeout(() => { this.bookingMsg = '' }, 4000)
      }
    },
    openTrekDetail(trek) {
      this.detail = trek
      this.showDetail = true
    },
    async loadBookings() {
      const data = await apiFetch('/user/bookings')
      if (data.success) this.bookingList = data.bookings
    },
    async cancelBooking(id) {
      if (!confirm('Cancel this booking?')) return
      const data = await apiFetch('/user/bookings/' + id + '/cancel', { method: 'PUT' })
      alert(data.message)
      if (data.success) {
        await this.loadBookings()
        await this.loadDashboard()
      }
    },
    async loadProfile() {
      const data = await apiFetch('/user/profile')
      if (data.success) {
        this.profile = { ...data.profile, newpassword: '' }
      }
    },
    async saveProfile() {
      const payload = { name: this.profile.name, phone: this.profile.phone, gender: this.profile.gender }
      if (this.profile.newpassword) payload.password = this.profile.newpassword
      const data = await apiFetch('/user/profile', { method: 'PUT', json: payload })
      this.profileMsg = data.message
      setTimeout(() => { this.profileMsg = '' }, 3000)
    },
    async exportBookings() {
      const res = await apiFetch('/user/export', { raw: true })
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'my_bookings.csv'
      a.click()
    },
  },
}
</script>
