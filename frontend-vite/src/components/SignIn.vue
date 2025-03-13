<script>
export default {
  name: "SignIn"
}
</script>

<script setup>
import HelloWorld from './components/HelloWorld.vue'
import RecoverPassword from './components/RecoverPassword.vue'
import {ref} from "vue";


const email = ref()
const password = ref()
const submitted = ref(false)
const submit = () => {
  submitted.value = true;
}
const validEmail = ref(false)
const keepMeLoggedIn = ref(false)
const validateEmail = (email) => {
  validEmail.value = email
  if(email) {
    let re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    validEmail.value = re.test(email);
  }

}
</script>

<template>
<!--  <h1 class="mb-3 text-opacity-50 text-5xl font-bold tracking-tight text-gray-900">BFC procurement tool</h1>-->
  <div class="min-w-[500px]">
<!--    <h1 class="mb-3 text-2lg font-bold tracking-tight text-gray-900 drop-shadow-2xl shadow-md">PBFC</h1>-->
    <div class="mx-auto bg-white rounded-xl  drop-shadow-2xl overflow-hidden ">
<!--    <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl md:min-w-">-->
      <div class="flex min-h-full flex-1 flex-col justify-center px-6 py-6 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-sm">
          <img class="mx-auto h-40 w-auto top-model" src="../assets/img/pixelcut-export1.png?color=green&shade=600" alt="Your Company" />
          <h1 class="mt-10 text-center text-4xl font-bold tracking-tight text-gray-900">Sign into PBFC</h1>
        </div>

        <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form class="space-y-6" action="#" method="POST" @submit.prevent="validateEmail(email)">
            <div class="h-16 mb-10">
              <label for="email" class="block text-sm/6 font-medium text-gray-900 text-left">Email address</label>
              <div class="mt-2">
                <input type="email" v-model="email" name="email" id="email" autocomplete="email"
                       class="peer/email drop-shadow-none shadow-none block w-full rounded-md bg-white px-3 py-1.5
                       text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300
                       placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2
                       focus:ring-green-600 focus:shadow-none focus:drop-shadow-none focus:outline-green-600
                       sm:text-sm/6 border-slate-300"
                       v-bind:class="{'text-pink-600': !validEmail && submitted,
                       'border-pink-500': !validEmail && submitted,
                       'outline-pink-600': !validEmail && submitted,
                       'focus:outline-pink-600': !validEmail && submitted,
                       'ring-pink-600': !validEmail && submitted,
                       'focus:ring-pink-600': !validEmail && submitted}" @change="validateEmail(email)"/>
                <p v-show="!validEmail && submitted" class="mt-2 text-pink-600 text-sm text-left">This field is required.</p>
              </div>
<!--              <div class="peer-[.is-dirty]:peer-required:block hidden">This field is required.</div>-->
            </div>
            <div class="h-16 mb-16">
              <div class="flex items-center justify-between">
                <label for="password" class="block text-sm/6 font-medium text-gray-900">Password</label>
                <div class="text-sm">
<!--                  <a href="#" class="font-semibold text-green-600 hover:text-green-500">Forgot password?</a>-->
                  <router-link to="/recover_password" class="font-semibold text-green-600 hover:text-green-500">Forgot Password</router-link>
                </div>
              </div>
              <div class="mt-2">
                <input type="password" v-model="password" name="password" id="password"
                       autocomplete="current-password" class="peer/password drop-shadow-none block
                        w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900
                        outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline
                        focus:outline-2 focus:-outline-offset-2 focus:outline-green-600 focus:ring-green-600
                        sm:text-sm/6 border-slate-300 "
                       v-bind:class="{'text-pink-600': !password && submitted,
                       'border-pink-500': !password && submitted,
                       'outline-pink-600': !password && submitted,
                       'focus:outline-pink-600': !password && submitted,
                       'ring-pink-600': !password && submitted,
                       'focus:ring-pink-600': !password && submitted}"/>
                <p v-show="!password && submitted" class="mt-2 text-pink-600 text-sm text-left ">This field is required.</p>
              </div>
