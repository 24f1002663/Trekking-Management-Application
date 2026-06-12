<template>
  <div class="dashboard">
    <div class="page-actions">
      <h1 class="heading">Staff Management</h1>
      <button class="add-btn" @click="openAdd()">+ Add Staff</button>
    </div>

    <div class="content-box">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Gender</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staffList" :key="s.userid">
            <td v-text="s.userid"></td>
            <td v-text="s.name"></td>
            <td v-text="s.email"></td>
            <td v-text="s.phone || '-'"></td>
            <td v-text="s.gender"></td>
            <td>
              <select v-model="s.status" @change="changeStatus(s.userid, s.status)">
                <option value="active">Active</option>
                <option value="blacklisted">Blacklisted</option>
              </select>
            </td>
            <td>
              <button class="action-btn edit" @click="openEdit(s)">Edit</button>
              <button class="action-btn del" @click="deleteStaff(s.userid)">Delete</button>
            </td>
          </tr>
          <tr v-if="staffList.length === 0">
            <td colspan="7">No staff found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add / Edit Modal -->
    <div class="modal-overlay" :class="{ active: showModal }">
      <div class="modal-box">
        <h3 v-if="editing">Edit Staff</h3>
        <h3 v-else>Add Staff</h3>

        <input v-model="form.name" placeholder="Name">
        <input v-model="form.email" placeholder="Email" :disabled="editing">
        <input type="password" v-model="form.password"
               :placeholder="editing ? 'New Password (leave blank to keep)' : 'Password'">
        <input v-model="form.phone" placeholder="Phone">

        <select v-model="form.gender">
          <option value="">Select Gender</option>
          <option>Male</option>
          <option>Female</option>
          <option>Other</option>
        </select>

        <p v-if="modalMsg" style="color:red; margin-top:8px;" v-text="modalMsg"></p>

        <div class="modal-actions">
          <button class="btn-save" @click="saveStaff()">Save</button>
          <button class="btn-cancel" @click="showModal = false">Cancel</button>
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
      staffList: [],
      showModal: false,
      editing: false,
      editingId: null,
      modalMsg: '',
      form: { name: '', email: '', password: '', phone: '', gender: '' },
    }
  },
  mounted() {
    this.loadStaff()
  },
  methods: {
    async loadStaff() {
      const data = await apiFetch('/admin/staff')
      if (data.success) this.staffList = data.staff
    },
    openAdd() {
      this.editing = false
      this.editingId = null
      this.modalMsg = ''
      this.form = { name: '', email: '', password: '', phone: '', gender: '' }
      this.showModal = true
    },
    openEdit(s) {
      this.editing = true
      this.editingId = s.userid
      this.modalMsg = ''
      this.form = { name: s.name, email: s.email, password: '', phone: s.phone || '', gender: s.gender }
      this.showModal = true
    },
    async saveStaff() {
      const url = this.editing ? '/admin/staff/' + this.editingId : '/admin/staff'
      const method = this.editing ? 'PUT' : 'POST'
      const data = await apiFetch(url, { method, json: this.form })
      if (data.success) {
        this.showModal = false
        await this.loadStaff()
      } else {
        this.modalMsg = data.message
      }
    },
    async deleteStaff(id) {
      if (!confirm('Delete this staff member?')) return
      const data = await apiFetch('/admin/staff/' + id, { method: 'DELETE' })
      alert(data.message)
      await this.loadStaff()
    },
    async changeStatus(id, status) {
      const url = status === 'blacklisted'
        ? '/admin/staff/' + id + '/blacklist'
        : '/admin/staff/' + id + '/unblacklist'
      const data = await apiFetch(url, { method: 'PUT' })
      alert(data.message)
      await this.loadStaff()
    },
  },
}
</script>
