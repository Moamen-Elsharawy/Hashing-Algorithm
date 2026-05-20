# AETHER SHIELD // SECURE AUTHENTICATION SYSTEM
**نظام درع الأثير - نظام مصادقة وتشفير آمن**

---
*Choose your language / اختر لغتك:*
- 🌍 [English Documentation](#english-documentation)
- 🇸🇦 [الوثائق باللغة العربية](#arabic-documentation)

---

<a id="english-documentation"></a>
# 🌍 English Documentation

## 1. Introduction & Objectives
**Aether Shield** is a robust, Python-based secure authentication system designed to demonstrate and implement industry-standard cryptographic best practices. The primary objective of this project is to protect user credentials and mitigate common vulnerabilities found in standard authentication flows.

**Key Security Concepts Implemented:**
*   **Hashing vs. Encryption:** Storing passwords using irreversible one-way cryptographic hashes instead of plaintext or two-way encryption.
*   **Rainbow Table Defense:** Using unique, cryptographically secure 16-byte random **Salts** for each user to neutralize pre-computed dictionary attacks.
*   **Timing Attack Mitigation:** Utilizing constant-time string comparisons (`secrets.compare_digest`) for password hashes and session tokens to prevent attackers from deducing secrets via response time analysis.
*   **Brute-Force & Credential Stuffing Defense:** Implementing a dynamic **Lockout Policy** that temporarily disables an account after 3 consecutive failed login or recovery attempts.
*   **Modern Cryptography:** Supporting multiple advanced password hashing engines including `PBKDF2`, `bcrypt`, and the state-of-the-art memory-hard `Argon2id`.

## 2. System Architecture & Components
The application follows a modular design, separating the web server interface from the cryptographic core logic.

*   **`app.py` (Web Server & Routing):** 
    The main entry point using the Flask web framework. It defines API endpoints (`/api/login`, `/api/register`, etc.), handles HTTP requests/responses, and manages secure HTTPOnly cookies for session tracking. It also seeds the database with default accounts on startup.
*   **`auth_manager.py` (Core Security Engine):** 
    The heart of the project. It handles all database I/O, cryptographic hashing, session management in memory (`ACTIVE_SESSIONS`), and audit logging. 
*   **`verify_system.py` (Integration Testing):** 
    An automated test suite designed to run comprehensive security checks, including verifying that no plaintext passwords leak into the database, testing lockout expiration, and verifying session invalidation.
*   **`users.json` & `audit_log.json`:** 
    Local JSON files acting as the persistent database for user accounts (storing salts, algorithm types, and hashes) and security audit trails.
*   **`templates/` & `static/`:** 
    The Frontend components (HTML, CSS, JavaScript) that interact with the backend API to provide a seamless user interface and an interactive admin dashboard.

## 3. User Roles (RBAC)
The system enforces Role-Based Access Control with two distinct privilege levels:

*   **User Role:**
    *   Secure registration and login.
    *   Secure logout (invalidating the active session token).
    *   Password recovery using a securely hashed security question and answer.
*   **Admin Role:**
    *   Access to a restricted Admin Dashboard.
    *   View all registered users and their configurations.
    *   Manually unlock accounts that were disabled due to failed attempts.
    *   Elevate or demote user roles.
    *   Delete user accounts.
    *   View chronological Audit Logs of all authentication events in the system.

## 4. Technical Details & Functions Explained

### A. Built-in Functions & External Libraries
*   `hashlib.pbkdf2_hmac`: A Python built-in function used to generate a secure hash by applying a pseudo-random function iteratively (e.g., 100,000 iterations), slowing down cracking attempts.
*   `secrets.compare_digest`: A critical built-in security function. It compares two strings character-by-character without exiting early upon finding a mismatch. This constant-time execution prevents **Timing Attacks**.
*   `secrets.token_hex` & `secrets.token_urlsafe`: Used to generate unpredictable, cryptographically secure random values for Salts and 32-byte Session Tokens.
*   `bcrypt` & `argon2`: Third-party cryptographic libraries used as alternatives to PBKDF2. Argon2 is specifically designed to be memory-hard, making GPU-based cracking financially unfeasible.

### B. Custom Functions (in `auth_manager.py`)
*   **`hash_pbkdf2_sha256` / `hash_bcrypt` / `hash_argon2`:** Wrapper functions that handle the generation of the salt and the computation of the final hash string based on the chosen algorithm.
*   **`register_user`:** Validates inputs, selects the hashing algorithm, hashes both the password and the security answer, initializes lockout counters, and writes the record to `users.json`.
*   **`login_user`:** Checks if the user is currently locked out. If not, it retrieves the user's salt, hashes the incoming password, and compares it to the stored hash using `compare_digest`. On failure, it increments the attempt counter and triggers a 30-second lockout upon 3 failures. On success, it generates a session token.
*   **`validate_session` & `logout_session`:** Manages the `ACTIVE_SESSIONS` dictionary, verifying token validity/expiration, and securely purging tokens upon logout.
*   **`verify_reset_answer_and_change_password`:** Securely hashes the provided security answer and compares it to the stored answer hash. If correct, it generates a new salt and hash for the new password.
*   **Admin Functions (`admin_unlock_user`, `admin_change_role`, etc.):** Functions restricted by the `require_auth` decorator in `app.py`. They manipulate the user database and generate logs using `log_event`.

---

<a id="arabic-documentation"></a>
# 🇸🇦 الوثائق باللغة العربية

## 1. مقدمة عن المشروع وأهدافه
**درع الأثير (Aether Shield)** هو نظام مصادقة آمن (Secure Authentication System) مبني بلغة بايثون، صُمم لتوضيح وتطبيق أفضل الممارسات الأمنية المعيارية في الصناعة. الهدف الرئيسي من هذا المشروع هو حماية بيانات الاعتماد (كلمات المرور) وتأمين النظام ضد الثغرات الأمنية الشائعة.

**المفاهيم الأمنية الأساسية المطبقة:**
*   **التشفير أحادي الاتجاه (Hashing):** حفظ كلمات المرور باستخدام دوال التجزئة غير القابلة للعكس بدلاً من حفظها كنصوص عادية أو تشفيرها بطرق قابلة للعكس (Encryption).
*   **الحماية من جداول قوس قزح (Rainbow Tables):** استخدام "ملح" (Salt) عشوائي وآمن التشفير بحجم 16 بايت لكل مستخدم لجعل الهجمات المعدة مسبقاً مستحيلة.
*   **منع هجمات التوقيت (Timing Attacks):** استخدام مقارنات ذات وقت التنفيذ الثابت (`secrets.compare_digest`) عند التحقق من كلمات المرور وتوكن الجلسات، لمنع المهاجم من استنتاج الكلمات الصحيحة بناءً على وقت استجابة الخادم.
*   **الحماية من هجمات التخمين (Brute-Force):** تطبيق سياسة حظر ذكية (Lockout Policy) توقف الحساب مؤقتاً بعد 3 محاولات تسجيل دخول أو استرداد خاطئة.
*   **التشفير الحديث:** دعم خوارزميات التشفير المتقدمة مثل `PBKDF2`، و `bcrypt`، والخوارزمية الأحدث المستهلكة للذاكرة `Argon2id` لمنع هجمات كروت الشاشة (GPUs).

## 2. هيكلية النظام ومكوناته
يعتمد التطبيق على هيكلية معمارية معيارية تفصل بين واجهة الخادم والمنطق الأمني.

*   **`app.py` (خادم الويب والمسارات):** 
    نقطة الإدخال الرئيسية باستخدام إطار العمل `Flask`. يقوم بتعريف مسارات الـ API (مثل `/api/login`)، والتعامل مع طلبات HTTP، وإدارة ملفات الارتباط (Cookies) من نوع HTTPOnly لتتبع الجلسات بشكل آمن. كما يقوم بإنشاء حسابات افتراضية عند التشغيل الأول.
*   **`auth_manager.py` (المحرك الأمني الأساسي):** 
    قلب المشروع النابض. يتعامل مع قراءة وكتابة قواعد البيانات، خوارزميات التشفير، وإدارة الجلسات في الذاكرة الحية (`ACTIVE_SESSIONS`)، وتسجيل الأحداث (Audit Logging).
*   **`verify_system.py` (اختبارات التكامل):** 
    ملف لاختبار النظام بشكل آلي (Integration Tests) للتأكد من عدم وجود كلمات مرور غير مشفرة، والتأكد من تفعيل سياسة الحظر بشكل صحيح، وعملية إبطال الجلسات عند تسجيل الخروج.
*   **`users.json` و `audit_log.json`:** 
    ملفات JSON تمثل قاعدة البيانات المحلية لحفظ بيانات المستخدمين (مثل نوع التشفير، الـ Salt، الـ Hash) وسجلات الأحداث الأمنية.
*   **مجلدات `templates/` و `static/`:** 
    مكونات الواجهة الأمامية (HTML, CSS, JavaScript) التي تتواصل مع الـ API لتقديم واجهة مستخدم سلسة ولوحة تحكم تفاعلية للمسؤول.

## 3. أدوار المستخدمين (RBAC)
يفرض النظام التحكم في الوصول بناءً على الأدوار، ويحتوي على مستويين من الصلاحيات:

*   **صلاحيات المستخدم العادي (User):**
    *   إنشاء حساب جديد وتسجيل الدخول بشكل آمن.
    *   تسجيل الخروج (والذي يقوم بحذف التوكن بشكل آمن لمنع اختراق الجلسة).
    *   استعادة كلمة المرور عبر سؤال الأمان (الذي يُشفر ولا يحفظ كنص عادي).
*   **صلاحيات المسؤول (Admin):**
    *   الوصول إلى لوحة تحكم الإدارة (Admin Dashboard).
    *   عرض جميع المستخدمين المسجلين وتفاصيل التشفير الخاصة بهم.
    *   فك حظر الحسابات المقفلة يدوياً.
    *   تغيير أدوار المستخدمين (ترقية أو تخفيض).
    *   حذف حسابات المستخدمين.
    *   استعراض سجلات التدقيق (Audit Logs) لمعرفة تفاصيل كل حركة تسجيل أو دخول في النظام.

## 4. التفاصيل التقنية وطريقة عمل الدوال

### أ. الدوال المدمجة والمكتبات (Built-in Functions & Libraries)
*   **`hashlib.pbkdf2_hmac`:** دالة مدمجة في بايثون لإنشاء تجزئة (Hash) قوية عبر عمليات تكرارية (Iterations)، مما يطيل من وقت المعالجة لإحباط هجمات التخمين.
*   **`secrets.compare_digest`:** دالة أمنية حاسمة. تقارن بين سلسلتين نصيتين حرفاً بحرف ولا تتوقف عند أول حرف خاطئ. هذا يضمن أن وقت تنفيذ الدالة ثابت دائماً (Constant-Time) مما يمنع هجمات التوقيت (Timing Attacks).
*   **`secrets.token_hex` و `secrets.token_urlsafe`:** لإنشاء بيانات عشوائية آمنة جداً تستخدم كـ Salt أو كرموز جلسات (Session Tokens) بحجم 32 بايت.
*   **`bcrypt` و `argon2`:** مكتبات خارجية متميزة تعتبر المعيار الذهبي لتشفير كلمات المرور. تتميز `argon2` باستهلاكها العالي للذاكرة (Memory-Hard) مما يُفشل محاولات الكسر باستخدام كروت الشاشة.

### ب. الدوال المخصصة (Custom Functions داخل `auth_manager.py`)
*   **`hash_pbkdf2_sha256` / `hash_bcrypt` / `hash_argon2`:** دوال مساعدة تُغلف عملية التشفير وتوليد الـ Salt وترجع النص المشفر النهائي لحفظه في النظام.
*   **`register_user`:** الدالة المسؤولة عن التسجيل. تتحقق من المدخلات، وتختار نوع التشفير، ثم تشفر كلاً من "كلمة المرور" و"إجابة سؤال الأمان"، وتهيئ إعدادات الحظر قبل الحفظ في ملف `users.json`.
*   **`login_user`:** دالة تسجيل الدخول. تتأكد أولاً من عدم إيقاف الحساب. إذا لم يكن موقوفاً، تقوم بجلب الـ Salt المحفوظ وتشفر الباسورد المدخل وتقارنه باستخدام `compare_digest`. عند الفشل 3 مرات يُقفل الحساب لـ 30 ثانية، وعند النجاح يتم إنشاء رمز جلسة فريد.
*   **`validate_session` و `logout_session`:** تدير هذه الدوال قاموس الجلسات النشطة (`ACTIVE_SESSIONS`)، وتتحقق من صلاحية الجلسة، وتحذفها نهائياً عند تسجيل الخروج.
*   **`verify_reset_answer_and_change_password`:** تقوم بتشفير الإجابة المدخلة لسؤال الأمان ومقارنتها بالإجابة المشفرة المحفوظة بطريقة التوقيت الثابت. عند المطابقة يتم تحديث كلمة المرور وتغيير الـ Salt.
*   **دوال المسؤول (`admin_unlock_user`، `admin_change_role` وغيرها):** دوال لتعديل خصائص المستخدمين في ملف قاعدة البيانات، ولا يتم تنفيذها إلا إذا كانت صلاحية الجلسة "admin". تسجل هذه الدوال أعمالها عبر استدعاء دالة `log_event`.
