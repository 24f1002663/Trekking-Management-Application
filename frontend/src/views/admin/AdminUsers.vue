<template>
  <div class="dashboard">
    <div class="page-actions">
      <h1 class="heading">User Management</h1>
      <input class="search-box" type="text" v-model="searchQuery"
             @input="searchUsers()" placeholder="Search users by name or email...">
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
          <tr v-for="u in userList" :key="u.userid">
            <td v-text="u.userid"></td>
            <td v-text="u.name"></td>
            <td v-text="u.email"></td>
            <td v-text="u.phone || '-'"></td>
            <td v-text="u.gender"></td>
            <td>
              <span :class="u.status === 'active' ? 'badge-active' : 'badge-closed'"
                    v-text="u.status"></span>
            </td>
            <td>
              <button v-if="u.status === 'active'" class="action-btn del"
                      @click="blacklistUser(u.userid)">Blacklist</button>
              <button v-else class="action-btn edit"
                      @click="activateUser(u.userid)">Activate</button>
            </td>
          </tr>
          <tr v-if="userList.length === 0">
            <td colspan="7">No users found.</td>
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
      userList: [],
      searchQuery: '',
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      const data = await apiFetch('/admin/users')
      if (data.success) this.userList = data.users
    },
    async searchUsers() {
      if (!this.searchQuery.trim()) {
        await this.loadUsers()
        return
      }
      const data = await apiFetch('/admin/users/search/' + encodeURIComponent(this.searchQuery))
      if (data.success) this.userList = data.users
    },
    async blacklistUser(id) {
      if (!confirm('Blacklist this user?')) return
      const data = await apiFetch('/admin/users/' + id + '/blacklist', { method: 'PUT' })
      alert(data.message)
      await this.loadUsers()
    },
    async activateUser(id) {
      if (!confirm('Activate this user?')) return
      const data = await apiFetch('/admin/users/' + id + '/unblacklist', { method: 'PUT' })
      alert(data.message)
      await this.loadUsers()
    },
  },
}
</script>
