<template>
  <div class="dashboard">
    <div class="page-actions">
      <h1 class="heading">Trek Management</h1>
      <button class="add-btn" @click="openAdd()">+ Create Trek</button>
    </div>

    <div class="content-box">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Trek Name</th>
            <th>Location</th>
            <th>Difficulty</th>
            <th>Duration</th>
            <th>Price</th>
            <th>Seats</th>
            <th>Booked</th>
            <th>Assigned Staff</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in trekList" :key="t.trekid">
            <td v-text="t.trekid"></td>
            <td v-text="t.trekname"></td>
            <td v-text="t.location"></td>
            <td v-text="t.difficulty"></td>
            <td v-text="t.durationdays + ' days'"></td>
            <td v-text="'₹' + t.price"></td>
            <td v-text="t.seats"></td>
            <td v-text="t.bookedseats"></td>
            <td v-text="getStaffName(t.assignedstaffid)"></td>
            <td>
              <select v-model="t.status" @change="updateTrekStatus(t.trekid, t.status)">
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
                <option value="Started">Started</option>
                <option value="Completed">Completed</option>
              </select>
            </td>
            <td>
              <button class="action-btn edit" @click="openEdit(t)">Edit</button>
              <button class="action-btn del" @click="deleteTrek(t.trekid)">Delete</button>
              <button class="action-btn assign" @click="openAssign(t)">Assign Staff</button>
              <button class="action-btn" @click="openImages(t)">Images</button>
            </td>
          </tr>
          <tr v-if="trekList.length === 0">
            <td colspan="11">No treks found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create / Edit Trek Modal -->
    <div class="modal-overlay" :class="{ active: showTrekModal }">
      <div class="modal-box">
        <h3 v-if="editing">Edit Trek</h3>
        <h3 v-else>Create Trek</h3>

        <input v-model="form.trekname" placeholder="Trek Name">
        <input v-model="form.location" placeholder="Location">

        <select v-model="form.difficulty">
          <option value="">Difficulty</option>
          <option>Easy</option>
          <option>Medium</option>
          <option>Hard</option>
        </select>

        <input type="number" v-model="form.durationdays" placeholder="Duration (days)">
        <input type="number" v-model="form.price" placeholder="Price (₹)">
        <input type="number" v-model="form.seats" placeholder="Total Seats">
        <input type="date" v-model="form.startdate">
        <input type="date" v-model="form.enddate">

        <select v-model="form.allowedgender">
          <option value="">Allowed Gender</option>
          <option>Male</option>
          <option>Female</option>
          <option>Coed</option>
        </select>

        <textarea v-model="form.description" placeholder="Description"></textarea>
        <textarea v-model="form.instructions" placeholder="Instructions"></textarea>

        <p v-if="modalMsg" style="color:red; margin-top:6px;" v-text="modalMsg"></p>

        <div class="modal-actions">
          <button class="btn-save" @click="saveTrek()">Save</button>
          <button class="btn-cancel" @click="showTrekModal = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div class="modal-overlay" :class="{ active: showAssignModal }">
      <div class="modal-box">
        <h3>Assign Staff</h3>
        <p style="margin-bottom:10px;">Trek: <b v-text="assignTrekName"></b></p>

        <select v-model="assignStaffId">
          <option value="">Select Staff</option>
          <option v-for="s in staffList" :key="s.userid" :value="s.userid" v-text="s.name"></option>
        </select>

        <p v-if="assignMsg" style="color:red; margin-top:8px;" v-text="assignMsg"></p>

        <div class="modal-actions">
          <button class="btn-save" @click="saveAssign()">Assign</button>
          <button class="btn-cancel" @click="showAssignModal = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Images Modal -->
    <div class="modal-overlay" :class="{ active: showImagesModal }">
      <div class="modal-box">
        <h3><span v-text="selectedTrekName"></span> — Images</h3>

        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px;">
          <div v-for="img in trekImages" :key="img.imageid" style="position:relative;">
            <img :src="img.imageurl" style="width:120px; height:90px; object-fit:cover; border-radius:6px;">
            <button @click="deleteImage(img.imageid)"
                    style="position:absolute; top:2px; right:2px; background:rgba(200,0,0,0.8); color:white; border:none; border-radius:4px; padding:2px 6px; cursor:pointer; font-size:11px;">
              ✕
            </button>
          </div>
          <p v-if="trekImages.length === 0" style="color:#888;">No images uploaded yet.</p>
        </div>

        <label style="font-size:13px; color:#555;">Upload Image:</label>
        <input type="file" ref="imageInput" accept="image/*" style="margin-bottom:12px;">

        <div class="modal-actions">
          <button class="btn-save" @click="uploadImage()">Upload</button>
          <button class="btn-cancel" @click="showImagesModal = false">Close</button>
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
      trekList: [],
      staffList: [],
      showTrekModal: false,
      showAssignModal: false,
      showImagesModal: false,
      editing: false,
      editingId: null,
      selectedTrekId: null,
      selectedTrekName: '',
      assignTrekId: null,
      assignTrekName: '',
      assignStaffId: '',
      assignMsg: '',
      trekImages: [],
      modalMsg: '',
      form: {
        trekname: '', location: '', difficulty: '', durationdays: '',
        price: '', seats: '', startdate: '', enddate: '',
        allowedgender: '', description: '', instructions: '',
      },
    }
  },
  mounted() {
    this.loadTreks()
    this.loadStaff()
  },
  methods: {
    async loadTreks() {
      const data = await apiFetch('/admin/treks')
      if (data.success) this.trekList = data.treks
    },
    async loadStaff() {
      const data = await apiFetch('/admin/staff')
      if (data.success) this.staffList = data.staff
    },
    getStaffName(id) {
      const s = this.staffList.find((s) => s.userid == id)
      return s ? s.name : '-'
    },
    openAdd() {
      this.editing = false
      this.editingId = null
      this.modalMsg = ''
      this.form = {
        trekname: '', location: '', difficulty: '', durationdays: '',
        price: '', seats: '', startdate: '', enddate: '',
        allowedgender: '', description: '', instructions: '',
      }
      this.showTrekModal = true
    },
    openEdit(t) {
      this.editing = true
      this.editingId = t.trekid
      this.modalMsg = ''
      this.form = {
        trekname: t.trekname, location: t.location, difficulty: t.difficulty,
        durationdays: t.durationdays, price: t.price, seats: t.seats,
        startdate: t.startdate || '', enddate: t.enddate || '',
        allowedgender: t.allowedgender || 'Coed',
        description: t.description || '', instructions: t.instructions || '',
      }
      this.showTrekModal = true
    },
    async saveTrek() {
      const url = this.editing ? '/admin/treks/' + this.editingId : '/admin/treks'
      const method = this.editing ? 'PUT' : 'POST'
      const data = await apiFetch(url, { method, json: this.form })
      if (data.success) {
        this.showTrekModal = false
        await this.loadTreks()
      } else {
        this.modalMsg = data.message
      }
    },
    async deleteTrek(id) {
      if (!confirm('Delete this trek?')) return
      const data = await apiFetch('/admin/treks/' + id, { method: 'DELETE' })
      alert(data.message)
      await this.loadTreks()
    },
    openAssign(t) {
      this.assignTrekId = t.trekid
      this.assignTrekName = t.trekname
      this.assignStaffId = ''
      this.assignMsg = ''
      this.showAssignModal = true
    },
    async saveAssign() {
      if (!this.assignStaffId) {
        this.assignMsg = 'Please select a staff member.'
        return
      }
      const data = await apiFetch('/admin/treks/' + this.assignTrekId + '/assign', {
        method: 'PUT',
        json: { staffid: this.assignStaffId },
      })
      if (data.success) {
        this.showAssignModal = false
        await this.loadTreks()
      } else {
        this.assignMsg = data.message
      }
    },
    async updateTrekStatus(id, status) {
      const data = await apiFetch('/admin/treks/' + id + '/status', {
        method: 'PUT',
        json: { status },
      })
      if (!data.success) {
        alert(data.message)
        await this.loadTreks()
      }
    },
    async openImages(t) {
      this.selectedTrekId = t.trekid
      this.selectedTrekName = t.trekname
      this.trekImages = []
      this.showImagesModal = true
      await this.loadImages()
    },
    async loadImages() {
      const data = await apiFetch('/admin/treks/' + this.selectedTrekId + '/images')
      if (data.success) this.trekImages = data.images
    },
    async uploadImage() {
      const file = this.$refs.imageInput.files[0]
      if (!file) {
        alert('Select an image first.')
        return
      }
      const formData = new FormData()
      formData.append('image', file)
      const data = await apiFetch('/admin/treks/' + this.selectedTrekId + '/images', {
        method: 'POST',
        body: formData,
      })
      alert(data.message)
      if (data.success) await this.loadImages()
    },
    async deleteImage(id) {
      if (!confirm('Delete this image?')) return
      // Correct route: /admin/treks/<trekid>/images/<imageid>
      const data = await apiFetch(
        '/admin/treks/' + this.selectedTrekId + '/images/' + id,
        { method: 'DELETE' }
      )
      if (data.success) await this.loadImages()
    },
  },
}
</script>
