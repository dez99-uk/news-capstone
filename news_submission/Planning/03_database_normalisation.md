# Database Design and Normalisation Notes

## Main entities
- User
- Publisher
- Article
- Newsletter
- ApprovedArticleLog

## Normalisation summary

### First Normal Form (1NF)
- Each model uses atomic fields.
- Repeating groups are represented with foreign keys or many-to-many relationships.

### Second Normal Form (2NF)
- Non-key attributes depend on the full primary key.
- Newsletter/article relationships are stored through a many-to-many relation instead of duplicated columns.

### Third Normal Form (3NF)
- Publisher information is stored once in `Publisher` and referenced by related records.
- Subscription relationships are stored as many-to-many fields instead of repeated text values.
- Approval log data is separated into `ApprovedArticleLog` rather than being embedded directly inside `Article`.

## Role modelling decision
- A role field is stored on the custom user.
- Django groups mirror the role value so permissions can be administered consistently.
