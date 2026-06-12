<template>
  <div class="dashboard">
    <h1 class="heading">Notifications</h1>

    <div class="content-box">
      <p v-if="notifications.length === 0" style="color:#888; padding: 16px;">No notifications yet.</p>

      <table v-else>
        <thead>
          <tr>
            <th>Title</th>
            <th>Message</th>
            <th>Date</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in notifications" :key="n.notificationid"
              :style="n.isread ? 'opacity:0.6;' : 'font-weight:bold;'">
            <td v-text="n.title"></td>
            <td style="white-space: pre-wrap; max-width: 400px;" v-text="n.message"></td>
            <td v-text="n.created_at"></td>
            <td>
              <span :class="n.isread ? 'badge-completed' : 'badge-active'"
                    v-text="n.isread ? 'Read' : 'Unread'"></span>
            </td>
            <td>
              <button v-if="!n.isread" class="action-btn edit"
                      @click="markRead(n.notificationid)">Mark Read</button>
            </td>
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
      notifications: [],
    }
  },
  async mounted() {
    await this.loadNotifications()
  },
  methods: {
    async loadNotifications() {
      const data = await apiFetch('/admin/notifications')
      if (data.success) this.notifications = data.notifications
    },
    async markRead(nid) {
      await apiFetch('/admin/notifications/' + nid + '/read', { method: 'PUT' })
      await this.loadNotifications()
    },
  },
}
</script>
