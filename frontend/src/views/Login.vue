<template>
  <div class="card">
    <h1>Trek Management</h1>
    <p>Login to continue</p>

    <div id="message">
      <div v-if="message" :class="messageType === 'success' ? 'success' : 'error'" v-text="message"></div>
    </div>

    <form @submit.prevent="handleLogin">
      <input type="email" v-model="email" class="form-control" placeholder="Enter Email" required>
      <input type="password" v-model="password" class="form-control" placeholder="Enter Password" required>
      <button type="submit" class="btn btn-success w-100">Login</button>
    </form>

    <div class="link">
      Don't have an account?
      <router-link to="/register">Register</router-link>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      message: '',
      messageType: '',
    }
  },
  methods: {
    async handleLogin() {
      this.message = ''
      try {
        const response = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password }),
        })
        const data = await response.json()

        if (data.success) {
          localStorage.setItem('token', data.token)
          localStorage.setItem('userid', data.userid)
          localStorage.setItem('name', data.name)
          localStorage.setItem('role', data.role)

          this.message = data.message
          this.messageType = 'success'

          setTimeout(() => {
            if (data.role === 'admin') this.$router.push('/admindashboard')
            else if (data.role === 'staff') this.$router.push('/staffdashboard')
            else this.$router.push('/userdashboard')
          }, 1000)
        } else {
          this.message = data.message
          this.messageType = 'error'
        }
      } catch (error) {
        this.message = 'Unable to connect to the server.'
        this.messageType = 'error'
      }
    },
  },
}
</script>
