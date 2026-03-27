# Technical Research Notes

## Why use a custom user model?
A custom user model allows the system to store a role directly on the user and attach reader subscription relationships without using separate profile tables.

## Why use Django REST Framework token authentication?
Token authentication is simple, widely used in coursework, and suitable for machine-to-machine access for a third-party news client.

## Why use Django signals for approval?
Signals help keep the approval side effects separate from the core data model. Once an article changes to approved, the notification and internal API logging logic runs automatically.

## Why add an internal API key?
The brief asks for a POST to the app's own REST endpoint. An internal API key keeps that endpoint separate from public user tokens and makes the integration easier to secure and test.

## Why support SQLite and MariaDB?
SQLite is fast for development and automated testing. MariaDB support is included because the brief requires migration to MariaDB for the final project.
