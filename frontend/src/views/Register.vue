<template>
  <div class="card">
    <h1>Create Account</h1>
    <p>Register as a Trekker</p>

    <div id="message">
      <div v-if="message" :class="messageType === 'success' ? 'success' : 'error'" v-text="message"></div>
    </div>

    <form @submit.prevent="handleRegister">
      <input type="text" v-model="name" class="form-control" placeholder="Full Name" required>
      <input type="email" v-model="email" class="form-control" placeholder="Email" required>
      <input type="password" v-model="password" class="form-control" placeholder="Password" required>
      <input type="text" v-model="phone" class="form-control" placeholder="Phone Number">
      <select v-model="gender" class="form-select" required>
        <option value="">Select Gender</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>
      <button type="submit" class="btn btn-success w-100">Register</button>
    </form>

    <div class="link">
      Already have an account?
      <router-link to="/">Login</router-link>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      phone: '',
      gender: '',
      message: '',
      messageType: '',
    }
  },
  methods: {
    async handleRegister() {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: this.name,
          email: this.email,
          password: this.password,
          phone: this.phone,
          gender: this.gender,
        }),
      })
      const data = await response.json()

      if (data.success) {
        this.message = 'Registration Successful! Redirecting...'
        this.messageType = 'success'
        setTimeout(() => this.$router.push('/'), 1500)
      } else {
        this.message = data.message
        this.messageType = 'error'
      }
    },
  },
}
</script>
