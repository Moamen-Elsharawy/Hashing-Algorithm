---
marp: true
theme: default
size: 16:9
transition: fade
---

<style>
/* Ultra-Modern Premium UI Typography - Light Mode */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;500&display=swap');

section {
  font-family: 'Outfit', sans-serif;
  background-color: #f8fafc;
  background-image: 
    radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08) 0%, transparent 50%);
  color: #334155;
  padding: 10px 60px 30px; /* Padding-top fixed to clear the absolute h2 */
  font-size: 22px; /* Smaller font size */
}

section.title-slide {
  /* padding: 30px 30px; */
}

h1 {
  font-size: 4.2em;
  font-weight: 800;
  background: linear-gradient(135deg, #7e22ce 0%, #4338ca 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-transform: uppercase;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

h2 {
  position: absolute;
  top: 30px;
  left: 60px;
  right: 60px;
  font-size: 1.8em;
  font-weight: 600;
  color: #0f172a;
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 0.2em;
  margin: 0;
}

h2::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, #8b5cf6, #3b82f6);
}

.title-subtitle {
  font-size: 2em;
  font-weight: 400;
  color: #475569;
  margin-top: 5px;
  margin-bottom: 15px; /* Minimized space */
}

.title-divider {
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, #8b5cf6, #3b82f6);
  margin-bottom: 25px; /* Minimized space */
  border-radius: 2px;
}

h3 {
  font-size: 1.4em;
  color: #1e293b;
  margin-bottom: 0.3em; /* Minimized space */
}

p, li {
  font-size: 1.1em;
  line-height: 1.4; /* Minimized vertical space */
  color: #475569;
}

li {
  margin-bottom: 0.2em; /* Minimized space */
}

/* Monospace Utilities */
.mono-top {
  font-family: 'Fira Code', monospace;
  font-size: 0.65em;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 30px; /* Minimized space */
}

.mono-bottom {
  font-family: 'Fira Code', monospace;
  font-size: 0.6em;
  color: #94a3b8;
  position: absolute;
  bottom: 20px;
  left: 60px;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 25px; /* Minimized space */
}

.tag {
  font-family: 'Fira Code', monospace;
  font-size: 0.7em;
  color: #7e22ce;
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

/* Two-column Layout for Title */
.title-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.left-col {
  flex: 6.5;
  padding-right: 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.right-col {
  flex: 3.5;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.right-col::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10%;
  bottom: 10%;
  width: 1px;
  background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.1), transparent);
}

.right-col svg {
  width: 85%;
  filter: drop-shadow(0 10px 15px rgba(99, 102, 241, 0.15));
}

/* Tables */
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-top: 10px;
  font-size: 0.9em;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

th, td {
  padding: 10px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

th {
  background-color: #f1f5f9;
  color: #334155;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8em;
  letter-spacing: 0.05em;
}

tr:last-child td {
  border-bottom: none;
}

code {
  background-color: rgba(236, 72, 153, 0.1);
  color: #db2777;
  padding: 0.2em 0.4em;
  border-radius: 6px;
  font-family: 'Fira Code', monospace;
  font-size: 0.85em;
  border: 1px solid rgba(236, 72, 153, 0.2);
}
.team-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.team-image-container {
  flex: 1;
  text-align: center;
}

.team-names-container {
  flex: 1.5;
  font-size: 1.2em;
  text-align: right;
  direction: rtl;
}

.team-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.thanks-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
}

.thanks-image {
  margin-top: 40px;
}

.thanks-questions {
  margin-top: 20px;
  color: #7e22ce;
  font-size: 2em;
  margin-bottom: 0;
}
</style>

<!-- _class: title-slide -->
<div class="title-layout">
<div class="left-col">
<div class="mono-top">AETHER SHIELD • Computers and Network Security • MAY 2026</div>
<h1>AETHER SHIELD</h1>
<div class="title-subtitle">Secure Authentication System</div>
<div class="title-divider"></div>
<p style="font-size: 1.25em; line-height: 1.4;">Technical presentation on enterprise-grade cryptographic security architecture featuring zero-knowledge authentication, memory-hard hashing, and constant-time verification.</p>

<div class="tag-container">
<span class="tag">[ Zero-Knowledge Auth ]</span>
<span class="tag">[ Memory-Hard Hashing ]</span>
<span class="tag">[ Constant-Time Verification ]</span>
</div>
</div>
<div class="right-col">
  <img src="presentation/assets/shield.svg" alt="shield" width="300" />
</div>
</div>
<!-- <div class="mono-bottom">AETHER SHIELD • Computers and Network Security • MAY 2026</div> -->

---

## Introduction & Core Objectives

The **Aether Shield** project implements industry-standard cryptographic best practices to protect user credentials and mitigate common authentication vulnerabilities.

**Core Security Concepts:**
- **Zero-Knowledge Architecture:** The 1system never knows or stores the actual password in plaintext.
- **Rainbow Table Defense:** Neutralization of pre-computed dictionary attacks via unique cryptographic Salts.
- **Timing Attack Mitigation:** Thwarting side-channel attacks using constant-time string comparisons.
- **Brute-Force Defense:** Dynamic Lockout Policies stopping automated credential stuffing attacks.
- **Modern Cryptography:** Integrating `PBKDF2`, `bcrypt`, and the memory-hard `Argon2id`.

---

## System Architecture

The application employs a modular design, decoupling the web interface from the core cryptographic engine to maintain a secure boundary.

- **`app.py` (Web Server & Routing):** 
  The Flask entry point. Handles HTTP requests, API endpoints (`/api/login`, `/api/register`), and manages secure `HTTPOnly` cookies for session tracking.
- **`auth_manager.py` (Security Engine):** 
  The cryptographic heart. Manages all hashing logic, in-memory session tracking (`ACTIVE_SESSIONS`), and comprehensive audit logging.
- **JSON Data Stores:** 
  Lightweight `users.json` and `audit_log.json` handle persistent account configurations (salts, hash algorithms, digests) and chronological security events.

---

## Role-Based Access Control (RBAC)

Aether Shield enforces strict access control through two distinct privilege tiers:

**1. User Privileges**
- Secure account registration, login, and safe logout (invalidating the active session token).
- Password recovery via securely hashed security questions.

**2. Admin Privileges**
- Access to a restricted, authenticated Admin Dashboard.
- View registered users and inspect their security configurations.
- Manually unlock accounts disabled by the automated lockout policy.
- Elevate or demote user roles, and delete anomalous accounts.
- Review chronological Audit Logs for intrusion detection.

---

## Encryption vs. Hashing

Understanding the fundamental mathematical differences is critical.

### Encryption (Two-Way)
- Obfuscates plaintext into ciphertext using an encryption key.
- **Reversible:** Can be decrypted back to plaintext with the correct key.
- **Flaw for Passwords:** If the database and the key are breached, all passwords are exposed instantly.

### Hashing (One-Way)
- Maps an input of any size to a fixed-size bit string (digest).
- **Irreversible:** Computationally infeasible to reverse engineer the plaintext.
- **Zero-Knowledge:** The server only stores the hash. During login, it hashes the input and compares it, never knowing the actual password.

---

## Rainbow Tables & Salting

### The Threat: Rainbow Tables
A Rainbow Table is a massive, precomputed database of password hashes. Attackers use it to perform high-speed lookups on stolen password hashes, instantly cracking common passwords.

### The Solution: Cryptographic Salting
A **salt** is a secure, random 16-byte sequence uniquely generated for every user.
- **Formula:** `Hash(Password + Salt) = Stored Hash`
- **Exploding the Keyspace:** Appending a unique salt means an attacker cannot use a single precomputed table for multiple users. They must compute a new table for every possible salt, which requires financially impossible computing power.

---

## Timing Attacks & Constant-Time Comparisons

### The Vulnerability: Standard `==` Operator
Standard string comparison evaluates character-by-character and uses **early-exit optimization** (it stops at the very first mismatched character). 
- *Leakage:* Attackers measure response times in microseconds. A longer response time indicates a longer matching prefix, allowing them to guess the secret character by character.

### The Defense: `secrets.compare_digest()`
Aether Shield uses constant-time comparison algorithms.
- Processes the entire sequence regardless of where a mismatch occurs.
- CPU cycles spent remain constant, eliminating measurable time differentials and neutralizing side-channel timing attacks entirely.

---

## Modern Hashing: bcrypt vs. Argon2

Why is standard **SHA-256** unacceptable for passwords? 
- **Speed:** Modern GPUs compute tens of billions of SHA-256 hashes per second, making offline brute-forcing trivial.

**Adaptive Alternatives:**
- **bcrypt:** Employs a configurable *Work Factor*. By increasing iterations, administrators intentionally slow down the hashing process (e.g., to ~100ms), dropping crack rates from billions to thousands per second.
- **Argon2 (Argon2id):** The state-of-the-art standard. It introduces **Memory-Hardness**. Computing an Argon2 hash requires significant RAM bandwidth, instantly starving highly parallel GPU and ASIC cores, erasing the hardware advantage.

---

## Cryptographic Algorithm Comparison Matrix

| Hashing Algorithm | Category | Iteration Control | Memory-Hardness | Resists GPU/ASIC Cracking | Production Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SHA-256** | Cryptographic Hash | None (Fixed) | None ($0$ RAM) | **No** (Vulnerable) | **UNACCEPTABLE** |
| **PBKDF2** | Key Derivation | Yes (Iterations) | None ($0$ RAM) | **Weak** (GPU parallelizable) | **Legacy / Minimum** |
| **bcrypt** | Password Hash | Yes (Work Factor) | Negligible | **Yes** (Strong CPU limits) | **Good** (Standard) |
| **Argon2id** | Modern KDF | Yes (Time Cost) | Yes (Memory Cost) | **Excellent** (Best-in-class) | **Exceptional** (Recommended) |

---

## Team Members

<div class="team-container">
<div class="team-image-container">
  <img src="presentation/assets/team.svg" alt="team" width="350" />
</div>
<div class="team-names-container" dir="rtl">
  <div class="team-grid">
    <div>1. محمد أحمد محمد عطية</div>
    <div>2. محمد أحمد محمد الجزار</div>
    <div>3. محمد خالد فتحي بدر</div>
    <div>4. محمد خالد محمد العبادي</div>
    <div>5. مؤمن أحمد طه الشعراوي</div>
  </div>
</div>
</div>

---

<div class="thanks-container">

# Thank You
**Aether Shield** successfully demonstrates that robust authentication requires layers of mathematical and architectural defenses.

  <img src="presentation/assets/thanks.svg" alt="thanks" height="220" class="thanks-image" />
  <h3 class="thanks-questions">Any Questions?</h3>

</div>

<!-- ---

## Future Enhancements

- **Biometric Integration:** Support for WebAuthn and hardware security keys.
- **Advanced Threat Intelligence:** Real-time analysis of authentication requests using ML models.
- **Decentralized Identity:** Exploring blockchain-based identity verification. -->
