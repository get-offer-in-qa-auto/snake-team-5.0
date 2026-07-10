# TeamCity Postman Collection

## Files

- `teamcity-api-mvp.postman_collection.json` - collection with MVP API request chains.
- `teamcity-local.postman_environment.json` - optional environment for local TeamCity variables.

## Import

Option A: import only the collection.

The collection already contains collection variables, so requests can run after filling `teamcity_username` and `teamcity_password` in collection variables. Fill the `Current value` column in Postman, not only `Initial value`.

Option B: import collection + environment.

1. Import `teamcity-api-mvp.postman_collection.json`.
2. Import `teamcity-local.postman_environment.json`.
3. Select `TeamCity Local` in the environment dropdown.
4. Fill `teamcity_username` and `teamcity_password` in `Current value`.

## Auth Bootstrap

Run `00 Setup / 00.1 Create bearer token from username/password` first.

This request creates an explicit `Authorization: Basic ...` header from `teamcity_username` and `teamcity_password`, then creates a TeamCity bearer token through:

```text
POST /app/rest/users/current/tokens
```

The response contains `token.value` only once. The collection saves it into `teamcity_token` automatically.

`teamcity_password` and generated `teamcity_token` are intentionally empty in committed files and should not be committed.

If TeamCity returns `Authentication required`, check that:

- `teamcity_username` and `teamcity_password` are filled in `Current value`.
- The same credentials can log in at `/login.html`.
- The user has permission to create access tokens.

Optional variables:

- `base_url` defaults to `http://localhost:8111`.
- `repository_url` defaults to this GitHub repository.
- `limited_role_id` is needed only for the optional limited-user permissions folder.
