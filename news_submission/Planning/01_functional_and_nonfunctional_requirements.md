# Functional and Non-Functional Requirements

## Functional requirements

1. The system must support three roles: Reader, Editor, and Journalist.
2. The system must use a custom user model with role-specific behaviour.
3. Readers must be able to subscribe to publishers and journalists.
4. Journalists must be able to create articles and newsletters.
5. Editors must be able to review and approve article submissions.
6. Approved articles must be viewable by readers.
7. The API must return approved articles and reader-specific subscribed articles.
8. The system must authenticate API users with token-based authentication.
9. The system must enforce role-based authorisation for create, update, delete, and approve actions.
10. Once an article is approved, the system must email subscribers and POST to an internal REST endpoint.
11. The project must include automated unit tests for the API and approval workflow.

## Non-functional requirements

1. Code should be modular, readable, and PEP 8 compliant.
2. The application should use defensive validation and meaningful error handling.
3. The data model should be normalised to reduce duplication.
4. The application should be maintainable and logically separated into models, serializers, views, permissions, and services.
5. The API should be predictable and role-safe.
6. The database layer must support MariaDB.
7. The submission should include planning and diagram artefacts so the design is easy to assess.
