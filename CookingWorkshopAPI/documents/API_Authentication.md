[[_TOC_]]

# login

<pre>
POST /api/v1/auth/login
</pre>

Parameters

| Name     | Data Type | Required | Default Value | Description           |
| -------- | --------- | -------- | ------------- | --------------------- |
| email    | text      | true     | null          | email of the user.    |
| password | text      | true     | null          | password of the user. |

Request

```
{
    "email": "hello@example.com",
    "password": "VerySafePassword0909"
}
```

Response

```
Status: 200 OK
{
    "id": 1,
    "first_name": "Zahra",
    "last_name": "Alizadeh",
    "email": "hello@example.com",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "auth_token": "34303fc8c5a686f2e21b89a3feff4763abab5f7e",
    "last_login": "2020-08-12T04:19:49.793463+04:30"
}


Status: 400 Bad Request
{
    "en": "Invlid username/password!",
    "fa": "نام کاربری یا کلمه عبور اشتباه است!"
}
```

# Register

<pre>
POST /api/v1/auth/register
</pre>

Parameters

| Name       | Data Type | Required | Default Value | Description             |
| ---------- | --------- | -------- | ------------- | ----------------------- |
| email      | text      | true     | null          | email of the user.      |
| password   | text      | true     | null          | password of the user.   |
| first_name | text      | false    | ""            | first name of the user. |
| last_name  | text      | false    | ""            | last name of the user.  |

Request

```
{
    "email": "hello@example.com",
    "password": "VerySafePassword0909",
    "first_name": "John",
    "last_name": "Howley",
}
```

Response

```
Status: 201 Created
{
    "en": "Registration successful.A confirmation message has been sent to your registered email address.Please follow the instructions in the email to activate your account. Once you have activated your account you will be able to sign in to SDATA.",
    "fa": "ثبت نام با موفقیت انجام شد.یک ایمیل به آدرس اعلام شده توسط شما ارسال شده است. جهت فعالسازی حساب کاربری و ورود به ناحیه کاربری خود،روی لینک فعالسازی موجود در ایمیل دریافتی کلیک نمائید."
}


Status: 400 Bad Request
{
    "email": [
        "Email is already taken"
    ]
}
```

# Activate account

<pre>
POST /api/v1/auth/activate
</pre>

Parameters

| Name   | Data Type | Required | Default Value | Description             |
| ------ | --------- | -------- | ------------- | ----------------------- |
| uidb64 | text      | true     | null          | encoded id of the user. |
| token  | text      | true     | null          | token of the user.      |

Request

```
{
    "uidb64": "MzM",
    "token": "5j1-a005675ae3e7dbc0b934",
}
```

Response

```
Status: 200 OK
{
    "id": 2
    "first_name": "Zahra",
    "last_name": "Alizadeh",
    "email": "hello@example.com",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "auth_token": "34303fc8c5a686f2e21b89a3feff4763abab5f7e"
}


Status: 400 Bad Request
{
    "en": "Activation link is not valid",
    "fa": "لینک فعالسازی معتبر نیست!"
}
```

# Logout

<pre>
GET  /api/v1/auth/logout
POST /api/v1/auth/logout
</pre>

Response

```
Status: 200 OK
{
    "success": "Successfully logged out"
}
```

# Change Password

<pre>
POST /api/v1/auth/password_change (requires authentication)
</pre>

Parameters

| Name             | Description                   |
| ---------------- | ----------------------------- |
| current_password | Current password of the user. |
| new_password     | New password of the user.     |

Request

```
Headers:
{
    "Authorization": "token TOKEN_GENERATED_FOR_USER",
}

Body:
{
    "current_password": "NotSoSafePassword",
    "new_password": "VerySafePassword0909"
}
```

Response

```
Status: 204 No-Content

Status: 400 Bad Request
{
    "current_password": {
        "en": "Current password does not match",
        "fa": "کلمه عبور وارد شده معتبر نیست!"
    }
}

Status: 401 Unauthorized
{
    "detail": "Invalid token." OR "Authentication credentials were not provided."
}
```

# Forgot password

<pre>
POST /api/v1/auth/forgot_password
</pre>

Parameters

| Name  | Data Type | Required | Default Value | Description        |
| ----- | --------- | -------- | ------------- | ------------------ |
| email | text      | true     | null          | email of the user. |

Request

```
{
    "email": "hello@example.com",
}
```

Response

```
Status: 200 OK
{
    "en": "An email has been sent to the supplied email address.Follow the instruction in the email to reset your password",
    "fa": "ایمیلی به آدرس ایمیل ارائه شده ارسال شده است. برای بازنشانی کلمه عبور خود، دستورالعمل موجود در ایمیل را دنبال کنید."
}


Status: 400 Bad Request
{
    "email": [
        "This field may not be blank."
    ]
}

Status: 400 Bad Request
{
    "email": {
        "en": "There is no user with this email.",
        "fa": "کاربری با این ایمیل وجود ندارد."
    }
}
```

# Forgot password - verify user by email

<pre>
POST /api/v1/auth/forgot_password_done
</pre>

Parameters

| Name   | Data Type | Required | Default Value | Description             |
| ------ | --------- | -------- | ------------- | ----------------------- |
| uidb64 | text      | true     | null          | encoded id of the user. |
| token  | text      | true     | null          | token of the user.      |

Request

```
{
    "uidb64": "MzM",
    "token": "5j1-a005675ae3e7dbc0b934",
}
```

Response

```
Status: 200 OK
{
    "id": 33,
    "email": "zahraa.alizadeh@outlook.com",
    "first_name": "Zahra",
    "last_name": "Alizadeh",
    "is_active": false,
    "is_staff": false,
    "auth_token": "2aa6d0e020f249866dc5a661465725ef236b7ff6",
    "last_login": null
}


Status: 400 Bad Request
{
    "en": "Reset Password link is not valid",
    "fa": "لینک ارسال شده معتبر نیست!"
}
```

# Reset Password - after forgot password

<pre>
POST /api/v1/auth/password_change (requires authentication)
</pre>

Parameters

| Name         | Description               |
| ------------ | ------------------------- |
| new_password | New password of the user. |

Request

```
Headers:
{
    "Authorization": "token TOKEN_GENERATED_FOR_USER",
}

Body:
{
    "new_password": "VerySafePassword0909"
}
```

Response

```
Status: 204 No-Content

Status: 400 Bad Request
{
    "current_password": {
        "en": "Current password does not match",
        "fa": "کلمه عبور وارد شده معتبر نیست!"
    }
}

Status: 401 Unauthorized
{
    "detail": "Invalid token." OR "Authentication credentials were not provided."
}
```
