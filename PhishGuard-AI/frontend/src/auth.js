const AUTH_KEY = "phishguard_authenticated";

export function isAuthenticated() {
  return sessionStorage.getItem(AUTH_KEY) === "true";
}

export function loginUser() {
  sessionStorage.setItem(AUTH_KEY, "true");
}

export function logoutUser() {
  sessionStorage.removeItem(AUTH_KEY);
}
