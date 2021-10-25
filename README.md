# CSDT Django REST API

Taking the back end of the site, and converting it to a full fledged API for proper separation and optimization.

1. docker-compose up

2. Head to 127.0.0.1:8080/api/user/create/ and create a new test user

3. Head to 127.0.0.1:8080/api/user/token/ , login to account, and grab token

4. Download Chrome extension, ModHeader.

5. Add to profile (Authorization, Token WHATEVER_TOKEN_GETS_GENERATED)

Now, you will be authorized to access all endpoints. Otherwise, you would just be able to view some of them.