<!--              <div class="peer-[.is-dirty]:peer-required:block hidden">This field is required.</div>-->
            </div>
            <div class="h-10 mt-30 pt-1">
              <div class="mt-2 md:text-left">
                <input type="checkbox" v-model="keepMeLoggedIn" name="checkbox" id="checkbox"
                       class="form-checkbox peer/checkbox drop-shadow-none checked:bg-green-600 outline-gray-300
                        focus:bg-green-600 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-green-600
                        focus:ring-green-600 sm:text-sm/6 border-slate-300  focus-visible:bg-green-600
                         hover:bg-green-600 checked:focus:bg-green-600 checked:hover:bg-green-600"/>
                 <label for="checkbox" class="ml-4 text-sm/6 font-medium text-gray-900">Keep me logged in</label>
              </div>

            </div>
            <div class="h-16">
              <button type="submit" @submit="submit()" @click="submit()"
                      class="flex w-full justify-center rounded-md bg-green-600 px-3 py-1.5 text-sm/6 font-semibold
                      text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2
                      focus-visible:outline-offset-2 focus-visible:outline-green-600 motion-safe:hover:-translate-x-0.5
                      motion-safe:transition"
                      v-bind:class="{'opacity-50': submitted, 'cursor-not-allowed': submitted}" style="outline: 4px auto green">

<!--                <svg v-if="submitted" class="animate-spin h-5 w-5 mr-3 ..." viewBox="0 0 24 24">-->
<!--                  &lt;!&ndash; ... &ndash;&gt;-->
<!--                </svg>-->
                <svg v-if="submitted" class="mr-2 w-4 text-gray-300 animate-spin" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"
                  width="24" height="24">
                  <path
                    d="M32 3C35.8083 3 39.5794 3.75011 43.0978 5.20749C46.6163 6.66488 49.8132 8.80101 52.5061 11.4939C55.199 14.1868 57.3351 17.3837 58.7925 20.9022C60.2499 24.4206 61 28.1917 61 32C61 35.8083 60.2499 39.5794 58.7925 43.0978C57.3351 46.6163 55.199 49.8132 52.5061 52.5061C49.8132 55.199 46.6163 57.3351 43.0978 58.7925C39.5794 60.2499 35.8083 61 32 61C28.1917 61 24.4206 60.2499 20.9022 58.7925C17.3837 57.3351 14.1868 55.199 11.4939 52.5061C8.801 49.8132 6.66487 46.6163 5.20749 43.0978C3.7501 39.5794 3 35.8083 3 32C3 28.1917 3.75011 24.4206 5.2075 20.9022C6.66489 17.3837 8.80101 14.1868 11.4939 11.4939C14.1868 8.80099 17.3838 6.66487 20.9022 5.20749C24.4206 3.7501 28.1917 3 32 3L32 3Z"
                    stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"></path>
                  <path
                    d="M32 3C36.5778 3 41.0906 4.08374 45.1692 6.16256C49.2477 8.24138 52.7762 11.2562 55.466 14.9605C58.1558 18.6647 59.9304 22.9531 60.6448 27.4748C61.3591 31.9965 60.9928 36.6232 59.5759 40.9762"
                    stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" class="text-gray-900">
                  </path>
                </svg>
                Sign in
<!--                <svg class="motion-reduce:hidden animate-spin" viewBox="0 0 24 24">&lt;!&ndash; ... &ndash;&gt;</svg>Sign in-->
              </button>
            </div>
          </form>

<!--          <p class="mt-10 text-center text-sm/6 text-gray-500">-->
<!--            Not a member?-->
<!--            {{ ' ' }}-->
<!--            <a href="#" class="font-semibold text-green-600 hover:text-green-500">Sign Up</a>-->
<!--          </p>-->
        </div>
      </div>
          <div class="md:-mr-48">
            <div class="md:flex-shrink-0">
      <!--        style="float: left"-->
    <!--          <img class="h-30 w-full object-cover md:h-full md:w-48 top-model" src="../src/assets/img/pixelcut-export1.png" alt="Man looking at item at a store" width="400">-->
            </div>
          </div>
        </div>
  </div>
  <div style="bottom: 3px;">
    <p class="mt-2 text-gray-500">© 2024 <a href="#" class="inline-block mt-1 text-lg anchor-green-500 hover:anchor-green-700 leading-tight font-medium te xt-black hover:underline">BFC SARL</a> All rights reserved.</p>
  </div>
<!--  <HelloWorld msg="Vite + Vue" />-->
</template>


<style scoped>

</style>