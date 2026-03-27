# Access Control Design

## Role summary

### Reader
- View approved articles
- View newsletters
- Use subscribed content API feed
- No create, update, delete, or approve permissions

### Journalist
- Create articles
- Create newsletters
- Update and delete own articles/newsletters
- Cannot approve articles

### Editor
- View all articles, including pending ones
- Update and delete articles and newsletters
- Approve articles

## Enforcement points
- Django groups and permissions are created after migration.
- API permissions check both authentication and role.
- Object-level permissions prevent journalists from editing other journalists' content.
- Template-based review pages are protected with an editor-only mixin.
- Internal approval logging requires a shared internal API key header.
